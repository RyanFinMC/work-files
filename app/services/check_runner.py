from datetime import datetime, timezone
from hashlib import sha256
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.alert_event import AlertEvent, AlertScope, AlertSeverity
from app.models.campaign import Campaign
from app.models.delivery_result import DeliveryResult, Placement, SourceProvider
from app.models.seed_account import SeedAccount, SeedStatus


def _placement_for_seed(campaign_id: UUID, seed: SeedAccount) -> Placement:
    digest = sha256(f"{campaign_id}:{seed.email}".encode("utf-8")).hexdigest()
    bucket = int(digest[:2], 16) % 100
    if bucket < 68:
        return Placement.inbox
    if bucket < 82:
        return Placement.promotions
    if bucket < 94:
        return Placement.spam
    return Placement.missing


def run_campaign_checks(db: Session, campaign: Campaign) -> dict[str, int]:
    active_seeds = db.execute(
        select(SeedAccount).where(SeedAccount.status == SeedStatus.active).order_by(SeedAccount.created_at.asc())
    ).scalars().all()

    existing_ids = set(
        db.execute(select(DeliveryResult.seed_account_id).where(DeliveryResult.campaign_id == campaign.id)).scalars().all()
    )

    created_count = 0
    skipped_count = 0
    now = datetime.now(timezone.utc)
    sent_at = campaign.sent_at
    if sent_at.tzinfo is None:
        sent_at = sent_at.replace(tzinfo=timezone.utc)

    for seed in active_seeds:
        if seed.id in existing_ids:
            skipped_count += 1
            continue

        placement = _placement_for_seed(campaign.id, seed)
        detected_at = None if placement == Placement.missing else now
        latency_ms = None
        if detected_at is not None:
            latency_ms = max(0, int((detected_at - sent_at).total_seconds() * 1000))

        result = DeliveryResult(
            campaign_id=campaign.id,
            seed_account_id=seed.id,
            placement=placement,
            detected_at=detected_at,
            latency_ms=latency_ms,
            source_provider=SourceProvider.imap,
            folder_or_label=placement.value,
            spf_result="pass" if placement != Placement.missing else None,
            dkim_result="pass" if placement in (Placement.inbox, Placement.promotions) else None,
            dmarc_result="pass" if placement != Placement.missing else None,
            raw_headers={
                "x-seed-check": "simulated",
                "x-campaign-id": str(campaign.id),
            },
        )
        db.add(result)
        created_count += 1

    db.flush()

    alerts_created = 0
    if created_count > 0:
        rows = db.execute(select(DeliveryResult.placement).where(DeliveryResult.campaign_id == campaign.id)).scalars().all()
        total = len(rows)
        inbox_count = sum(1 for placement in rows if placement == Placement.inbox)
        missing_count = sum(1 for placement in rows if placement == Placement.missing)
        inbox_rate = (inbox_count / total) if total else 0.0
        missing_rate = (missing_count / total) if total else 0.0

        if inbox_rate < 0.5:
            db.add(
                AlertEvent(
                    campaign_id=campaign.id,
                    scope=AlertScope.campaign,
                    severity=AlertSeverity.warning,
                    message=f"Inbox placement dropped below 50% ({inbox_rate:.1%})",
                )
            )
            alerts_created += 1

        if missing_rate > 0.2:
            db.add(
                AlertEvent(
                    campaign_id=campaign.id,
                    scope=AlertScope.campaign,
                    severity=AlertSeverity.critical,
                    message=f"Missing rate exceeded 20% ({missing_rate:.1%})",
                )
            )
            alerts_created += 1

    db.commit()
    return {
        "created_count": created_count,
        "skipped_count": skipped_count,
        "total_active_seeds": len(active_seeds),
        "alerts_created": alerts_created,
    }

"""Live FX feed engine with scheduled sync, fallback, and historical storage."""

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.fx_sources.registry import get_fx_feed_provider, list_fx_feed_providers
from app.models.fx import FxRateSource
from app.models.fx_sync import FxRateSnapshot, FxSyncRun
from app.models.enums import FxRateSourceType
from app.services.fx_engine import apply_markup, get_effective_fx_rate
from app.services.exchange_rate_engine import create_exchange_rate


DEFAULT_SYNC_PAIRS = [
    ("ZAR", "GHS"),
    ("ZAR", "ZWL"),
    ("ZAR", "ZMW"),
    ("ZAR", "KES"),
    ("ZAR", "NGN"),
    ("ZAR", "UGX"),
]


def sync_fx_from_feed(
    db: Session,
    *,
    source_code: str,
    pairs: list[tuple[str, str]] | None = None,
    config: dict | None = None,
    apply_manual_override: bool = True,
) -> FxSyncRun:
    pairs = pairs or DEFAULT_SYNC_PAIRS
    run = FxSyncRun(source_code=source_code, started_at=datetime.now(UTC))
    db.add(run)
    db.flush()

    try:
        provider = get_fx_feed_provider(source_code, config)
        synced = 0
        for from_ccy, to_ccy in pairs:
            feed_rate = provider.fetch_rate(from_ccy, to_ccy)
            if not feed_rate:
                continue

            effective = feed_rate.rate
            margin = None
            if apply_manual_override:
                effective = apply_markup(db, feed_rate.rate, from_currency=from_ccy, to_currency=to_ccy)
                margin = str(effective - feed_rate.rate)

            snapshot = FxRateSnapshot(
                source_code=source_code,
                from_currency=from_ccy,
                to_currency=to_ccy,
                base_rate=feed_rate.rate,
                effective_rate=effective,
                margin_applied=margin,
            )
            db.add(snapshot)

            from datetime import date as date_cls

            create_exchange_rate(
                db,
                from_currency=from_ccy,
                to_currency=to_ccy,
                rate=feed_rate.rate,
                effective_from=date_cls.today(),
                effective_to=None,
                created_by=None,
                change_reason=f"FX feed sync: {source_code}",
            )

            synced += 1

        run.success = synced > 0
        run.pairs_synced = synced
        run.completed_at = datetime.now(UTC)
    except Exception as exc:
        run.success = False
        run.error_message = str(exc)
        run.completed_at = datetime.now(UTC)

    db.flush()
    return run


def sync_all_active_sources(db: Session) -> list[FxSyncRun]:
    runs: list[FxSyncRun] = []
    sources = (
        db.query(FxRateSource)
        .filter(FxRateSource.is_active.is_(True), FxRateSource.source_type == FxRateSourceType.API)
        .order_by(FxRateSource.priority.desc())
        .all()
    )
    if not sources:
        for code in list_fx_feed_providers():
            runs.append(sync_fx_from_feed(db, source_code=code))
        return runs

    for src in sources:
        feed_code = (src.config or {}).get("feed_provider", src.code)
        if feed_code not in list_fx_feed_providers():
            continue
        runs.append(sync_fx_from_feed(db, source_code=feed_code, config=src.config))
    return runs


def get_fx_dashboard(db: Session) -> dict:
    latest_by_pair: dict[str, FxRateSnapshot] = {}
    snapshots = db.query(FxRateSnapshot).order_by(FxRateSnapshot.synced_at.desc()).limit(200).all()
    for snap in snapshots:
        key = f"{snap.from_currency}-{snap.to_currency}"
        if key not in latest_by_pair:
            latest_by_pair[key] = snap

    last_runs = db.query(FxSyncRun).order_by(FxSyncRun.started_at.desc()).limit(10).all()

    zar_ghs_rate, zar_ghs_meta = get_effective_fx_rate(db, from_currency="ZAR", to_currency="GHS")

    return {
        "current_rates": [
            {
                "pair": f"{s.from_currency}/{s.to_currency}",
                "base_rate": str(s.base_rate),
                "effective_rate": str(s.effective_rate) if s.effective_rate else None,
                "margin_applied": s.margin_applied,
                "source": s.source_code,
                "last_sync": s.synced_at.isoformat(),
            }
            for s in latest_by_pair.values()
        ],
        "zar_ghs_effective": str(zar_ghs_rate),
        "zar_ghs_metadata": zar_ghs_meta,
        "sync_history": [
            {
                "source": r.source_code,
                "success": r.success,
                "pairs_synced": r.pairs_synced,
                "error": r.error_message,
                "started_at": r.started_at.isoformat(),
                "completed_at": r.completed_at.isoformat() if r.completed_at else None,
            }
            for r in last_runs
        ],
        "available_feed_providers": list_fx_feed_providers(),
    }

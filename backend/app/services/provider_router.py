"""Configuration-driven provider orchestration router."""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.corridor import Corridor, CorridorProviderRoute
from app.models.enums import CorridorStatus
from app.providers.orchestration.adapters import create_orchestration_provider
from app.providers.orchestration.interface import (
    OrchestrationProvider,
    OrchestrationQuote,
    OrchestrationQuoteRequest,
    OrchestrationReconcileResult,
    OrchestrationStatusResult,
    OrchestrationTransferRequest,
    OrchestrationTransferResult,
)
from app.services.operations_audit import log_operations_action
from app.models.enums import OperationsAuditCategory


SUPPORTED_ORCHESTRATION_PROVIDERS = frozenset({
    "mock_mukuru",
    "live_mukuru",
    "manual_mukuru",
    "mukuru_api",
    "flutterwave",
    "veengu",
    "onafriq",
    "easy_pay",
    "pay_at",
})


def _rank_routes(routes: list[CorridorProviderRoute]) -> list[CorridorProviderRoute]:
    return sorted(
        [r for r in routes if r.is_available and r.provider_code in SUPPORTED_ORCHESTRATION_PROVIDERS],
        key=lambda r: (-r.priority, r.cost_score),
    )


def resolve_corridor(
    db: Session,
    *,
    source_country: str,
    destination_country: str,
) -> Corridor | None:
    return (
        db.query(Corridor)
        .filter(
            Corridor.source_country == source_country,
            Corridor.destination_country == destination_country,
            Corridor.status == CorridorStatus.ACTIVE,
        )
        .order_by(Corridor.priority.desc())
        .first()
    )


def select_provider(
    db: Session,
    *,
    source_country: str,
    destination_country: str,
    preferred_provider: str | None = None,
) -> tuple[str, Corridor | None]:
    corridor = resolve_corridor(db, source_country=source_country, destination_country=destination_country)
    if not corridor:
        fallback = preferred_provider or "mock_mukuru"
        return fallback, None

    if preferred_provider and preferred_provider in SUPPORTED_ORCHESTRATION_PROVIDERS:
        return preferred_provider, corridor

    routes = _rank_routes(
        db.query(CorridorProviderRoute).filter(CorridorProviderRoute.corridor_id == corridor.id).all()
    )
    if routes:
        return routes[0].provider_code, corridor

    return corridor.provider_code, corridor


def get_orchestration_provider(db: Session, provider_code: str) -> OrchestrationProvider:
    if provider_code not in SUPPORTED_ORCHESTRATION_PROVIDERS:
        raise ValueError(f"Unsupported orchestration provider: {provider_code}")
    return create_orchestration_provider(provider_code)


def quote_transfer(
    db: Session,
    request: OrchestrationQuoteRequest,
    *,
    preferred_provider: str | None = None,
    user_id: int | None = None,
) -> OrchestrationQuote:
    provider_code, corridor = select_provider(
        db,
        source_country=request.source_country,
        destination_country=request.destination_country,
        preferred_provider=preferred_provider,
    )
    metadata = dict(request.metadata)
    if corridor:
        metadata.setdefault("corridor_code", corridor.code)
        metadata.setdefault("receive_currency", corridor.destination_currency)

    enriched = OrchestrationQuoteRequest(
        source_country=request.source_country,
        destination_country=request.destination_country,
        send_amount=request.send_amount,
        send_currency=request.send_currency,
        receive_currency=metadata.get("receive_currency", request.receive_currency),
        beneficiary_type=request.beneficiary_type,
        metadata=metadata,
    )
    provider = get_orchestration_provider(db, provider_code)
    quote = provider.quote(enriched)
    if user_id is not None:
        log_operations_action(
            db,
            category=OperationsAuditCategory.PROVIDER,
            action="provider_quote",
            entity_type="transfer_quote",
            entity_id=None,
            user_id=user_id,
            details={"provider": provider_code, "corridor": corridor.code if corridor else None},
        )
    return quote


def route_create_transfer(
    db: Session,
    request: OrchestrationTransferRequest,
    *,
    preferred_provider: str | None = None,
    user_id: int | None = None,
) -> OrchestrationTransferResult:
    provider_code, corridor = select_provider(
        db,
        source_country=request.source_country,
        destination_country=request.destination_country,
        preferred_provider=preferred_provider,
    )
    provider = get_orchestration_provider(db, provider_code)
    result = provider.create_transfer(request)
    log_operations_action(
        db,
        category=OperationsAuditCategory.PROVIDER,
        action="provider_transfer_created",
        entity_type="transfer",
        entity_id=request.transfer_id,
        user_id=user_id,
        details={"provider": provider_code, "success": result.success, "corridor": corridor.code if corridor else None},
    )
    return result


def route_get_status(db: Session, provider_code: str, reference: str) -> OrchestrationStatusResult:
    provider = get_orchestration_provider(db, provider_code)
    return provider.get_status(reference)


def route_cancel_transfer(db: Session, provider_code: str, reference: str) -> OrchestrationTransferResult:
    provider = get_orchestration_provider(db, provider_code)
    return provider.cancel_transfer(reference)


def route_reconcile(
    db: Session, provider_code: str, reference: str, provider_data: dict
) -> OrchestrationReconcileResult:
    provider = get_orchestration_provider(db, provider_code)
    return provider.reconcile(reference, provider_data)


def list_available_providers() -> list[str]:
    return sorted(SUPPORTED_ORCHESTRATION_PROVIDERS)

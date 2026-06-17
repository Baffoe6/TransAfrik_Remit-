"""Background scheduler for transfer maintenance jobs."""

import asyncio
import logging

from app.database import SessionLocal
from app.services.transfer_cancellation_service import JOB_INTERVAL_MINUTES, cancel_expired_unpaid_transfers

logger = logging.getLogger(__name__)


async def run_transfer_maintenance_scheduler() -> None:
    """Run cancel_expired_unpaid_transfers every 15 minutes."""
    interval_seconds = JOB_INTERVAL_MINUTES * 60
    while True:
        try:
            db = SessionLocal()
            try:
                count = cancel_expired_unpaid_transfers(db)
                if count:
                    logger.info("Auto-cancelled %s expired unpaid transfer(s)", count)
                db.commit()
            except Exception:
                db.rollback()
                logger.exception("cancel_expired_unpaid_transfers job failed")
            finally:
                db.close()
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Transfer maintenance scheduler error")
        await asyncio.sleep(interval_seconds)


def run_cancel_expired_unpaid_transfers_once() -> int:
    """Synchronous entry point for tests and manual invocation."""
    db = SessionLocal()
    try:
        count = cancel_expired_unpaid_transfers(db)
        db.commit()
        return count
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

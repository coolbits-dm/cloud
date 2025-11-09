# Ledger implementation for cbT economy
import logging
from typing import Dict, Any, Optional
from decimal import Decimal
from datetime import datetime
import uuid
from .db import LedgerEntry, get_db_session

logger = logging.getLogger(__name__)

def debit_cbt(
    ref: str,
    amount: float,
    reason: str,
    meta: Optional[Dict[str, Any]] = None
) -> str:
    """Debit cbT tokens"""
    
    db = get_db_session()
    try:
        entry = LedgerEntry(
            ref=ref,
            delta=Decimal(-abs(amount)),  # Ensure negative
            reason=reason,
            meta=meta or {}
        )
        db.add(entry)
        db.commit()
        
        logger.info(f"Debited {amount} cbT for {ref}: {reason}")
        return str(entry.id)
        
    except Exception as e:
        logger.error(f"Failed to debit cbT: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def credit_cbt(
    ref: str,
    amount: float,
    reason: str,
    meta: Optional[Dict[str, Any]] = None
) -> str:
    """Credit cbT tokens"""
    
    db = get_db_session()
    try:
        entry = LedgerEntry(
            ref=ref,
            delta=Decimal(abs(amount)),  # Ensure positive
            reason=reason,
            meta=meta or {}
        )
        db.add(entry)
        db.commit()
        
        logger.info(f"Credited {amount} cbT for {ref}: {reason}")
        return str(entry.id)
        
    except Exception as e:
        logger.error(f"Failed to credit cbT: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def get_balance(ref: str) -> float:
    """Get cbT balance for reference"""
    
    db = get_db_session()
    try:
        from sqlalchemy import func
        
        result = db.query(func.sum(LedgerEntry.delta)).filter(
            LedgerEntry.ref == ref
        ).scalar()
        
        return float(result or 0)
        
    except Exception as e:
        logger.error(f"Failed to get balance for {ref}: {e}")
        return 0.0
    finally:
        db.close()

def get_ledger_history(ref: str, limit: int = 50) -> list:
    """Get ledger history for reference"""
    
    db = get_db_session()
    try:
        entries = db.query(LedgerEntry).filter(
            LedgerEntry.ref == ref
        ).order_by(LedgerEntry.ts.desc()).limit(limit).all()
        
        return [
            {
                "id": str(entry.id),
                "ts": entry.ts.isoformat(),
                "delta": float(entry.delta),
                "reason": entry.reason,
                "meta": entry.meta
            }
            for entry in entries
        ]
        
    except Exception as e:
        logger.error(f"Failed to get ledger history for {ref}: {e}")
        return []
    finally:
        db.close()

def get_session_delta(session_id: str) -> float:
    """Get cbT delta for session"""
    return get_balance(session_id)

# Tariff configuration
CB_TARIFF = {
    "WALL_POST": -1,
    "NHA_INVOCATION": -2,
    "BOARD_MEETING": -3,
    "BITS_DRY_RUN": -1
}

def apply_tariff(action: str, ref: str, meta: Optional[Dict[str, Any]] = None) -> str:
    """Apply tariff for action"""
    
    cost = CB_TARIFF.get(action, 0)
    if cost == 0:
        logger.warning(f"No tariff defined for action {action}")
        return ""
    
    reason = f"Tariff for {action}"
    return debit_cbt(ref, abs(cost), reason, meta)

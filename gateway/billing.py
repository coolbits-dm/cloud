# Billing and Usage module for M20.2
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from fastapi import HTTPException

logger = logging.getLogger(__name__)

# Environment variables
CB_BILLING_MODE = os.getenv("CB_BILLING_MODE", "dev")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
BIGQUERY_PROJECT_ID = os.getenv("BIGQUERY_PROJECT_ID", "")
BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET", "coolbits_usage")

# Default quotas per organization
DEFAULT_QUOTAS = {
    "soft_limit": 1000,  # cbT
    "hard_limit": 2000,  # cbT
    "monthly_limit": 5000,  # cbT
    "nha_invocations": 1000,
    "rag_queries": 5000,
    "flow_runs": 100
}

class BillingManager:
    """Billing and usage manager for M20.2"""
    
    def __init__(self, db: Session):
        self.db = db
        self.stripe_enabled = bool(STRIPE_SECRET_KEY and CB_BILLING_MODE == "prod")
    
    def get_org_balance(self, org_id: str) -> Dict[str, Any]:
        """Get organization cbT balance and usage"""
        from .db import LedgerEntry, Organization
        
        # Get current balance
        balance_query = self.db.query(func.sum(LedgerEntry.delta)).filter(
            LedgerEntry.org_id == org_id
        )
        current_balance = balance_query.scalar() or 0
        
        # Get organization quotas
        org = self.db.query(Organization).filter(Organization.id == org_id).first()
        quotas = org.settings.get("quotas", DEFAULT_QUOTAS) if org else DEFAULT_QUOTAS
        
        # Get monthly usage
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_usage = self.db.query(func.sum(LedgerEntry.delta)).filter(
            and_(
                LedgerEntry.org_id == org_id,
                LedgerEntry.created_at >= month_start,
                LedgerEntry.delta < 0  # Only negative (usage) entries
            )
        ).scalar() or 0
        
        # Calculate usage percentages
        soft_percent = abs(monthly_usage) / quotas["soft_limit"] * 100
        hard_percent = abs(monthly_usage) / quotas["hard_limit"] * 100
        
        return {
            "org_id": org_id,
            "current_balance": float(current_balance),
            "monthly_usage": abs(float(monthly_usage)),
            "quotas": quotas,
            "soft_limit_percent": min(soft_percent, 100),
            "hard_limit_percent": min(hard_percent, 100),
            "status": self._get_quota_status(monthly_usage, quotas),
            "billing_mode": CB_BILLING_MODE
        }
    
    def _get_quota_status(self, monthly_usage: float, quotas: Dict[str, Any]) -> str:
        """Get quota status based on usage"""
        abs_usage = abs(monthly_usage)
        
        if abs_usage >= quotas["hard_limit"]:
            return "hard_limit_exceeded"
        elif abs_usage >= quotas["soft_limit"]:
            return "soft_limit_exceeded"
        elif abs_usage >= quotas["soft_limit"] * 0.8:
            return "approaching_limit"
        else:
            return "healthy"
    
    def debit_cbt(self, org_id: str, amount: float, reason: str, 
                  ref_id: Optional[str] = None, metadata: Optional[Dict] = None) -> bool:
        """Debit cbT from organization balance with quota enforcement"""
        from .db import LedgerEntry
        
        # Check quotas before debiting
        balance_info = self.get_org_balance(org_id)
        
        # Hard stop at hard limit
        if balance_info["status"] == "hard_limit_exceeded":
            logger.warning(f"Hard limit exceeded for org {org_id}, blocking debit")
            raise HTTPException(status_code=402, detail="quota_exceeded")
        
        # Soft warning at soft limit
        if balance_info["status"] == "soft_limit_exceeded":
            logger.warning(f"Soft limit exceeded for org {org_id}, allowing with warning")
        
        # Create ledger entry
        entry = LedgerEntry(
            org_id=org_id,
            delta=-abs(amount),  # Negative for debits
            reason=reason,
            ref_id=ref_id,
            metadata=metadata or {}
        )
        
        self.db.add(entry)
        self.db.commit()
        
        logger.info(f"Debited {amount} cbT from org {org_id} for {reason}")
        return True
    
    def credit_cbt(self, org_id: str, amount: float, reason: str,
                   ref_id: Optional[str] = None, metadata: Optional[Dict] = None) -> bool:
        """Credit cbT to organization balance"""
        from .db import LedgerEntry
        
        # Create ledger entry
        entry = LedgerEntry(
            org_id=org_id,
            delta=abs(amount),  # Positive for credits
            reason=reason,
            ref_id=ref_id,
            metadata=metadata or {}
        )
        
        self.db.add(entry)
        self.db.commit()
        
        logger.info(f"Credited {amount} cbT to org {org_id} for {reason}")
        return True
    
    def get_usage_stats(self, org_id: str, days: int = 30) -> Dict[str, Any]:
        """Get usage statistics for organization"""
        from .db import LedgerEntry, Invocation
        
        since = datetime.utcnow() - timedelta(days=days)
        
        # Get ledger entries
        ledger_entries = self.db.query(LedgerEntry).filter(
            and_(
                LedgerEntry.org_id == org_id,
                LedgerEntry.created_at >= since
            )
        ).order_by(desc(LedgerEntry.created_at)).all()
        
        # Get NHA invocations
        nha_invocations = self.db.query(Invocation).filter(
            and_(
                Invocation.org_id == org_id,
                Invocation.created_at >= since
            )
        ).all()
        
        # Calculate stats
        total_debits = sum(abs(entry.delta) for entry in ledger_entries if entry.delta < 0)
        total_credits = sum(entry.delta for entry in ledger_entries if entry.delta > 0)
        
        # Group by reason
        usage_by_reason = {}
        for entry in ledger_entries:
            if entry.delta < 0:  # Only debits
                reason = entry.reason
                usage_by_reason[reason] = usage_by_reason.get(reason, 0) + abs(entry.delta)
        
        return {
            "period_days": days,
            "total_debits": float(total_debits),
            "total_credits": float(total_credits),
            "net_usage": float(total_debits - total_credits),
            "usage_by_reason": usage_by_reason,
            "nha_invocations": len(nha_invocations),
            "entries_count": len(ledger_entries)
        }
    
    def export_to_bigquery(self, org_id: str, start_date: datetime, end_date: datetime) -> bool:
        """Export usage data to BigQuery (placeholder for M20.2)"""
        if not BIGQUERY_PROJECT_ID or CB_BILLING_MODE != "prod":
            logger.info(f"BigQuery export skipped for org {org_id} (dev mode)")
            return True
        
        # TODO: Implement BigQuery export in M20.4
        logger.info(f"BigQuery export placeholder for org {org_id}")
        return True
    
    def create_stripe_customer(self, org_id: str, email: str, name: str) -> Optional[str]:
        """Create Stripe customer for organization"""
        if not self.stripe_enabled:
            logger.info(f"Stripe customer creation skipped (dev mode)")
            return None
        
        try:
            import stripe
            stripe.api_key = STRIPE_SECRET_KEY
            
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={
                    "org_id": org_id,
                    "billing_mode": CB_BILLING_MODE
                }
            )
            
            logger.info(f"Created Stripe customer {customer.id} for org {org_id}")
            return customer.id
            
        except Exception as e:
            logger.error(f"Failed to create Stripe customer: {e}")
            return None
    
    def create_payment_intent(self, org_id: str, amount_cents: int, 
                             description: str) -> Optional[Dict[str, Any]]:
        """Create Stripe payment intent"""
        if not self.stripe_enabled:
            logger.info(f"Stripe payment intent creation skipped (dev mode)")
            return {
                "id": f"pi_dev_{org_id}_{int(datetime.utcnow().timestamp())}",
                "client_secret": "pi_dev_secret",
                "status": "succeeded",
                "amount": amount_cents
            }
        
        try:
            import stripe
            stripe.api_key = STRIPE_SECRET_KEY
            
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency="usd",
                description=description,
                metadata={
                    "org_id": org_id,
                    "billing_mode": CB_BILLING_MODE
                }
            )
            
            return {
                "id": intent.id,
                "client_secret": intent.client_secret,
                "status": intent.status,
                "amount": amount_cents
            }
            
        except Exception as e:
            logger.error(f"Failed to create payment intent: {e}")
            return None

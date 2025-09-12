# Audit and Privacy module for M20.3
import os
import json
import logging
import hmac
import hashlib
import uuid
import zipfile
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc, or_
from fastapi import HTTPException, Request

logger = logging.getLogger(__name__)

# Environment variables
AUDIT_RETENTION_DAYS = int(os.getenv("AUDIT_RETENTION_DAYS", "365"))
PRIVACY_EXPORT_RETENTION_HOURS = int(os.getenv("PRIVACY_EXPORT_RETENTION_HOURS", "24"))
PRIVACY_TOMBSTONE_DAYS = int(os.getenv("PRIVACY_TOMBSTONE_DAYS", "30"))

class AuditManager:
    """Audit logging manager for M20.3"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_event(self, org_id: str, actor_type: str, actor_id: str, 
                  action: str, target_type: str, target_id: str,
                  before: Optional[Dict] = None, after: Optional[Dict] = None,
                  ip: Optional[str] = None, ua: Optional[str] = None,
                  trace_id: Optional[str] = None) -> str:
        """Log audit event"""
        from .db import AuditEvent
        
        event_id = str(uuid.uuid4())
        
        event = AuditEvent(
            id=event_id,
            org_id=org_id,
            actor_type=actor_type,
            actor_id=actor_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            before=before,
            after=after,
            ip=ip,
            user_agent=ua,
            trace_id=trace_id,
            created_at=datetime.utcnow()
        )
        
        self.db.add(event)
        self.db.commit()
        
        logger.info(f"Audit event logged: {action} on {target_type} by {actor_type}:{actor_id}")
        return event_id
    
    def get_audit_events(self, org_id: str, query: Optional[str] = None,
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None,
                        limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit events for organization"""
        from .db import AuditEvent
        
        query_obj = self.db.query(AuditEvent).filter(AuditEvent.org_id == org_id)
        
        if query:
            query_obj = query_obj.filter(
                or_(
                    AuditEvent.action.ilike(f"%{query}%"),
                    AuditEvent.target_type.ilike(f"%{query}%"),
                    AuditEvent.actor_id.ilike(f"%{query}%")
                )
            )
        
        if start_date:
            query_obj = query_obj.filter(AuditEvent.created_at >= start_date)
        
        if end_date:
            query_obj = query_obj.filter(AuditEvent.created_at <= end_date)
        
        events = query_obj.order_by(desc(AuditEvent.created_at)).limit(limit).all()
        
        result = []
        for event in events:
            result.append({
                "id": event.id,
                "org_id": event.org_id,
                "actor_type": event.actor_type,
                "actor_id": event.actor_id,
                "action": event.action,
                "target_type": event.target_type,
                "target_id": event.target_id,
                "before": event.before,
                "after": event.after,
                "ip": event.ip,
                "user_agent": event.user_agent,
                "trace_id": event.trace_id,
                "created_at": event.created_at.isoformat()
            })
        
        return result
    
    def get_events_by_trace(self, trace_id: str) -> List[Dict[str, Any]]:
        """Get all events for a trace ID"""
        from .db import AuditEvent
        
        events = self.db.query(AuditEvent).filter(
            AuditEvent.trace_id == trace_id
        ).order_by(AuditEvent.created_at).all()
        
        result = []
        for event in events:
            result.append({
                "id": event.id,
                "org_id": event.org_id,
                "actor_type": event.actor_type,
                "actor_id": event.actor_id,
                "action": event.action,
                "target_type": event.target_type,
                "target_id": event.target_id,
                "before": event.before,
                "after": event.after,
                "ip": event.ip,
                "user_agent": event.user_agent,
                "trace_id": event.trace_id,
                "created_at": event.created_at.isoformat()
            })
        
        return result

class PrivacyManager:
    """Privacy and data protection manager for M20.3"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def request_export(self, org_id: str, user_id: Optional[str] = None) -> str:
        """Request data export (DSAR)"""
        from .db import PrivacyJob
        
        job_id = str(uuid.uuid4())
        
        job = PrivacyJob(
            id=job_id,
            org_id=org_id,
            user_id=user_id,
            job_type="export",
            status="pending",
            metadata={
                "requested_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(hours=PRIVACY_EXPORT_RETENTION_HOURS)).isoformat()
            },
            created_at=datetime.utcnow()
        )
        
        self.db.add(job)
        self.db.commit()
        
        logger.info(f"Privacy export job created: {job_id} for org {org_id}")
        return job_id
    
    def request_deletion(self, user_id: str) -> str:
        """Request account deletion"""
        from .db import PrivacyJob
        
        job_id = str(uuid.uuid4())
        
        job = PrivacyJob(
            id=job_id,
            org_id=None,  # User-level deletion
            user_id=user_id,
            job_type="deletion",
            status="pending",
            metadata={
                "requested_at": datetime.utcnow().isoformat(),
                "tombstone_until": (datetime.utcnow() + timedelta(days=PRIVACY_TOMBSTONE_DAYS)).isoformat()
            },
            created_at=datetime.utcnow()
        )
        
        self.db.add(job)
        self.db.commit()
        
        logger.info(f"Privacy deletion job created: {job_id} for user {user_id}")
        return job_id
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get privacy job status"""
        from .db import PrivacyJob
        
        job = self.db.query(PrivacyJob).filter(PrivacyJob.id == job_id).first()
        
        if not job:
            return None
        
        return {
            "id": job.id,
            "org_id": job.org_id,
            "user_id": job.user_id,
            "job_type": job.job_type,
            "status": job.status,
            "metadata": job.metadata,
            "created_at": job.created_at.isoformat(),
            "completed_at": job.completed_at.isoformat() if job.completed_at else None
        }
    
    def process_export_job(self, job_id: str) -> Optional[str]:
        """Process export job and return download URL"""
        from .db import PrivacyJob
        
        job = self.db.query(PrivacyJob).filter(PrivacyJob.id == job_id).first()
        
        if not job or job.job_type != "export":
            return None
        
        try:
            # Create export data
            export_data = self._collect_export_data(job.org_id, job.user_id)
            
            # Create ZIP file
            export_path = f"artifacts/exports/{job.org_id}/{job_id}.zip"
            os.makedirs(os.path.dirname(export_path), exist_ok=True)
            
            with zipfile.ZipFile(export_path, 'w') as zipf:
                zipf.writestr("export_data.json", json.dumps(export_data, indent=2))
            
            # Update job status
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            job.metadata["export_path"] = export_path
            job.metadata["file_size"] = os.path.getsize(export_path)
            
            self.db.commit()
            
            # Generate signed URL (placeholder for M20.3)
            download_url = f"/v1/privacy/download/{job_id}"
            
            logger.info(f"Export job completed: {job_id}")
            return download_url
            
        except Exception as e:
            logger.error(f"Export job failed: {e}")
            job.status = "failed"
            job.metadata["error"] = str(e)
            self.db.commit()
            return None
    
    def process_deletion_job(self, job_id: str) -> bool:
        """Process deletion job"""
        from .db import PrivacyJob
        
        job = self.db.query(PrivacyJob).filter(PrivacyJob.id == job_id).first()
        
        if not job or job.job_type != "deletion":
            return False
        
        try:
            # Soft delete user data
            self._soft_delete_user_data(job.user_id)
            
            # Update job status
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"Deletion job completed: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Deletion job failed: {e}")
            job.status = "failed"
            job.metadata["error"] = str(e)
            self.db.commit()
            return False
    
    def _collect_export_data(self, org_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Collect data for export"""
        from .db import Post, Comment, Invocation, LedgerEntry, AuditEvent
        
        export_data = {
            "export_info": {
                "org_id": org_id,
                "user_id": user_id,
                "exported_at": datetime.utcnow().isoformat(),
                "retention_hours": PRIVACY_EXPORT_RETENTION_HOURS
            },
            "posts": [],
            "comments": [],
            "invocations": [],
            "ledger_entries": [],
            "audit_events": []
        }
        
        # Collect posts
        posts_query = self.db.query(Post).filter(Post.org_id == org_id)
        if user_id:
            posts_query = posts_query.filter(Post.author == user_id)
        
        for post in posts_query.all():
            export_data["posts"].append({
                "id": post.id,
                "panel": post.panel,
                "author": post.author,
                "text": post.text,
                "created_at": post.created_at.isoformat()
            })
        
        # Collect comments
        comments_query = self.db.query(Comment).join(Post).filter(Post.org_id == org_id)
        if user_id:
            comments_query = comments_query.filter(Comment.author == user_id)
        
        for comment in comments_query.all():
            export_data["comments"].append({
                "id": comment.id,
                "post_id": comment.post_id,
                "author": comment.author,
                "text": comment.text,
                "created_at": comment.created_at.isoformat()
            })
        
        # Collect invocations
        invocations_query = self.db.query(Invocation).filter(Invocation.org_id == org_id)
        if user_id:
            invocations_query = invocations_query.filter(Invocation.post.has(Post.author == user_id))
        
        for invocation in invocations_query.all():
            export_data["invocations"].append({
                "id": invocation.id,
                "post_id": invocation.post_id,
                "agent": invocation.agent,
                "role": invocation.role,
                "status": invocation.status,
                "created_at": invocation.created_at.isoformat()
            })
        
        # Collect ledger entries
        ledger_query = self.db.query(LedgerEntry).filter(LedgerEntry.org_id == org_id)
        
        for entry in ledger_query.all():
            export_data["ledger_entries"].append({
                "id": entry.id,
                "delta": float(entry.delta),
                "reason": entry.reason,
                "ref_id": entry.ref_id,
                "metadata": entry.metadata,
                "created_at": entry.created_at.isoformat()
            })
        
        # Collect audit events
        audit_query = self.db.query(AuditEvent).filter(AuditEvent.org_id == org_id)
        
        for event in audit_query.all():
            export_data["audit_events"].append({
                "id": event.id,
                "actor_type": event.actor_type,
                "actor_id": event.actor_id,
                "action": event.action,
                "target_type": event.target_type,
                "target_id": event.target_id,
                "created_at": event.created_at.isoformat()
            })
        
        return export_data
    
    def _soft_delete_user_data(self, user_id: str):
        """Soft delete user data"""
        from .db import Post, Comment, Invocation
        
        # Mark posts as soft deleted
        self.db.query(Post).filter(Post.author == user_id).update({
            "text": "*** DELETED ***",
            "metadata": {"soft_deleted": True, "deleted_at": datetime.utcnow().isoformat()}
        })
        
        # Mark comments as soft deleted
        self.db.query(Comment).filter(Comment.author == user_id).update({
            "text": "*** DELETED ***",
            "metadata": {"soft_deleted": True, "deleted_at": datetime.utcnow().isoformat()}
        })
        
        self.db.commit()

def verify_hmac(request: Request, secret: str) -> bool:
    """Verify HMAC signature"""
    signature = request.headers.get("x-cb-signature", "")
    if not signature:
        return False
    
    body = request.body()
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    
    return hmac.compare_digest(signature, expected)

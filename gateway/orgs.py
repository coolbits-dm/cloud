# Organizations and RBAC module for M20.1
import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

logger = logging.getLogger(__name__)

# Environment variables
INVITE_EXPIRY_HOURS = int(os.getenv("INVITE_EXPIRY_HOURS", "168"))  # 7 days
MAX_ORG_MEMBERS = int(os.getenv("MAX_ORG_MEMBERS", "100"))

class OrgManager:
    """Organization and RBAC manager"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_org(self, name: str, owner_id: str, owner_email: str) -> Dict[str, Any]:
        """Create new organization"""
        from .db import Organization, OrgUser
        
        # Create organization
        org = Organization(
            name=name,
            slug=self._generate_slug(name),
            created_by=owner_id,
            settings={
                "max_members": MAX_ORG_MEMBERS,
                "features": ["nha", "rag", "orchestrator"],
                "billing_mode": "dev"
            }
        )
        self.db.add(org)
        self.db.flush()  # Get the ID
        
        # Add owner as admin
        org_user = OrgUser(
            org_id=org.id,
            user_id=owner_id,
            email=owner_email,
            role="admin",
            status="active",
            invited_by=owner_id,
            joined_at=datetime.utcnow()
        )
        self.db.add(org_user)
        self.db.commit()
        
        logger.info(f"Created organization {org.name} with owner {owner_email}")
        
        return {
            "id": org.id,
            "name": org.name,
            "slug": org.slug,
            "created_at": org.created_at.isoformat(),
            "owner_id": owner_id,
            "member_count": 1
        }
    
    def get_org(self, org_id: str) -> Optional[Dict[str, Any]]:
        """Get organization by ID"""
        from .db import Organization, OrgUser
        
        org = self.db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            return None
        
        # Get member count
        member_count = self.db.query(OrgUser).filter(
            OrgUser.org_id == org_id,
            OrgUser.status == "active"
        ).count()
        
        return {
            "id": org.id,
            "name": org.name,
            "slug": org.slug,
            "created_at": org.created_at.isoformat(),
            "settings": org.settings,
            "member_count": member_count
        }
    
    def get_user_orgs(self, user_id: str) -> List[Dict[str, Any]]:
        """Get organizations for user"""
        from .db import Organization, OrgUser
        
        orgs = self.db.query(Organization).join(OrgUser).filter(
            OrgUser.user_id == user_id,
            OrgUser.status == "active"
        ).all()
        
        result = []
        for org in orgs:
            # Get user's role in this org
            org_user = self.db.query(OrgUser).filter(
                OrgUser.org_id == org.id,
                OrgUser.user_id == user_id
            ).first()
            
            result.append({
                "id": org.id,
                "name": org.name,
                "slug": org.slug,
                "role": org_user.role,
                "joined_at": org_user.joined_at.isoformat(),
                "settings": org.settings
            })
        
        return result
    
    def invite_user(self, org_id: str, email: str, role: str, invited_by: str) -> Dict[str, Any]:
        """Invite user to organization"""
        from .db import OrgUser, OrgInvite
        
        # Check if user is already a member
        existing_member = self.db.query(OrgUser).filter(
            OrgUser.org_id == org_id,
            OrgUser.email == email
        ).first()
        
        if existing_member:
            if existing_member.status == "active":
                raise ValueError("User is already a member of this organization")
            elif existing_member.status == "pending":
                raise ValueError("User already has a pending invitation")
        
        # Check org member limit
        current_members = self.db.query(OrgUser).filter(
            OrgUser.org_id == org_id,
            OrgUser.status == "active"
        ).count()
        
        org = self.db.query(Organization).filter(Organization.id == org_id).first()
        max_members = org.settings.get("max_members", MAX_ORG_MEMBERS)
        
        if current_members >= max_members:
            raise ValueError("Organization member limit reached")
        
        # Create invitation
        invite_token = secrets.token_urlsafe(32)
        invite = OrgInvite(
            org_id=org_id,
            email=email,
            role=role,
            token=invite_token,
            invited_by=invited_by,
            expires_at=datetime.utcnow() + timedelta(hours=INVITE_EXPIRY_HOURS)
        )
        self.db.add(invite)
        self.db.commit()
        
        logger.info(f"Created invitation for {email} to org {org_id}")
        
        return {
            "id": invite.id,
            "email": email,
            "role": role,
            "token": invite_token,
            "expires_at": invite.expires_at.isoformat(),
            "invited_by": invited_by
        }
    
    def accept_invite(self, token: str, user_id: str) -> Dict[str, Any]:
        """Accept organization invitation"""
        from .db import OrgInvite, OrgUser
        
        # Find invitation
        invite = self.db.query(OrgInvite).filter(
            OrgInvite.token == token,
            OrgInvite.status == "pending"
        ).first()
        
        if not invite:
            raise ValueError("Invalid or expired invitation")
        
        if invite.expires_at < datetime.utcnow():
            invite.status = "expired"
            self.db.commit()
            raise ValueError("Invitation expired")
        
        # Check if user is already a member
        existing_member = self.db.query(OrgUser).filter(
            OrgUser.org_id == invite.org_id,
            OrgUser.user_id == user_id
        ).first()
        
        if existing_member:
            if existing_member.status == "active":
                raise ValueError("User is already a member of this organization")
            elif existing_member.status == "pending":
                # Update existing pending membership
                existing_member.role = invite.role
                existing_member.status = "active"
                existing_member.joined_at = datetime.utcnow()
            else:
                # Reactivate membership
                existing_member.role = invite.role
                existing_member.status = "active"
                existing_member.joined_at = datetime.utcnow()
        else:
            # Create new membership
            org_user = OrgUser(
                org_id=invite.org_id,
                user_id=user_id,
                email=invite.email,
                role=invite.role,
                status="active",
                invited_by=invite.invited_by,
                joined_at=datetime.utcnow()
            )
            self.db.add(org_user)
        
        # Mark invitation as accepted
        invite.status = "accepted"
        invite.accepted_at = datetime.utcnow()
        self.db.commit()
        
        logger.info(f"User {user_id} accepted invitation to org {invite.org_id}")
        
        return {
            "org_id": invite.org_id,
            "role": invite.role,
            "joined_at": datetime.utcnow().isoformat()
        }
    
    def get_org_members(self, org_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Get organization members (admin only)"""
        from .db import OrgUser
        
        # Check if user is admin
        if not self._is_admin(org_id, user_id):
            raise ValueError("Admin access required")
        
        members = self.db.query(OrgUser).filter(
            OrgUser.org_id == org_id,
            OrgUser.status == "active"
        ).all()
        
        result = []
        for member in members:
            result.append({
                "id": member.id,
                "user_id": member.user_id,
                "email": member.email,
                "role": member.role,
                "status": member.status,
                "joined_at": member.joined_at.isoformat(),
                "invited_by": member.invited_by
            })
        
        return result
    
    def update_member_role(self, org_id: str, member_id: str, new_role: str, updated_by: str) -> bool:
        """Update member role (admin only)"""
        from .db import OrgUser
        
        # Check if updater is admin
        if not self._is_admin(org_id, updated_by):
            raise ValueError("Admin access required")
        
        # Check if member exists
        member = self.db.query(OrgUser).filter(
            OrgUser.id == member_id,
            OrgUser.org_id == org_id
        ).first()
        
        if not member:
            raise ValueError("Member not found")
        
        # Prevent demoting the last admin
        if member.role == "admin" and new_role != "admin":
            admin_count = self.db.query(OrgUser).filter(
                OrgUser.org_id == org_id,
                OrgUser.role == "admin",
                OrgUser.status == "active"
            ).count()
            
            if admin_count <= 1:
                raise ValueError("Cannot demote the last admin")
        
        member.role = new_role
        member.updated_at = datetime.utcnow()
        self.db.commit()
        
        logger.info(f"Updated member {member_id} role to {new_role} in org {org_id}")
        return True
    
    def remove_member(self, org_id: str, member_id: str, removed_by: str) -> bool:
        """Remove member from organization (admin only)"""
        from .db import OrgUser
        
        # Check if remover is admin
        if not self._is_admin(org_id, removed_by):
            raise ValueError("Admin access required")
        
        # Check if member exists
        member = self.db.query(OrgUser).filter(
            OrgUser.id == member_id,
            OrgUser.org_id == org_id
        ).first()
        
        if not member:
            raise ValueError("Member not found")
        
        # Prevent removing the last admin
        if member.role == "admin":
            admin_count = self.db.query(OrgUser).filter(
                OrgUser.org_id == org_id,
                OrgUser.role == "admin",
                OrgUser.status == "active"
            ).count()
            
            if admin_count <= 1:
                raise ValueError("Cannot remove the last admin")
        
        member.status = "removed"
        member.updated_at = datetime.utcnow()
        self.db.commit()
        
        logger.info(f"Removed member {member_id} from org {org_id}")
        return True
    
    def check_permission(self, org_id: str, user_id: str, permission: str) -> bool:
        """Check if user has permission in organization"""
        from .db import OrgUser
        
        org_user = self.db.query(OrgUser).filter(
            OrgUser.org_id == org_id,
            OrgUser.user_id == user_id,
            OrgUser.status == "active"
        ).first()
        
        if not org_user:
            return False
        
        # Role-based permissions
        permissions = {
            "admin": ["read", "write", "delete", "invite", "manage"],
            "editor": ["read", "write"],
            "viewer": ["read"]
        }
        
        user_permissions = permissions.get(org_user.role, [])
        return permission in user_permissions
    
    def _is_admin(self, org_id: str, user_id: str) -> bool:
        """Check if user is admin in organization"""
        return self.check_permission(org_id, user_id, "manage")
    
    def _generate_slug(self, name: str) -> str:
        """Generate URL-friendly slug"""
        import re
        slug = re.sub(r'[^a-zA-Z0-9\s-]', '', name.lower())
        slug = re.sub(r'\s+', '-', slug)
        slug = slug.strip('-')
        return slug[:50]  # Limit length

# Global org manager
def get_org_manager(db: Session) -> OrgManager:
    """Get organization manager instance"""
    return OrgManager(db)

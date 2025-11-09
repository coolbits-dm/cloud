from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, JSON, Numeric, ForeignKey, Index, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

Base = declarative_base()

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    panel = Column(String(20), nullable=False)  # user, business, agency, dev
    author = Column(String(100), nullable=False)
    ts = Column(DateTime, default=datetime.utcnow)
    text = Column(Text, nullable=False)
    attachments = Column(JSON)

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"), nullable=False)
    author = Column(String(100), nullable=False)
    ts = Column(DateTime, default=datetime.utcnow)
    text = Column(Text, nullable=False)
    
    post = relationship("Post", backref="comments")

class Invocation(Base):
    __tablename__ = "invocations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"), nullable=True)
    agent_id = Column(String(50), nullable=False)  # Andy, Kim, etc.
    role = Column(String(50), nullable=False)  # sentiment, summarize, tagging, scribe
    status = Column(String(20), nullable=False)  # queued, running, done, error
    result_ref = Column(JSON)
    cost_cbT = Column(Numeric(10, 2), default=0)
    ts = Column(DateTime, default=datetime.utcnow)
    
    post = relationship("Post", backref="invocations")

class LedgerEntry(Base):
    __tablename__ = "ledger_entries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ts = Column(DateTime, default=datetime.utcnow)
    ref = Column(String(100), nullable=False)  # reference to source
    delta = Column(Numeric(10, 2), nullable=False)  # positive = credit, negative = debit
    reason = Column(String(200), nullable=False)
    meta = Column(JSON)

class RAGChunk(Base):
    __tablename__ = "rag_chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    panel = Column(String(20), nullable=False)
    source = Column(String(200), nullable=False)
    text = Column(Text, nullable=False)
    meta = Column(JSON)

class RAGEmbedding(Base):
    __tablename__ = "rag_embeddings"
    
    chunk_id = Column(UUID(as_uuid=True), ForeignKey("rag_chunks.id"), primary_key=True)
    embedding = Column(String)  # pgvector will be added in migration
    
    chunk = relationship("RAGChunk", backref="embedding")

# Database connection
def get_engine(dsn: str):
    return create_engine(dsn)

def get_session(engine):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

# Orchestrator models
class Flow(Base):
    __tablename__ = "flows"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    panel = Column(String, nullable=False)
    version = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False, server_default='false')
    created_at = Column(DateTime, nullable=False, server_default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, server_default=datetime.utcnow)
    spec = Column(JSON, nullable=False)

class FlowRun(Base):
    __tablename__ = "flow_runs"
    
    id = Column(String, primary_key=True)
    flow_id = Column(String, ForeignKey("flows.id"), nullable=False)
    version = Column(Integer, nullable=False)
    status = Column(String, nullable=False)  # queued|running|success|failed|canceled
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    trigger_ref = Column(JSON, nullable=True)
    trace_id = Column(String, nullable=True)

class RunEvent(Base):
    __tablename__ = "run_events"
    
    id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("flow_runs.id"), nullable=False)
    ts = Column(DateTime, nullable=False, server_default=datetime.utcnow)
    level = Column(String, nullable=False)  # info|error|debug
    node_id = Column(String, nullable=True)
    message = Column(String, nullable=False)
    data = Column(JSON, nullable=True)

class NodeCache(Base):
    __tablename__ = "nodes_cache"
    
    id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("flow_runs.id"), nullable=False)
    node_id = Column(String, nullable=False)
    output = Column(JSON, nullable=True)
    status = Column(String, nullable=False)  # queued|running|success|failed|skipped
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    took_ms = Column(Integer, nullable=True)

# Multi-tenant models for M20.1
class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(String, primary_key=True, default=lambda: f"org_{uuid.uuid4().hex[:12]}")
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    created_by = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    settings = Column(JSON, default=dict)
    
    # Relationships
    members = relationship("OrgUser", back_populates="organization")
    invites = relationship("OrgInvite", back_populates="organization")

class OrgUser(Base):
    __tablename__ = "org_users"
    
    id = Column(String, primary_key=True, default=lambda: f"ou_{uuid.uuid4().hex[:12]}")
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # admin, editor, viewer
    status = Column(String(50), default="active")  # active, pending, removed
    invited_by = Column(String(255))
    joined_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="members")

class OrgInvite(Base):
    __tablename__ = "org_invites"
    
    id = Column(String, primary_key=True, default=lambda: f"oi_{uuid.uuid4().hex[:12]}")
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    email = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    invited_by = Column(String(255), nullable=False)
    status = Column(String(50), default="pending")  # pending, accepted, expired
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    accepted_at = Column(DateTime)
    
    # Relationships
    organization = relationship("Organization", back_populates="invites")

# M20.3 Audit and Privacy models
class AuditEvent(Base):
    __tablename__ = "audit_events"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    actor_type = Column(String(50), nullable=False)  # user, system, nha, admin
    actor_id = Column(String(255), nullable=False)
    action = Column(String(100), nullable=False)  # post.create, ledger.debit, etc.
    target_type = Column(String(50), nullable=False)  # post, ledger, invocation, etc.
    target_id = Column(String(255), nullable=False)
    before = Column(JSON)  # State before change
    after = Column(JSON)   # State after change
    ip = Column(String(45))  # IPv4/IPv6
    user_agent = Column(Text)
    trace_id = Column(String(255))  # For correlating related events
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_audit_org_time', 'org_id', 'created_at'),
        Index('idx_audit_trace', 'trace_id'),
        Index('idx_audit_action_time', 'action', 'created_at'),
    )

class PrivacyJob(Base):
    __tablename__ = "privacy_jobs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String, ForeignKey("organizations.id"), nullable=True)  # Null for user-level jobs
    user_id = Column(String(255), nullable=True)  # Null for org-level jobs
    job_type = Column(String(50), nullable=False)  # export, deletion
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    metadata = Column(JSON)  # Job-specific data
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Indexes
    __table_args__ = (
        Index('idx_privacy_org', 'org_id'),
        Index('idx_privacy_user', 'user_id'),
        Index('idx_privacy_status', 'status'),
    )

# M20.4 RAG Connect & Eval models
class RAGChunk(Base):
    __tablename__ = "rag_chunks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    space = Column(String(100), nullable=False)  # knowledge base space
    content = Column(Text, nullable=False)
    source_uri = Column(String(500), nullable=False)
    chunk_id = Column(String(255), nullable=False)
    metadata = Column(JSON)
    embedding = Column(JSON)  # Vector embedding
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_rag_org_space', 'org_id', 'space'),
        Index('idx_rag_source', 'source_uri'),
        Index('idx_rag_chunk_id', 'chunk_id'),
    )

class RAGSource(Base):
    __tablename__ = "rag_sources"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    connector_type = Column(String(100), nullable=False)  # fs_local, http_sitemap, etc.
    config = Column(JSON)  # Connector configuration
    status = Column(String(50), default="active")  # active, paused, error
    last_sync = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_rag_source_org', 'org_id'),
        Index('idx_rag_source_type', 'connector_type'),
    )

class EvalLabel(Base):
    __tablename__ = "eval_labels"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    query = Column(Text, nullable=False)
    chunk_id = Column(String(255), nullable=False)
    label = Column(String(50), nullable=False)  # good, bad, neutral
    user_id = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_eval_org', 'org_id'),
        Index('idx_eval_chunk', 'chunk_id'),
        Index('idx_eval_user', 'user_id'),
    )

class EvalRun(Base):
    __tablename__ = "eval_runs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    space = Column(String(100), nullable=False)
    variant = Column(String(10), nullable=False)  # A, B for canary
    metrics = Column(JSON)  # Evaluation metrics
    slo_passed = Column(Boolean, default=False)
    report_path = Column(String(500))  # Path to HTML report
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_eval_run_org', 'org_id'),
        Index('idx_eval_run_variant', 'variant'),
        Index('idx_eval_run_slo', 'slo_passed'),
    )

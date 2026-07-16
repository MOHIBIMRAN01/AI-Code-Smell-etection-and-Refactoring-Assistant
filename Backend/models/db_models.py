"""SQLAlchemy database models."""

import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, LargeBinary, JSON
from sqlalchemy.orm import relationship
from config.database import Base

class Analysis(Base):
    """Analyses metadata table."""
    __tablename__ = "analyses"

    id = Column(String, primary_key=True, index=True)  # analysis_id UUID/string
    user_id = Column(String, index=True, nullable=False)  # anonymous client UUID
    repository_url = Column(String, nullable=False)
    repository_name = Column(String, nullable=False)
    repository_path = Column(String, nullable=False)
    total_java_files = Column(Integer, nullable=False)
    analyzed_classes = Column(Integer, nullable=False)
    summary = Column(String, nullable=False)
    repo_archive_blob = Column(LargeBinary, nullable=True)  # gzip tar of cloned repo
    json_report_blob = Column(LargeBinary, nullable=True)  # JSON report bytes stored in DB
    pdf_report_blob = Column(LargeBinary, nullable=True)  # PDF bytes stored in DB
    repo_expires_at = Column(DateTime, nullable=True)  # when repo_archive_blob should be purged
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    findings = relationship("Finding", back_populates="analysis", cascade="all, delete-orphan")

class Finding(Base):
    """Findings detail table."""
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(String, ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String, nullable=False)
    class_name = Column(String, nullable=False)
    smell_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    rationale = Column(String, nullable=False)
    metrics = Column(JSON, nullable=False)  # JSON representation of metrics dict
    refactoring_suggestions = Column(JSON, nullable=False)  # JSON representation of suggestions list
    similar_examples = Column(JSON, nullable=False)  # JSON representation of examples list
    llm_provider = Column(String, nullable=False)

    # Relationships
    analysis = relationship("Analysis", back_populates="findings")

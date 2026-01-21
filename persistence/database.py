"""SQLite database layer for persistence."""

from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Generator, Optional

from sqlalchemy import (Column, DateTime, Enum, Float, ForeignKey, Integer,
                        String, create_engine)
from sqlalchemy.orm import (Session, declarative_base, relationship,
                            sessionmaker)

from domain.models import (RiskCategory, SignalDirection, SignalStrength,
                           TimeHorizon)

# Database setup
DATABASE_PATH = Path("personal_risk_radar.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# SQLAlchemy Models
class RiskModel(Base):
    """SQLAlchemy model for Risk."""

    __tablename__ = "risks"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(Enum(RiskCategory), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(String, nullable=True)
    base_likelihood = Column(Float, nullable=False)
    impact = Column(Integer, nullable=False)
    confidence = Column(Float, nullable=False)
    time_horizon = Column(Enum(TimeHorizon), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    signals = relationship("SignalModel", back_populates="risk", cascade="all, delete-orphan")
    assessments = relationship("AssessmentModel", back_populates="risk", cascade="all, delete-orphan")


class SignalModel(Base):
    """SQLAlchemy model for Signal."""

    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, index=True)
    risk_id = Column(Integer, ForeignKey("risks.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(String, nullable=True)
    direction = Column(Enum(SignalDirection), nullable=False)
    strength = Column(Enum(SignalStrength), nullable=False)
    observed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    risk = relationship("RiskModel", back_populates="signals")


class AssessmentModel(Base):
    """SQLAlchemy model for Assessment."""

    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    risk_id = Column(Integer, ForeignKey("risks.id"), nullable=False)
    effective_likelihood = Column(Float, nullable=False)
    impact = Column(Integer, nullable=False)
    confidence = Column(Float, nullable=False)
    risk_score = Column(Float, nullable=False)
    signal_count = Column(Integer, default=0)
    assessed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    risk = relationship("RiskModel", back_populates="assessments")


def init_db() -> None:
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Get database session context manager."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CRUD Operations for Risk
def create_risk(db: Session, risk_data: dict) -> RiskModel:
    """Create a new risk."""
    risk = RiskModel(**risk_data)
    db.add(risk)
    db.commit()
    db.refresh(risk)
    return risk


def get_risk(db: Session, risk_id: int) -> Optional[RiskModel]:
    """Get a risk by ID."""
    return db.query(RiskModel).filter(RiskModel.id == risk_id).first()


def get_all_risks(
    db: Session, skip: int = 0, limit: int = 100, category: Optional[RiskCategory] = None
) -> list[RiskModel]:
    """Get all risks with optional filtering."""
    query = db.query(RiskModel)
    if category:
        query = query.filter(RiskModel.category == category)
    return query.offset(skip).limit(limit).all()


def update_risk(db: Session, risk_id: int, risk_data: dict) -> Optional[RiskModel]:
    """Update an existing risk."""
    risk = get_risk(db, risk_id)
    if not risk:
        return None

    for key, value in risk_data.items():
        setattr(risk, key, value)

    risk.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(risk)
    return risk


def delete_risk(db: Session, risk_id: int) -> bool:
    """Delete a risk."""
    risk = get_risk(db, risk_id)
    if not risk:
        return False

    db.delete(risk)
    db.commit()
    return True


# CRUD Operations for Signal
def create_signal(db: Session, signal_data: dict) -> SignalModel:
    """Create a new signal."""
    signal = SignalModel(**signal_data)
    db.add(signal)
    db.commit()
    db.refresh(signal)
    return signal


def get_signal(db: Session, signal_id: int) -> Optional[SignalModel]:
    """Get a signal by ID."""
    return db.query(SignalModel).filter(SignalModel.id == signal_id).first()


def get_signals_for_risk(db: Session, risk_id: int) -> list[SignalModel]:
    """Get all signals for a specific risk."""
    return db.query(SignalModel).filter(SignalModel.risk_id == risk_id).all()


def update_signal(db: Session, signal_id: int, signal_data: dict) -> Optional[SignalModel]:
    """Update an existing signal."""
    signal = get_signal(db, signal_id)
    if not signal:
        return None

    for key, value in signal_data.items():
        setattr(signal, key, value)

    db.commit()
    db.refresh(signal)
    return signal


def delete_signal(db: Session, signal_id: int) -> bool:
    """Delete a signal."""
    signal = get_signal(db, signal_id)
    if not signal:
        return False

    db.delete(signal)
    db.commit()
    return True


# CRUD Operations for Assessment
def create_assessment(db: Session, assessment_data: dict) -> AssessmentModel:
    """Create a new assessment."""
    assessment = AssessmentModel(**assessment_data)
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


def get_assessments_for_risk(
    db: Session, risk_id: int, limit: int = 10
) -> list[AssessmentModel]:
    """Get recent assessments for a specific risk."""
    return (
        db.query(AssessmentModel)
        .filter(AssessmentModel.risk_id == risk_id)
        .order_by(AssessmentModel.assessed_at.desc())
        .limit(limit)
        .all()
    )


def get_latest_assessments(db: Session, limit: int = 100) -> list[AssessmentModel]:
    """Get latest assessments across all risks."""
    # Get the latest assessment for each risk
    subquery = (
        db.query(
            AssessmentModel.risk_id,
            db.func.max(AssessmentModel.assessed_at).label("max_date"),
        )
        .group_by(AssessmentModel.risk_id)
        .subquery()
    )

    return (
        db.query(AssessmentModel)
        .join(
            subquery,
            db.and_(
                AssessmentModel.risk_id == subquery.c.risk_id,
                AssessmentModel.assessed_at == subquery.c.max_date,
            ),
        )
        .order_by(AssessmentModel.risk_score.desc())
        .limit(limit)
        .all()
    )

"""SQLite database layer for persistence."""

from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generator, Optional

from sqlalchemy import (DateTime, Engine, Enum, Float, ForeignKey, Integer,
                        String, create_engine, func)
from sqlalchemy.orm import (Mapped, Session, declarative_base, mapped_column,
                            relationship, sessionmaker)
from sqlalchemy.orm.query import Query

from domain.models import (RiskCategory, SignalDirection, SignalStrength,
                           TimeHorizon)

# Database setup
DATABASE_PATH = Path("personal_risk_radar.db")
DATABASE_URL: str = f"sqlite:///{DATABASE_PATH}"

engine: Engine = create_engine(
    url=DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal: sessionmaker[Session] = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

Base: Any = declarative_base()


# SQLAlchemy Models
class RiskModel(Base):
    """SQLAlchemy model for Risk."""

    __tablename__: str = "risks"

    id: Mapped[int] = mapped_column(__name_pos=Integer, primary_key=True, index=True)
    category: Mapped[RiskCategory] = mapped_column(
        __name_pos=Enum(RiskCategory, values_callable=lambda x: [e.value for e in x], native_enum=False), nullable=False
    )
    name: Mapped[str] = mapped_column(__name_pos=String(length=200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(__name_pos=String, nullable=True)
    base_likelihood: Mapped[float] = mapped_column(__name_pos=Float, nullable=False)
    impact: Mapped[int] = mapped_column(__name_pos=Integer, nullable=False)
    confidence: Mapped[float] = mapped_column(__name_pos=Float, nullable=False)
    time_horizon: Mapped[TimeHorizon] = mapped_column(
        __name_pos=Enum(TimeHorizon, values_callable=lambda x: [e.value for e in x], native_enum=False), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        __name_pos=DateTime, default=lambda: datetime.now(tz=timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        __name_pos=DateTime,
        default=lambda: datetime.now(tz=timezone.utc),
        onupdate=lambda: datetime.now(tz=timezone.utc),
    )

    # Relationships
    signals: Mapped[list["SignalModel"]] = relationship(
        argument="SignalModel", back_populates="risk", cascade="all, delete-orphan"
    )
    assessments: Mapped[list["AssessmentModel"]] = relationship(
        argument="AssessmentModel", back_populates="risk", cascade="all, delete-orphan"
    )


class SignalModel(Base):
    """SQLAlchemy model for Signal."""

    __tablename__: str = "signals"

    id: Mapped[int] = mapped_column(__name_pos=Integer, primary_key=True, index=True)
    risk_id: Mapped[int] = mapped_column(
        __name_pos=Integer, __type_pos=ForeignKey(column="risks.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(__name_pos=String(length=200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(__name_pos=String, nullable=True)
    direction: Mapped[SignalDirection] = mapped_column(
        __name_pos=Enum(SignalDirection, values_callable=lambda x: [e.value for e in x], native_enum=False), nullable=False
    )
    strength: Mapped[SignalStrength] = mapped_column(
        __name_pos=Enum(SignalStrength, values_callable=lambda x: [e.value for e in x], native_enum=False), nullable=False
    )
    observed_at: Mapped[Optional[datetime]] = mapped_column(
        __name_pos=DateTime, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        __name_pos=DateTime, default=lambda: datetime.now(tz=timezone.utc)
    )

    # Relationships
    risk: Mapped["RiskModel"] = relationship(
        argument="RiskModel", back_populates="signals"
    )


class AssessmentModel(Base):
    """SQLAlchemy model for Assessment."""

    __tablename__: str = "assessments"

    id: Mapped[int] = mapped_column(__name_pos=Integer, primary_key=True, index=True)
    risk_id: Mapped[int] = mapped_column(
        __name_pos=Integer, __type_pos=ForeignKey(column="risks.id"), nullable=False
    )
    effective_likelihood: Mapped[float] = mapped_column(
        __name_pos=Float, nullable=False
    )
    impact: Mapped[int] = mapped_column(__name_pos=Integer, nullable=False)
    confidence: Mapped[float] = mapped_column(__name_pos=Float, nullable=False)
    risk_score: Mapped[float] = mapped_column(__name_pos=Float, nullable=False)
    signal_count: Mapped[int] = mapped_column(__name_pos=Integer, default=0)
    assessed_at: Mapped[datetime] = mapped_column(
        __name_pos=DateTime, default=lambda: datetime.now(tz=timezone.utc)
    )

    # Relationships
    risk: Mapped["RiskModel"] = relationship(
        argument="RiskModel", back_populates="assessments"
    )


def init_db() -> None:
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Get database session context manager."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CRUD Operations for Risk
def create_risk(db: Session, risk_data: dict[str, Any]) -> RiskModel:
    """Create a new risk."""
    risk = RiskModel(**risk_data)
    db.add(instance=risk)
    db.commit()
    db.refresh(instance=risk)
    return risk


def get_risk(db: Session, risk_id: int) -> Optional[RiskModel]:
    """Get a risk by ID."""
    return db.query(RiskModel).filter(RiskModel.id == risk_id).first()


def get_all_risks(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    category: Optional[RiskCategory] = None,
) -> list[RiskModel]:
    """Get all risks with optional filtering."""
    query = db.query(RiskModel)
    if category:
        query: Query[RiskModel] = query.filter(RiskModel.category == category)
    return query.offset(offset=skip).limit(limit=limit).all()


def update_risk(
    db: Session, risk_id: int, risk_data: dict[str, Any]
) -> Optional[RiskModel]:
    """Update an existing risk."""
    risk: RiskModel | None = get_risk(db=db, risk_id=risk_id)
    if not risk:
        return None

    for key, value in risk_data.items():
        setattr(risk, key, value)

    risk.updated_at = datetime.now(tz=timezone.utc)
    db.commit()
    db.refresh(instance=risk)
    return risk


def delete_risk(db: Session, risk_id: int) -> bool:
    """Delete a risk."""
    risk: RiskModel | None = get_risk(db=db, risk_id=risk_id)
    if not risk:
        return False

    db.delete(instance=risk)
    db.commit()
    return True


# CRUD Operations for Signal
def create_signal(db: Session, signal_data: dict[str, Any]) -> SignalModel:
    """Create a new signal."""
    signal = SignalModel(**signal_data)
    db.add(instance=signal)
    db.commit()
    db.refresh(instance=signal)
    return signal


def get_signal(db: Session, signal_id: int) -> Optional[SignalModel]:
    """Get a signal by ID."""
    return db.query(SignalModel).filter(SignalModel.id == signal_id).first()


def get_signals_for_risk(db: Session, risk_id: int) -> list[SignalModel]:
    """Get all signals for a specific risk."""
    return db.query(SignalModel).filter(SignalModel.risk_id == risk_id).all()


def update_signal(
    db: Session, signal_id: int, signal_data: dict[str, Any]
) -> Optional[SignalModel]:
    """Update an existing signal."""
    signal: SignalModel | None = get_signal(db=db, signal_id=signal_id)
    if not signal:
        return None

    for key, value in signal_data.items():
        setattr(signal, key, value)

    db.commit()
    db.refresh(instance=signal)
    return signal


def delete_signal(db: Session, signal_id: int) -> bool:
    """Delete a signal."""
    signal: SignalModel | None = get_signal(db=db, signal_id=signal_id)
    if not signal:
        return False

    db.delete(instance=signal)
    db.commit()
    return True


# CRUD Operations for Assessment
def create_assessment(db: Session, assessment_data: dict[str, Any]) -> AssessmentModel:
    """Create a new assessment."""
    assessment = AssessmentModel(**assessment_data)
    db.add(instance=assessment)
    db.commit()
    db.refresh(instance=assessment)
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
            func.max(AssessmentModel.assessed_at).label("max_date"),
        )
        .group_by(AssessmentModel.risk_id)
        .subquery()
    )

    return (
        db.query(AssessmentModel)
        .join(
            subquery,
            (AssessmentModel.risk_id == subquery.c.risk_id)
            & (AssessmentModel.assessed_at == subquery.c.max_date),
        )
        .order_by(AssessmentModel.risk_score.desc())
        .limit(limit)
        .all()
    )


def get_risk_with_signals(
    db: Session, risk_id: int
) -> Optional[tuple[RiskModel, list[SignalModel]]]:
    """Get a risk along with all its signals."""
    risk: Optional[RiskModel] = get_risk(db=db, risk_id=risk_id)
    if not risk:
        return None

    signals: list[SignalModel] = get_signals_for_risk(db=db, risk_id=risk_id)
    return (risk, signals)


def get_all_risks_with_signals(
    db: Session,
) -> list[tuple[RiskModel, list[SignalModel]]]:
    """Get all risks along with their signals."""
    risks: list[RiskModel] = get_all_risks(db=db, limit=1000)

    results: list[tuple[RiskModel, list[SignalModel]]] = []
    for risk in risks:
        signals: list[SignalModel] = get_signals_for_risk(db=db, risk_id=risk.id)
        results.append((risk, signals))

    return results

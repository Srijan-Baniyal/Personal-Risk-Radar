"""FastAPI routes for Risk CRUD operations."""

from typing import Any, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from domain.models import Assessment, Risk, RiskCategory, Signal
from domain.scoring import assess_all_risks, assess_risk
from persistence.database import (
    AssessmentModel,
    RiskModel,
    SignalModel,
    create_assessment,
    create_risk,
    delete_risk,
    get_all_risks,
    get_all_risks_with_signals,
    get_db,
    get_risk,
    get_risk_with_signals,
    get_signals_for_risk,
    update_risk,
)

router = APIRouter(prefix="/api/risks", tags=["risks"])


# Request/Response Models
class RiskCreate(BaseModel):
    """Request model for creating a risk."""

    category: RiskCategory
    name: str
    description: Optional[str] = None
    base_likelihood: float
    impact: int
    confidence: float
    time_horizon: str


class RiskUpdate(BaseModel):
    """Request model for updating a risk."""

    category: Optional[RiskCategory] = None
    name: Optional[str] = None
    description: Optional[str] = None
    base_likelihood: Optional[float] = None
    impact: Optional[int] = None
    confidence: Optional[float] = None
    time_horizon: Optional[str] = None


class RiskResponse(BaseModel):
    """Response model for risk."""

    id: int
    category: str
    name: str
    description: Optional[str]
    base_likelihood: float
    impact: int
    confidence: float
    time_horizon: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


# Endpoints
@router.post(path="/", response_model=RiskResponse, status_code=status.HTTP_201_CREATED)
def create_risk_endpoint(risk: RiskCreate) -> RiskResponse:
    """Create a new risk."""
    with get_db() as db:
        # Validate using domain model
        _ = Risk(**risk.model_dump())

        # Create in database
        db_risk: RiskModel = create_risk(db=db, risk_data=risk.model_dump())

        return RiskResponse(
            id=db_risk.id,
            category=db_risk.category.value,
            name=db_risk.name,
            description=db_risk.description,
            base_likelihood=db_risk.base_likelihood,
            impact=db_risk.impact,
            confidence=db_risk.confidence,
            time_horizon=db_risk.time_horizon.value,
            created_at=db_risk.created_at.isoformat(),
            updated_at=db_risk.updated_at.isoformat(),
        )


@router.get(path="/{risk_id}", response_model=RiskResponse)
def get_risk_endpoint(risk_id: int) -> RiskResponse:
    """Get a risk by ID."""
    with get_db() as db:
        db_risk: RiskModel | None = get_risk(db=db, risk_id=risk_id)
        if not db_risk:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Risk not found"
            )

        return RiskResponse(
            id=db_risk.id,
            category=db_risk.category.value,
            name=db_risk.name,
            description=db_risk.description,
            base_likelihood=db_risk.base_likelihood,
            impact=db_risk.impact,
            confidence=db_risk.confidence,
            time_horizon=db_risk.time_horizon.value,
            created_at=db_risk.created_at.isoformat(),
            updated_at=db_risk.updated_at.isoformat(),
        )


@router.get(path="/", response_model=list[RiskResponse])
def get_all_risks_endpoint(
    skip: int = 0, limit: int = 100, category: Optional[RiskCategory] = None
) -> list[RiskResponse]:
    """Get all risks with optional filtering."""
    with get_db() as db:
        db_risks: list[RiskModel] = get_all_risks(
            db=db, skip=skip, limit=limit, category=category
        )

        return [
            RiskResponse(
                id=risk.id,
                category=risk.category.value,
                name=risk.name,
                description=risk.description,
                base_likelihood=risk.base_likelihood,
                impact=risk.impact,
                confidence=risk.confidence,
                time_horizon=risk.time_horizon.value,
                created_at=risk.created_at.isoformat(),
                updated_at=risk.updated_at.isoformat(),
            )
            for risk in db_risks
        ]


@router.put(path="/{risk_id}", response_model=RiskResponse)
def update_risk_endpoint(risk_id: int, risk: RiskUpdate) -> RiskResponse:
    """Update an existing risk."""
    with get_db() as db:
        # Filter out None values
        update_data: dict[str, Any] = {
            k: v for k, v in risk.model_dump().items() if v is not None
        }

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No update data provided",
            )

        db_risk: RiskModel | None = update_risk(
            db=db, risk_id=risk_id, risk_data=update_data
        )
        if not db_risk:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Risk not found"
            )

        return RiskResponse(
            id=db_risk.id,
            category=db_risk.category.value,
            name=db_risk.name,
            description=db_risk.description,
            base_likelihood=db_risk.base_likelihood,
            impact=db_risk.impact,
            confidence=db_risk.confidence,
            time_horizon=db_risk.time_horizon.value,
            created_at=db_risk.created_at.isoformat(),
            updated_at=db_risk.updated_at.isoformat(),
        )


@router.delete("/{risk_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_risk_endpoint(risk_id: int) -> None:
    """Delete a risk."""
    with get_db() as db:
        success: bool = delete_risk(db=db, risk_id=risk_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Risk not found"
            )


class AssessmentResponse(BaseModel):
    """Response model for assessment."""

    id: int
    risk_id: int
    effective_likelihood: float
    impact: int
    confidence: float
    risk_score: float
    signal_count: int
    assessed_at: str

    class Config:
        from_attributes = True


@router.post(
    path="/{risk_id}/recompute",
    response_model=AssessmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def recompute_risk_endpoint(risk_id: int) -> AssessmentResponse:
    """Recompute risk score based on current signals and create new assessment."""
    with get_db() as db:
        # Get risk with signals
        result: Optional[tuple[RiskModel, list[SignalModel]]] = get_risk_with_signals(
            db=db, risk_id=risk_id
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Risk not found"
            )

        db_risk, db_signals = result

        # Convert to domain models
        risk: Risk = Risk(
            id=db_risk.id,
            category=db_risk.category,
            name=db_risk.name,
            description=db_risk.description,
            base_likelihood=db_risk.base_likelihood,
            impact=db_risk.impact,
            confidence=db_risk.confidence,
            time_horizon=db_risk.time_horizon,
            created_at=db_risk.created_at,
            updated_at=db_risk.updated_at,
        )

        signals: list[Signal] = [Signal.from_db_model(db_signal=s) for s in db_signals]

        # Compute assessment
        assessment: Assessment = assess_risk(risk=risk, signals=signals)

        # Save assessment to database
        db_assessment: AssessmentModel = create_assessment(
            db=db,
            assessment_data={
                "risk_id": assessment.risk_id,
                "effective_likelihood": assessment.effective_likelihood,
                "impact": assessment.impact,
                "confidence": assessment.confidence,
                "risk_score": assessment.risk_score,
                "signal_count": assessment.signal_count,
                "assessed_at": assessment.assessed_at,
            },
        )

        return AssessmentResponse(
            id=db_assessment.id,
            risk_id=db_assessment.risk_id,
            effective_likelihood=db_assessment.effective_likelihood,
            impact=db_assessment.impact,
            confidence=db_assessment.confidence,
            risk_score=db_assessment.risk_score,
            signal_count=db_assessment.signal_count,
            assessed_at=db_assessment.assessed_at.isoformat(),
        )


@router.post(
    path="/recompute",
    response_model=list[AssessmentResponse],
    status_code=status.HTTP_201_CREATED,
)
def recompute_all_risks_endpoint() -> list[AssessmentResponse]:
    """Recompute all risk scores based on current signals and create new assessments."""
    with get_db() as db:
        # Get all risks with their signals
        risks_with_signals_db: list[tuple[RiskModel, list[SignalModel]]] = (
            get_all_risks_with_signals(db=db)
        )

        # Convert to domain models
        risks_with_signals: list[tuple[Risk, list[Signal]]] = []
        for db_risk, db_signals in risks_with_signals_db:
            risk: Risk = Risk(
                id=db_risk.id,
                category=db_risk.category,
                name=db_risk.name,
                description=db_risk.description,
                base_likelihood=db_risk.base_likelihood,
                impact=db_risk.impact,
                confidence=db_risk.confidence,
                time_horizon=db_risk.time_horizon,
                created_at=db_risk.created_at,
                updated_at=db_risk.updated_at,
            )
            signals: list[Signal] = [
                Signal.from_db_model(db_signal=s) for s in db_signals
            ]
            risks_with_signals.append((risk, signals))

        # Compute all assessments
        assessments: list[Assessment] = assess_all_risks(
            risks_with_signals=risks_with_signals
        )

        # Save all assessments to database
        db_assessments: list[AssessmentModel] = []
        for assessment in assessments:
            db_assessment: AssessmentModel = create_assessment(
                db=db,
                assessment_data={
                    "risk_id": assessment.risk_id,
                    "effective_likelihood": assessment.effective_likelihood,
                    "impact": assessment.impact,
                    "confidence": assessment.confidence,
                    "risk_score": assessment.risk_score,
                    "signal_count": assessment.signal_count,
                    "assessed_at": assessment.assessed_at,
                },
            )
            db_assessments.append(db_assessment)

        return [
            AssessmentResponse(
                id=db_assessment.id,
                risk_id=db_assessment.risk_id,
                effective_likelihood=db_assessment.effective_likelihood,
                impact=db_assessment.impact,
                confidence=db_assessment.confidence,
                risk_score=db_assessment.risk_score,
                signal_count=db_assessment.signal_count,
                assessed_at=db_assessment.assessed_at.isoformat(),
            )
            for db_assessment in db_assessments
        ]


@router.get(path="/{risk_id}/with-signals", response_model=dict[str, Any])
def get_risk_with_signals_endpoint(risk_id: int) -> dict[str, Any]:
    """Get a risk with all its signals."""
    with get_db() as db:
        db_risk: RiskModel | None = get_risk(db=db, risk_id=risk_id)
        if not db_risk:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Risk not found"
            )

        db_signals: list[SignalModel] = get_signals_for_risk(db=db, risk_id=risk_id)

        # Convert to domain models
        domain_risk = Risk(
            id=db_risk.id,
            category=db_risk.category,
            name=db_risk.name,
            description=db_risk.description,
            base_likelihood=db_risk.base_likelihood,
            impact=db_risk.impact,
            confidence=db_risk.confidence,
            time_horizon=db_risk.time_horizon,
            created_at=db_risk.created_at,
            updated_at=db_risk.updated_at,
        )

        domain_signals: list[Signal] = [
            Signal(
                id=signal.id,
                risk_id=signal.risk_id,
                name=signal.name,
                description=signal.description,
                direction=signal.direction,
                strength=signal.strength,
                observed_at=signal.observed_at,
                created_at=signal.created_at,
            )
            for signal in db_signals
        ]

        return {
            "risk": domain_risk.model_dump(),
            "signals": [s.model_dump() for s in domain_signals],
        }


@router.post(path="/{risk_id}/assess", response_model=dict[str, Any])
def assess_risk_endpoint(risk_id: int) -> dict[str, Any]:
    """Generate a new assessment for a risk."""
    with get_db() as db:
        db_risk: RiskModel | None = get_risk(db=db, risk_id=risk_id)
        if not db_risk:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Risk not found"
            )

        db_signals: list[SignalModel] = get_signals_for_risk(db=db, risk_id=risk_id)

        # Convert to domain models
        domain_risk = Risk(
            id=db_risk.id,
            category=db_risk.category,
            name=db_risk.name,
            description=db_risk.description,
            base_likelihood=db_risk.base_likelihood,
            impact=db_risk.impact,
            confidence=db_risk.confidence,
            time_horizon=db_risk.time_horizon,
        )

        domain_signals: list[Signal] = [
            Signal(
                id=signal.id,
                risk_id=signal.risk_id,
                name=signal.name,
                description=signal.description,
                direction=signal.direction,
                strength=signal.strength,
                observed_at=signal.observed_at,
            )
            for signal in db_signals
        ]

        # Generate assessment
        assessment: Assessment = assess_risk(risk=domain_risk, signals=domain_signals)

        # Save to database
        assessment_data: dict[str, Any] = assessment.model_dump(exclude={"id"})
        db_assessment: AssessmentModel = create_assessment(
            db=db, assessment_data=assessment_data
        )

        return {
            "assessment": {
                "id": db_assessment.id,
                "risk_id": db_assessment.risk_id,
                "effective_likelihood": db_assessment.effective_likelihood,
                "impact": db_assessment.impact,
                "confidence": db_assessment.confidence,
                "risk_score": db_assessment.risk_score,
                "signal_count": db_assessment.signal_count,
                "assessed_at": db_assessment.assessed_at.isoformat(),
            },
            "risk": domain_risk.model_dump(),
        }

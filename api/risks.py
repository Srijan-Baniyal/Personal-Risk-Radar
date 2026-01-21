"""FastAPI routes for Risk CRUD operations."""

from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from domain.models import (Assessment, Risk, RiskCategory, RiskWithSignals,
                           Signal)
from domain.scoring import assess_risk
from persistence.database import (create_assessment, create_risk, delete_risk,
                                  get_all_risks, get_db, get_risk,
                                  get_signals_for_risk, update_risk)

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
@router.post("/", response_model=RiskResponse, status_code=status.HTTP_201_CREATED)
def create_risk_endpoint(risk: RiskCreate) -> RiskResponse:
    """Create a new risk."""
    with get_db() as db:
        # Validate using domain model
        domain_risk = Risk(**risk.model_dump())

        # Create in database
        db_risk = create_risk(db, risk.model_dump())

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


@router.get("/{risk_id}", response_model=RiskResponse)
def get_risk_endpoint(risk_id: int) -> RiskResponse:
    """Get a risk by ID."""
    with get_db() as db:
        db_risk = get_risk(db, risk_id)
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


@router.get("/", response_model=list[RiskResponse])
def get_all_risks_endpoint(
    skip: int = 0, limit: int = 100, category: Optional[RiskCategory] = None
) -> list[RiskResponse]:
    """Get all risks with optional filtering."""
    with get_db() as db:
        db_risks = get_all_risks(db, skip=skip, limit=limit, category=category)

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


@router.put("/{risk_id}", response_model=RiskResponse)
def update_risk_endpoint(risk_id: int, risk: RiskUpdate) -> RiskResponse:
    """Update an existing risk."""
    with get_db() as db:
        # Filter out None values
        update_data = {k: v for k, v in risk.model_dump().items() if v is not None}

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No update data provided",
            )

        db_risk = update_risk(db, risk_id, update_data)
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
        success = delete_risk(db, risk_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Risk not found"
            )


@router.get("/{risk_id}/with-signals", response_model=dict)
def get_risk_with_signals_endpoint(risk_id: int) -> dict:
    """Get a risk with all its signals."""
    with get_db() as db:
        db_risk = get_risk(db, risk_id)
        if not db_risk:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Risk not found"
            )

        db_signals = get_signals_for_risk(db, risk_id)

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

        domain_signals = [
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


@router.post("/{risk_id}/assess", response_model=dict)
def assess_risk_endpoint(risk_id: int) -> dict:
    """Generate a new assessment for a risk."""
    with get_db() as db:
        db_risk = get_risk(db, risk_id)
        if not db_risk:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Risk not found"
            )

        db_signals = get_signals_for_risk(db, risk_id)

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

        domain_signals = [
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
        assessment = assess_risk(domain_risk, domain_signals)

        # Save to database
        assessment_data = assessment.model_dump(exclude={"id"})
        db_assessment = create_assessment(db, assessment_data)

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

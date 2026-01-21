"""FastAPI routes for Signal CRUD operations."""

from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from domain.models import SignalDirection, SignalStrength
from persistence.database import (create_signal, delete_signal, get_db,
                                  get_risk, get_signal, get_signals_for_risk,
                                  update_signal)

router = APIRouter(prefix="/api/signals", tags=["signals"])


# Request/Response Models
class SignalCreate(BaseModel):
    """Request model for creating a signal."""

    risk_id: int
    name: str
    description: Optional[str] = None
    direction: SignalDirection
    strength: SignalStrength
    observed_at: Optional[str] = None


class SignalUpdate(BaseModel):
    """Request model for updating a signal."""

    name: Optional[str] = None
    description: Optional[str] = None
    direction: Optional[SignalDirection] = None
    strength: Optional[SignalStrength] = None
    observed_at: Optional[str] = None


class SignalResponse(BaseModel):
    """Response model for signal."""

    id: int
    risk_id: int
    name: str
    description: Optional[str]
    direction: str
    strength: str
    observed_at: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


# Endpoints
@router.post("/", response_model=SignalResponse, status_code=status.HTTP_201_CREATED)
def create_signal_endpoint(signal: SignalCreate) -> SignalResponse:
    """Create a new signal."""
    with get_db() as db:
        # Verify risk exists
        risk = get_risk(db, signal.risk_id)
        if not risk:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Risk not found"
            )

        # Create signal
        db_signal = create_signal(db, signal.model_dump())

        return SignalResponse(
            id=db_signal.id,
            risk_id=db_signal.risk_id,
            name=db_signal.name,
            description=db_signal.description,
            direction=db_signal.direction.value,
            strength=db_signal.strength.value,
            observed_at=db_signal.observed_at.isoformat() if db_signal.observed_at else None,
            created_at=db_signal.created_at.isoformat(),
        )


@router.get("/{signal_id}", response_model=SignalResponse)
def get_signal_endpoint(signal_id: int) -> SignalResponse:
    """Get a signal by ID."""
    with get_db() as db:
        db_signal = get_signal(db, signal_id)
        if not db_signal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Signal not found"
            )

        return SignalResponse(
            id=db_signal.id,
            risk_id=db_signal.risk_id,
            name=db_signal.name,
            description=db_signal.description,
            direction=db_signal.direction.value,
            strength=db_signal.strength.value,
            observed_at=db_signal.observed_at.isoformat() if db_signal.observed_at else None,
            created_at=db_signal.created_at.isoformat(),
        )


@router.get("/risk/{risk_id}", response_model=list[SignalResponse])
def get_signals_for_risk_endpoint(risk_id: int) -> list[SignalResponse]:
    """Get all signals for a specific risk."""
    with get_db() as db:
        # Verify risk exists
        risk = get_risk(db, risk_id)
        if not risk:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Risk not found"
            )

        db_signals = get_signals_for_risk(db, risk_id)

        return [
            SignalResponse(
                id=signal.id,
                risk_id=signal.risk_id,
                name=signal.name,
                description=signal.description,
                direction=signal.direction.value,
                strength=signal.strength.value,
                observed_at=signal.observed_at.isoformat() if signal.observed_at else None,
                created_at=signal.created_at.isoformat(),
            )
            for signal in db_signals
        ]


@router.put("/{signal_id}", response_model=SignalResponse)
def update_signal_endpoint(signal_id: int, signal: SignalUpdate) -> SignalResponse:
    """Update an existing signal."""
    with get_db() as db:
        # Filter out None values
        update_data = {k: v for k, v in signal.model_dump().items() if v is not None}

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No update data provided",
            )

        db_signal = update_signal(db, signal_id, update_data)
        if not db_signal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Signal not found"
            )

        return SignalResponse(
            id=db_signal.id,
            risk_id=db_signal.risk_id,
            name=db_signal.name,
            description=db_signal.description,
            direction=db_signal.direction.value,
            strength=db_signal.strength.value,
            observed_at=db_signal.observed_at.isoformat() if db_signal.observed_at else None,
            created_at=db_signal.created_at.isoformat(),
        )


@router.delete("/{signal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_signal_endpoint(signal_id: int) -> None:
    """Delete a signal."""
    with get_db() as db:
        success = delete_signal(db, signal_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Signal not found"
            )

"""Domain models for Personal Risk Radar."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class RiskCategory(str, Enum):
    """Fixed risk categories."""

    CAREER = "career"
    FINANCIAL = "financial"
    HEALTH = "health"
    TECHNICAL = "technical"
    PERSONAL = "personal"


class TimeHorizon(str, Enum):
    """Time horizon for risk materialization."""

    WEEKS = "weeks"
    MONTHS = "months"


class SignalStrength(str, Enum):
    """Strength of a signal's impact on risk."""

    WEAK = "weak"
    MEDIUM = "medium"
    STRONG = "strong"


class SignalDirection(str, Enum):
    """Whether a signal increases or decreases risk."""

    INCREASE = "increase"
    DECREASE = "decrease"


class Risk(BaseModel):
    """A future uncertainty with potential impact."""

    id: Optional[int] = None
    category: RiskCategory
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    base_likelihood: float = Field(..., ge=0.0, le=1.0)
    impact: int = Field(..., ge=1, le=5)
    confidence: float = Field(..., ge=0.0, le=1.0)
    time_horizon: TimeHorizon
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator("base_likelihood", "confidence")
    @classmethod
    def validate_probability(cls, v: float) -> float:
        """Ensure probability values are between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Probability must be between 0.0 and 1.0")
        return v

    @field_validator("impact")
    @classmethod
    def validate_impact(cls, v: int) -> int:
        """Ensure impact is between 1 and 5."""
        if not 1 <= v <= 5:
            raise ValueError("Impact must be between 1 and 5")
        return v


class Signal(BaseModel):
    """A measurable early warning sign linked to a risk."""

    id: Optional[int] = None
    risk_id: int
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    direction: SignalDirection
    strength: SignalStrength
    observed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    def get_likelihood_modifier(self) -> float:
        """
        Calculate how much this signal modifies risk likelihood.

        Returns:
            Modifier value (positive for increase, negative for decrease)
        """
        # Base modifiers by strength
        modifiers = {
            SignalStrength.WEAK: 0.05,
            SignalStrength.MEDIUM: 0.10,
            SignalStrength.STRONG: 0.20,
        }

        modifier = modifiers[self.strength]

        # Flip sign for decrease signals
        if self.direction == SignalDirection.DECREASE:
            modifier = -modifier

        return modifier


class Assessment(BaseModel):
    """A snapshot of computed risk scores at a point in time."""

    id: Optional[int] = None
    risk_id: int
    effective_likelihood: float = Field(..., ge=0.0, le=1.0)
    impact: int = Field(..., ge=1, le=5)
    confidence: float = Field(..., ge=0.0, le=1.0)
    risk_score: float = Field(..., ge=0.0)
    signal_count: int = Field(default=0, ge=0)
    assessed_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("effective_likelihood", "confidence")
    @classmethod
    def validate_probability(cls, v: float) -> float:
        """Ensure probability values are between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Probability must be between 0.0 and 1.0")
        return v


class RiskWithSignals(Risk):
    """Risk model with associated signals."""

    signals: list[Signal] = Field(default_factory=list)


class AssessmentWithRisk(Assessment):
    """Assessment model with associated risk details."""

    risk: Risk

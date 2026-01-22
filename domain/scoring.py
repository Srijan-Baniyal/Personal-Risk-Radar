"""Risk scoring logic - transparent and explainable."""

from typing import Optional

from domain.models import Assessment, Risk, Signal


def calculate_effective_likelihood(
    base_likelihood: float, signals: list[Signal]
) -> float:
    """
    Calculate effective likelihood by applying signal modifiers.

    Args:
        base_likelihood: Base probability (0-1)
        signals: List of signals affecting the risk

    Returns:
        Effective likelihood (clamped to 0-1)
    """
    effective: float = base_likelihood

    for signal in signals:
        modifier: float = signal.get_likelihood_modifier()
        effective += modifier

    # Clamp to valid probability range
    return max(0.0, min(1.0, effective))


def calculate_risk_score(
    likelihood: float, impact: int, confidence: float
) -> float:
    """
    Calculate risk score using the core formula.

    Formula: risk_score = likelihood × impact × confidence

    Args:
        likelihood: Probability of occurrence (0-1)
        impact: Severity scale (1-5)
        confidence: Confidence in assessment (0-1)

    Returns:
        Risk score (0-5)
    """
    return likelihood * impact * confidence


def assess_risk(risk: Risk, signals: Optional[list[Signal]] = None) -> Assessment:
    """
    Generate a complete risk assessment.

    Args:
        risk: The risk to assess
        signals: Optional list of signals (defaults to empty list)

    Returns:
        Complete assessment with computed scores
    """
    if signals is None:
        signals = []

    # Calculate effective likelihood with signal adjustments
    effective_likelihood: float = calculate_effective_likelihood(base_likelihood=risk.base_likelihood, signals=signals)

    # Calculate final risk score
    risk_score: float = calculate_risk_score(likelihood=effective_likelihood, impact=risk.impact, confidence=risk.confidence)

    if risk.id is None:
        raise ValueError("Risk must have an ID to create an assessment")

    return Assessment(
        risk_id=risk.id,
        effective_likelihood=effective_likelihood,
        impact=risk.impact,
        confidence=risk.confidence,
        risk_score=risk_score,
        signal_count=len(signals),
    )


def assess_all_risks(risks_with_signals: list[tuple[Risk, list[Signal]]]) -> list[Assessment]:
    """
    Generate assessments for multiple risks.

    Args:
        risks_with_signals: List of (risk, signals) tuples

    Returns:
        List of assessments
    """
    return [assess_risk(risk=risk, signals=signals) for risk, signals in risks_with_signals]

"""Unit tests for domain models and scoring logic."""

from domain.models import (Risk, RiskCategory, Signal, SignalDirection,
                           SignalStrength, TimeHorizon)
from domain.scoring import (assess_risk, calculate_effective_likelihood,
                            calculate_risk_score)


def test_signal_likelihood_modifiers() -> None:
    """Test that signals calculate correct likelihood modifiers."""
    # Test WEAK signals
    signal = Signal(
        id=1,
        risk_id=1,
        name="Test",
        direction=SignalDirection.INCREASE,
        strength=SignalStrength.WEAK,
    )
    assert signal.get_likelihood_modifier() == 0.05
    
    signal.direction = SignalDirection.DECREASE
    assert signal.get_likelihood_modifier() == -0.05
    
    # Test MEDIUM signals
    signal.strength = SignalStrength.MEDIUM
    signal.direction = SignalDirection.INCREASE
    assert signal.get_likelihood_modifier() == 0.10
    
    signal.direction = SignalDirection.DECREASE
    assert signal.get_likelihood_modifier() == -0.10
    
    # Test STRONG signals
    signal.strength = SignalStrength.STRONG
    signal.direction = SignalDirection.INCREASE
    assert signal.get_likelihood_modifier() == 0.20
    
    signal.direction = SignalDirection.DECREASE
    assert signal.get_likelihood_modifier() == -0.20
    
    print("✓ Signal likelihood modifiers correct")


def test_calculate_effective_likelihood() -> None:
    """Test effective likelihood calculation with signals."""
    base_likelihood = 0.5
    
    # No signals
    signals: list[Signal] = []
    result = calculate_effective_likelihood(base_likelihood, signals)
    assert result == 0.5
    
    # Single increase signal
    signals = [
        Signal(
            id=1,
            risk_id=1,
            name="Test",
            direction=SignalDirection.INCREASE,
            strength=SignalStrength.STRONG,
        )
    ]
    result = calculate_effective_likelihood(base_likelihood, signals)
    assert result == 0.7  # 0.5 + 0.2
    
    # Multiple signals
    signals = [
        Signal(
            id=1,
            risk_id=1,
            name="Increase",
            direction=SignalDirection.INCREASE,
            strength=SignalStrength.STRONG,
        ),
        Signal(
            id=2,
            risk_id=1,
            name="Decrease",
            direction=SignalDirection.DECREASE,
            strength=SignalStrength.WEAK,
        ),
    ]
    result = calculate_effective_likelihood(base_likelihood, signals)
    assert abs(result - 0.65) < 0.01  # 0.5 + 0.2 - 0.05
    
    # Test clamping upper bound
    signals = [
        Signal(
            id=i,
            risk_id=1,
            name=f"Strong {i}",
            direction=SignalDirection.INCREASE,
            strength=SignalStrength.STRONG,
        )
        for i in range(10)
    ]
    result = calculate_effective_likelihood(0.9, signals)
    assert result == 1.0
    
    # Test clamping lower bound
    signals = [
        Signal(
            id=i,
            risk_id=1,
            name=f"Strong {i}",
            direction=SignalDirection.DECREASE,
            strength=SignalStrength.STRONG,
        )
        for i in range(10)
    ]
    result = calculate_effective_likelihood(0.1, signals)
    assert result == 0.0
    
    print("✓ Effective likelihood calculation correct")


def test_calculate_risk_score() -> None:
    """Test risk score calculation."""
    # Standard case
    score = calculate_risk_score(likelihood=0.5, impact=3, confidence=0.8)
    assert abs(score - 1.2) < 0.01
    
    # Maximum score
    score = calculate_risk_score(likelihood=1.0, impact=5, confidence=1.0)
    assert score == 5.0
    
    # Minimum score
    score = calculate_risk_score(likelihood=0.0, impact=1, confidence=0.0)
    assert score == 0.0
    
    print("✓ Risk score calculation correct")


def test_assess_risk() -> None:
    """Test full risk assessment."""
    risk = Risk(
        id=1,
        category=RiskCategory.TECHNICAL,
        name="Test Risk",
        base_likelihood=0.5,
        impact=3,
        confidence=0.8,
        time_horizon=TimeHorizon.MONTHS,
    )
    
    signals = [
        Signal(
            id=1,
            risk_id=1,
            name="Increase Signal",
            direction=SignalDirection.INCREASE,
            strength=SignalStrength.STRONG,
        ),
        Signal(
            id=2,
            risk_id=1,
            name="Decrease Signal",
            direction=SignalDirection.DECREASE,
            strength=SignalStrength.WEAK,
        ),
    ]
    
    assessment = assess_risk(risk, signals)
    
    # Check effective likelihood: 0.5 + 0.2 - 0.05 = 0.65
    assert abs(assessment.effective_likelihood - 0.65) < 0.01
    
    # Check risk score: 0.65 * 3 * 0.8 = 1.56
    assert abs(assessment.risk_score - 1.56) < 0.01
    
    # Check other fields
    assert assessment.risk_id == 1
    assert assessment.impact == 3
    assert assessment.confidence == 0.8
    assert assessment.signal_count == 2
    
    print("✓ Risk assessment correct")


def test_risk_model_validation() -> None:
    """Test that Risk model validates inputs correctly."""
    # Valid risk
    risk = Risk(
        category=RiskCategory.FINANCIAL,
        name="Valid Risk",
        base_likelihood=0.5,
        impact=3,
        confidence=0.8,
        time_horizon=TimeHorizon.WEEKS,
    )
    assert risk.base_likelihood == 0.5
    
    # Test likelihood bounds
    try:
        Risk(
            category=RiskCategory.FINANCIAL,
            name="Invalid",
            base_likelihood=1.5,  # Invalid: > 1.0
            impact=3,
            confidence=0.8,
            time_horizon=TimeHorizon.WEEKS,
        )
        assert False, "Should have raised validation error"
    except ValueError:
        pass
    
    # Test impact bounds
    try:
        Risk(
            category=RiskCategory.FINANCIAL,
            name="Invalid",
            base_likelihood=0.5,
            impact=10,  # Invalid: > 5
            confidence=0.8,
            time_horizon=TimeHorizon.WEEKS,
        )
        assert False, "Should have raised validation error"
    except ValueError:
        pass
    
    print("✓ Risk model validation works")


if __name__ == "__main__":
    print("Running unit tests...\n")
    test_signal_likelihood_modifiers()
    test_calculate_effective_likelihood()
    test_calculate_risk_score()
    test_assess_risk()
    test_risk_model_validation()
    print("\n✅ All unit tests passed!")

"""Integration tests for recompute endpoints."""

from typing import Any

import requests

from domain.models import (RiskCategory, SignalDirection, SignalStrength,
                           TimeHorizon)

BASE_URL = "http://localhost:8000"


def test_recompute_single_risk() -> None:
    """Test recomputing a single risk with signals."""
    # Create a test risk
    risk_data: dict[str, Any] = {
        "category": RiskCategory.TECHNICAL.value,
        "name": "Test Risk for Recompute",
        "description": "Testing the recompute endpoint",
        "base_likelihood": 0.5,
        "impact": 3,
        "confidence": 0.8,
        "time_horizon": TimeHorizon.MONTHS.value,
    }
    
    response: requests.Response = requests.post(f"{BASE_URL}/api/risks/", json=risk_data)
    assert response.status_code == 201
    risk: dict[str, Any] = response.json()
    risk_id: int = risk["id"]
    print(f"Created risk with ID: {risk_id}")
    
    # Add some signals
    signal1_data: dict[str, Any] = {
        "risk_id": risk_id,
        "name": "Positive Signal",
        "description": "This increases the risk",
        "direction": SignalDirection.INCREASE.value,
        "strength": SignalStrength.STRONG.value,
    }
    
    response = requests.post(f"{BASE_URL}/api/signals/", json=signal1_data)
    assert response.status_code == 201
    print(f"Created signal: {response.json()['name']}")
    
    signal2_data: dict[str, Any] = {
        "risk_id": risk_id,
        "name": "Negative Signal",
        "description": "This decreases the risk",
        "direction": SignalDirection.DECREASE.value,
        "strength": SignalStrength.WEAK.value,
    }
    
    response = requests.post(f"{BASE_URL}/api/signals/", json=signal2_data)
    assert response.status_code == 201
    print(f"Created signal: {response.json()['name']}")
    
    # Recompute the risk
    response = requests.post(f"{BASE_URL}/api/risks/{risk_id}/recompute")
    assert response.status_code == 201
    assessment: dict[str, Any] = response.json()
    
    print("\n=== Assessment Result ===")
    print(f"Risk ID: {assessment['risk_id']}")
    print(f"Base Likelihood: {risk['base_likelihood']}")
    print(f"Effective Likelihood: {assessment['effective_likelihood']}")
    print(f"Impact: {assessment['impact']}")
    print(f"Confidence: {assessment['confidence']}")
    print(f"Risk Score: {assessment['risk_score']}")
    print(f"Signal Count: {assessment['signal_count']}")
    
    # Expected: base_likelihood (0.5) + strong increase (0.2) - weak decrease (0.05) = 0.65
    expected_likelihood: float = 0.5 + 0.2 - 0.05
    assert abs(assessment["effective_likelihood"] - expected_likelihood) < 0.01
    print(f"\n✓ Likelihood calculation correct: {expected_likelihood}")
    
    # Expected risk score: 0.65 * 3 * 0.8 = 1.56
    expected_score: float = expected_likelihood * 3 * 0.8
    assert abs(assessment["risk_score"] - expected_score) < 0.01
    print(f"✓ Risk score calculation correct: {expected_score}")


def test_recompute_all_risks() -> None:
    """Test recomputing all risks in the system."""
    print("\n\n=== Testing Recompute All ===")
    
    response: requests.Response = requests.post(f"{BASE_URL}/api/risks/recompute")
    assert response.status_code == 201
    assessments: list[dict[str, Any]] = response.json()
    
    print(f"Recomputed {len(assessments)} risks")
    for assessment in assessments:
        print(f"  - Risk {assessment['risk_id']}: score={assessment['risk_score']:.2f}, "
              f"likelihood={assessment['effective_likelihood']:.2f}, "
              f"signals={assessment['signal_count']}")


def test_likelihood_modifiers() -> None:
    """Test that signal strength modifiers work correctly."""
    print("\n\n=== Testing Signal Modifiers ===")
    
    # Create a base risk
    risk_data: dict[str, Any] = {
        "category": RiskCategory.FINANCIAL.value,
        "name": "Test Modifier Risk",
        "base_likelihood": 0.5,
        "impact": 3,
        "confidence": 1.0,
        "time_horizon": TimeHorizon.WEEKS.value,
    }
    
    response: requests.Response = requests.post(f"{BASE_URL}/api/risks/", json=risk_data)
    assert response.status_code == 201
    risk: dict[str, Any] = response.json()
    risk_id: int = risk["id"]
    
    test_cases: list[tuple[str, SignalDirection, SignalStrength, float]] = [
        ("WEAK increase", SignalDirection.INCREASE, SignalStrength.WEAK, 0.55),
        ("MEDIUM increase", SignalDirection.INCREASE, SignalStrength.MEDIUM, 0.60),
        ("STRONG increase", SignalDirection.INCREASE, SignalStrength.STRONG, 0.70),
        ("WEAK decrease", SignalDirection.DECREASE, SignalStrength.WEAK, 0.45),
        ("MEDIUM decrease", SignalDirection.DECREASE, SignalStrength.MEDIUM, 0.40),
        ("STRONG decrease", SignalDirection.DECREASE, SignalStrength.STRONG, 0.30),
    ]
    
    for name, direction, strength, expected_likelihood in test_cases:
        # Create signal
        signal_data: dict[str, Any] = {
            "risk_id": risk_id,
            "name": f"Test {name}",
            "direction": direction.value,
            "strength": strength.value,
        }
        
        response = requests.post(f"{BASE_URL}/api/signals/", json=signal_data)
        assert response.status_code == 201
        signal_id: int = response.json()["id"]
        
        # Recompute
        response = requests.post(f"{BASE_URL}/api/risks/{risk_id}/recompute")
        assert response.status_code == 201
        assessment: dict[str, Any] = response.json()
        
        # Verify
        assert abs(assessment["effective_likelihood"] - expected_likelihood) < 0.01
        print(f"✓ {name}: {assessment['effective_likelihood']:.2f} (expected {expected_likelihood})")
        
        # Clean up signal for next test
        requests.delete(f"{BASE_URL}/api/signals/{signal_id}")


def test_likelihood_clamping() -> None:
    """Test that effective likelihood is clamped to [0, 1]."""
    print("\n\n=== Testing Likelihood Clamping ===")
    
    # Test upper bound clamping
    risk_data: dict[str, Any] = {
        "category": RiskCategory.HEALTH.value,
        "name": "Test Upper Clamp",
        "base_likelihood": 0.9,
        "impact": 5,
        "confidence": 1.0,
        "time_horizon": TimeHorizon.MONTHS.value,
    }
    
    response: requests.Response = requests.post(f"{BASE_URL}/api/risks/", json=risk_data)
    risk: dict[str, Any] = response.json()
    risk_id: int = risk["id"]
    
    # Add multiple strong increase signals (should push over 1.0)
    for i in range(3):
        signal_data: dict[str, Any] = {
            "risk_id": risk_id,
            "name": f"Strong Increase {i+1}",
            "direction": SignalDirection.INCREASE.value,
            "strength": SignalStrength.STRONG.value,
        }
        requests.post(f"{BASE_URL}/api/signals/", json=signal_data)
    
    # Recompute - should be clamped to 1.0
    response = requests.post(f"{BASE_URL}/api/risks/{risk_id}/recompute")
    assessment: dict[str, Any] = response.json()
    
    assert assessment["effective_likelihood"] <= 1.0
    assert assessment["effective_likelihood"] == 1.0
    print(f"✓ Upper bound clamped: {assessment['effective_likelihood']}")
    
    # Test lower bound clamping
    risk_data["name"] = "Test Lower Clamp"
    risk_data["base_likelihood"] = 0.1
    
    response = requests.post(f"{BASE_URL}/api/risks/", json=risk_data)
    risk = response.json()
    risk_id = risk["id"]
    
    # Add multiple strong decrease signals (should push below 0.0)
    for i in range(3):
        signal_data = {
            "risk_id": risk_id,
            "name": f"Strong Decrease {i+1}",
            "direction": SignalDirection.DECREASE.value,
            "strength": SignalStrength.STRONG.value,
        }
        requests.post(f"{BASE_URL}/api/signals/", json=signal_data)
    
    # Recompute - should be clamped to 0.0
    response = requests.post(f"{BASE_URL}/api/risks/{risk_id}/recompute")
    assessment = response.json()
    
    assert assessment["effective_likelihood"] >= 0.0
    assert assessment["effective_likelihood"] == 0.0
    print(f"✓ Lower bound clamped: {assessment['effective_likelihood']}")


if __name__ == "__main__":
    print("Starting recompute endpoint tests...\n")
    try:
        test_recompute_single_risk()
        test_recompute_all_risks()
        test_likelihood_modifiers()
        test_likelihood_clamping()
        print("\n✅ All tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        raise
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to API. Make sure the server is running.")
        print("Run: uv run uvicorn api.main:app --reload")
        raise

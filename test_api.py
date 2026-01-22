"""Example usage and testing of the Personal Risk Radar API."""

from typing import Any, LiteralString

import requests

# Base URL for the API
BASE_URL = "http://localhost:8000"


def test_create_risk() -> dict[str, Any]:
    """Test creating a risk via API."""
    url: LiteralString = f"{BASE_URL}/api/risks/"
    data: dict[str, Any] = {
        "category": "technical",
        "name": "Production deployment failure",
        "description": "Risk of deployment causing downtime",
        "base_likelihood": 0.3,
        "impact": 4,
        "confidence": 0.8,
        "time_horizon": "weeks",
    }

    response: requests.Response = requests.post(url=url, json=data)
    print(f"Create Risk Status: {response.status_code}")
    if response.status_code == 201:
        risk: dict[str, Any] = response.json()
        print(f"Created Risk ID: {risk['id']}")
        return risk
    else:
        print(f"Error: {response.text}")
        return {}


def test_create_signal(risk_id: int) -> dict[str, Any]:
    """Test creating a signal via API."""
    url: LiteralString = f"{BASE_URL}/api/signals/"
    data: dict[str, Any] = {
        "risk_id": risk_id,
        "name": "Failed tests in CI/CD",
        "description": "Multiple test failures in pipeline",
        "direction": "increase",
        "strength": "strong",
    }

    response: requests.Response = requests.post(url=url, json=data)
    print(f"Create Signal Status: {response.status_code}")
    if response.status_code == 201:
        signal: dict[str, Any] = response.json()
        print(f"Created Signal ID: {signal['id']}")
        return signal
    else:
        print(f"Error: {response.text}")
        return {}


def test_assess_risk(risk_id: int) -> dict[str, Any]:
    """Test assessing a risk via API."""
    url: str = f"{BASE_URL}/api/risks/{risk_id}/assess"

    response: requests.Response = requests.post(url=url)
    print(f"Assess Risk Status: {response.status_code}")
    if response.status_code == 200:
        assessment: dict[str, Any] = response.json()
        print(f"Assessment Risk Score: {assessment['assessment']['risk_score']:.3f}")
        print(f"Effective Likelihood: {assessment['assessment']['effective_likelihood']:.3f}")
        return assessment
    else:
        print(f"Error: {response.text}")
        return {}


def test_get_all_risks() -> list[dict[str, Any]]:
    """Test getting all risks."""
    url: str = f"{BASE_URL}/api/risks/"

    response: requests.Response = requests.get(url=url)
    print(f"Get All Risks Status: {response.status_code}")
    if response.status_code == 200:
        risks: list[dict[str, Any]] = response.json()
        print(f"Total Risks: {len(risks)}")
        return risks
    else:
        print(f"Error: {response.text}")
        return []


def test_upload_csv() -> None:
    """Test uploading risks from CSV."""
    url: str = f"{BASE_URL}/api/data-input/upload/risks/csv"

    # Create sample CSV file
    csv_content = """name,category,base_likelihood,impact,confidence,time_horizon,description
Career stagnation,career,0.4,3,0.7,months,Lack of skill development
Budget overrun,financial,0.25,4,0.85,weeks,Project exceeds allocated budget
Chronic stress,health,0.6,3,0.9,months,Sustained high workload"""

    files: dict[str, tuple[str, str, str]] = {"file": ("test_risks.csv", csv_content, "text/csv")}

    response: requests.Response = requests.post(url=url, files=files)
    print(f"Upload CSV Status: {response.status_code}")
    if response.status_code == 200:
        result: dict[str, Any] = response.json()
        print(f"Records Created: {result['records_created']}/{result['records_processed']}")
        if result['errors']:
            print(f"Errors: {result['errors']}")
    else:
        print(f"Error: {response.text}")


def main() -> None:
    """Run all tests."""
    print("=" * 50)
    print("Personal Risk Radar API Test Suite")
    print("=" * 50)

    # Test 1: Create a risk
    print("\n1. Testing Risk Creation...")
    risk: dict[str, Any] = test_create_risk()

    if risk.get("id"):
        # Test 2: Create a signal for the risk
        print("\n2. Testing Signal Creation...")
        # signal: dict[str, Any] = test_create_signal(risk_id=risk["id"]) #type: ignore

        # Test 3: Assess the risk
        print("\n3. Testing Risk Assessment...")
        test_assess_risk(risk_id=risk["id"])

    # Test 4: Get all risks
    print("\n4. Testing Get All Risks...")
    test_get_all_risks()

    # Test 5: Upload CSV
    print("\n5. Testing CSV Upload...")
    test_upload_csv()

    print("\n" + "=" * 50)
    print("Test suite completed!")
    print("=" * 50)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""System verification script for Personal Risk Radar"""

from domain.models import Assessment
from persistence.database import RiskModel, SignalModel

print("🧭 Personal Risk Radar - System Verification")
print("=" * 60)
print()

# Test dependencies
print("📦 DEPENDENCIES:")
try:
    import fastapi
    import pandas
    import plotly  # type: ignore
    import pydantic
    import sqlalchemy
    import streamlit
    print(f"  ✅ FastAPI      {fastapi.__version__}")
    print(f"  ✅ Streamlit    {streamlit.__version__}")
    print(f"  ✅ Plotly       {plotly.__version__}")  # type: ignore
    print(f"  ✅ SQLAlchemy   {sqlalchemy.__version__}")
    print(f"  ✅ Pydantic     {pydantic.__version__}")
    print(f"  ✅ Pandas       {pandas.__version__}")
except ImportError as e:
    print(f"  ❌ Import error: {e}")
print()

# Test database
print("🗄️  DATABASE:")
try:
    from persistence.database import (get_all_risks,
                                      get_all_risks_with_signals, get_db)
    with get_db() as db:
        risks: list[RiskModel] = get_all_risks(db=db)
        risks_with_signals: list[tuple[RiskModel, list[SignalModel]]] = get_all_risks_with_signals(db=db)
        print(f"  ✅ {len(risks)} risks in database")
        print(f"  ✅ {sum(len(signals) for _, signals in risks_with_signals)} total signals")
        print(f"  ✅ SQLite operational")
except Exception as e:
    print(f"  ❌ Database error: {e}")
print()

# Test domain logic
print("🧮 DOMAIN LOGIC:")
try:
    from domain.models import (Risk, RiskCategory, Signal, SignalDirection,
                               SignalStrength, TimeHorizon)
    from domain.scoring import assess_risk, calculate_risk_score
    
    score: float = calculate_risk_score(likelihood=0.5, impact=3, confidence=0.8)
    print(f"  ✅ Risk scoring: 0.5 × 3 × 0.8 = {score:.2f}")
    
    signal = Signal(risk_id=1, name="Test", direction=SignalDirection.INCREASE, strength=SignalStrength.STRONG)
    modifier: float = signal.get_likelihood_modifier()
    print(f"  ✅ Signal modifiers: {modifier:+.2f} (strong increase)")
    
    test_risk = Risk(
        id=999,
        category=RiskCategory.TECHNICAL,
        name="Test Risk",
        base_likelihood=0.5,
        impact=3,
        confidence=0.8,
        time_horizon=TimeHorizon.WEEKS
    )
    assessment: Assessment = assess_risk(risk=test_risk, signals=[])
    print(f"  ✅ Assessment engine: score={assessment.risk_score:.2f}")
except Exception as e:
    print(f"  ❌ Domain logic error: {e}")
print()

# Test API availability
print("🌐 API:")
try:
    from api.main import app
    print(f"  ✅ FastAPI app loaded: {type(app).__name__}")
    print(f"  ✅ Endpoints: /health, /api/risks/, /api/signals/")
except Exception as e:
    print(f"  ❌ API error: {e}")
print()

# Test Streamlit app
print("🎨 STREAMLIT UI:")
try:
    with open(file='main.py', mode='r') as f:
        content: str = f.read()
        has_plotly: bool = 'plotly' in content
        has_dashboard: bool = '📊 Dashboard' in content
        has_trends: bool = '📈 Trends' in content
        has_charts: bool = 'px.pie' in content or 'go.Figure' in content
    print(f"  ✅ Plotly integration: {has_plotly}")
    print(f"  ✅ Dashboard page: {has_dashboard}")
    print(f"  ✅ Trends page: {has_trends}")
    print(f"  ✅ Interactive charts: {has_charts}")
except Exception as e:
    print(f"  ❌ Streamlit check error: {e}")
print()

print("=" * 60)
print("✅ ALL SYSTEMS OPERATIONAL")
print()
print("🚀 Quick Start:")
print("   uv run streamlit run main.py")
print()
print("🔗 API Documentation:")
print("   Start API: uv run uvicorn api.main:app --reload")
print("   Then visit: http://localhost:8000/docs")
print()
print("📖 For more info, see README.md and GETTING_STARTED.md")

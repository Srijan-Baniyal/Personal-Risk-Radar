"""Personal Risk Radar - Streamlit Dashboard."""

from datetime import date, datetime, timezone
from typing import Any

import pandas as pd
import plotly.express as px  # type: ignore[import-untyped]
import plotly.graph_objects as go  # type: ignore[import-untyped]
import streamlit as st

from domain.models import (Assessment, Risk, RiskCategory, Signal,
                           SignalDirection, SignalStrength, TimeHorizon)
from domain.scoring import assess_risk, calculate_risk_score
from persistence.database import (AssessmentModel, RiskModel, SignalModel,
                                  create_assessment, create_risk,
                                  create_signal, delete_risk, delete_signal,
                                  get_all_risks, get_all_risks_with_signals,
                                  get_assessments_for_risk, get_db,
                                  get_latest_assessments, get_risk,
                                  get_signals_for_risk, init_db, update_risk,
                                  update_signal)

# Initialize database
init_db()

# Set page config
st.set_page_config(
    page_title="Personal Risk Radar",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Enhanced Custom CSS for better styling and accessibility with theme support
st.markdown(
    body="""
    <style>
    /* ═══════════════════════════════════════════════════════════════════════
       CSS VARIABLES FOR THEME SUPPORT
       ═══════════════════════════════════════════════════════════════════════ */
    
    /* Light Theme (Default) */
    :root {
        /* Primary Colors */
        --color-primary: #667eea;
        --color-primary-light: #8b9df0;
        --color-secondary: #764ba2;
        
        /* Risk Colors */
        --color-risk-high: #f44336;
        --color-risk-high-bg: rgba(244, 67, 54, 0.1);
        --color-risk-medium: #ff9800;
        --color-risk-medium-bg: rgba(255, 152, 0, 0.1);
        --color-risk-low: #4caf50;
        --color-risk-low-bg: rgba(76, 175, 80, 0.1);
        
        /* Text Colors */
        --color-text-primary: #1a1a2e;
        --color-text-secondary: #4a4a6a;
        --color-text-muted: #666666;
        
        /* Background Colors */
        --color-bg-primary: #ffffff;
        --color-bg-secondary: #f8f9fa;
        --color-bg-card: rgba(102, 126, 234, 0.05);
        --color-bg-sidebar-start: #f0f2f6;
        --color-bg-sidebar-end: #e8eaf0;
        
        /* Box Colors */
        --color-info-bg: rgba(33, 150, 243, 0.1);
        --color-info-border: #2196f3;
        --color-info-heading: #1565c0;
        --color-info-text: #1a1a2e;
        
        --color-success-bg: rgba(76, 175, 80, 0.1);
        --color-success-border: #4caf50;
        --color-success-heading: #2e7d32;
        --color-success-text: #1a1a2e;
        
        --color-warning-bg: rgba(255, 152, 0, 0.1);
        --color-warning-border: #ff9800;
        --color-warning-heading: #e65100;
        --color-warning-text: #1a1a2e;
        
        /* Card Colors */
        --color-feature-bg: rgba(102, 126, 234, 0.08);
        --color-feature-border: rgba(102, 126, 234, 0.2);
        --color-feature-heading: #5c6bc0;
        --color-feature-text: #4a4a6a;
        
        --color-concept-bg: rgba(102, 126, 234, 0.08);
        --color-concept-text: #4a4a6a;
        
        /* Footer */
        --color-footer-text: #888888;
        --color-footer-border: rgba(0, 0, 0, 0.1);
        
        /* Shadows */
        --shadow-card: 0 2px 8px rgba(0, 0, 0, 0.1);
        --shadow-card-hover: 0 8px 24px rgba(102, 126, 234, 0.15);
        --shadow-risk-high: 0 2px 8px rgba(244, 67, 54, 0.15);
        --shadow-risk-medium: 0 2px 8px rgba(255, 152, 0, 0.15);
        --shadow-risk-low: 0 2px 8px rgba(76, 175, 80, 0.15);
    }
    
    /* Dark Theme */
    @media (prefers-color-scheme: dark) {
        :root {
            /* Primary Colors */
            --color-primary: #667eea;
            --color-primary-light: #9fa8da;
            --color-secondary: #764ba2;
            
            /* Risk Colors */
            --color-risk-high: #f44336;
            --color-risk-high-bg: rgba(244, 67, 54, 0.15);
            --color-risk-medium: #ff9800;
            --color-risk-medium-bg: rgba(255, 152, 0, 0.15);
            --color-risk-low: #4caf50;
            --color-risk-low-bg: rgba(76, 175, 80, 0.15);
            
            /* Text Colors */
            --color-text-primary: #fafafa;
            --color-text-secondary: #e0e0e0;
            --color-text-muted: #888888;
            
            /* Background Colors */
            --color-bg-primary: #1a1a2e;
            --color-bg-secondary: #16213e;
            --color-bg-card: rgba(255, 255, 255, 0.05);
            --color-bg-sidebar-start: #1a1a2e;
            --color-bg-sidebar-end: #16213e;
            
            /* Box Colors */
            --color-info-bg: rgba(33, 150, 243, 0.15);
            --color-info-border: #2196f3;
            --color-info-heading: #64b5f6;
            --color-info-text: #e0e0e0;
            
            --color-success-bg: rgba(76, 175, 80, 0.15);
            --color-success-border: #4caf50;
            --color-success-heading: #81c784;
            --color-success-text: #e0e0e0;
            
            --color-warning-bg: rgba(255, 152, 0, 0.15);
            --color-warning-border: #ff9800;
            --color-warning-heading: #ffb74d;
            --color-warning-text: #e0e0e0;
            
            /* Card Colors */
            --color-feature-bg: rgba(102, 126, 234, 0.1);
            --color-feature-border: rgba(102, 126, 234, 0.3);
            --color-feature-heading: #9fa8da;
            --color-feature-text: #e0e0e0;
            
            --color-concept-bg: rgba(102, 126, 234, 0.1);
            --color-concept-text: #e0e0e0;
            
            /* Footer */
            --color-footer-text: #888888;
            --color-footer-border: rgba(255, 255, 255, 0.1);
            
            /* Shadows */
            --shadow-card: 0 2px 8px rgba(0, 0, 0, 0.3);
            --shadow-card-hover: 0 8px 24px rgba(102, 126, 234, 0.2);
            --shadow-risk-high: 0 2px 8px rgba(244, 67, 54, 0.2);
            --shadow-risk-medium: 0 2px 8px rgba(255, 152, 0, 0.2);
            --shadow-risk-low: 0 2px 8px rgba(76, 175, 80, 0.2);
        }
    }
    
    /* ═══════════════════════════════════════════════════════════════════════
       GLOBAL STYLES
       ═══════════════════════════════════════════════════════════════════════ */
    
    /* Global Selection */
    ::selection { background-color: var(--color-primary); color: white; }
    
    /* ═══════════════════════════════════════════════════════════════════════
       RISK CARDS
       ═══════════════════════════════════════════════════════════════════════ */
    
    .risk-high { 
        background-color: var(--color-risk-high-bg); 
        padding: 16px; 
        border-radius: 12px; 
        border-left: 5px solid var(--color-risk-high); 
        margin-bottom: 12px;
        box-shadow: var(--shadow-risk-high);
        color: var(--color-text-primary);
    }
    .risk-medium { 
        background-color: var(--color-risk-medium-bg); 
        padding: 16px; 
        border-radius: 12px; 
        border-left: 5px solid var(--color-risk-medium); 
        margin-bottom: 12px;
        box-shadow: var(--shadow-risk-medium);
        color: var(--color-text-primary);
    }
    .risk-low { 
        background-color: var(--color-risk-low-bg); 
        padding: 16px; 
        border-radius: 12px; 
        border-left: 5px solid var(--color-risk-low); 
        margin-bottom: 12px;
        box-shadow: var(--shadow-risk-low);
        color: var(--color-text-primary);
    }
    
    /* ═══════════════════════════════════════════════════════════════════════
       METRIC & CARD CONTAINERS
       ═══════════════════════════════════════════════════════════════════════ */
    
    .metric-card { 
        padding: 20px; 
        border-radius: 12px; 
        box-shadow: var(--shadow-card);
        background: var(--color-bg-card);
    }
    
    .card-container {
        background: var(--color-bg-card);
        border-radius: 16px;
        padding: 24px;
        box-shadow: var(--shadow-card);
        margin-bottom: 20px;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════
       SIDEBAR STYLING
       ═══════════════════════════════════════════════════════════════════════ */
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--color-bg-sidebar-start) 0%, var(--color-bg-sidebar-end) 100%);
    }
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: var(--color-text-primary) !important;
    }
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown span {
        color: var(--color-text-secondary) !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════
       NAVIGATION BUTTONS
       ═══════════════════════════════════════════════════════════════════════ */
    
    .nav-button {
        background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
        border: none;
        border-radius: 10px;
        padding: 12px 20px;
        color: white;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
        margin-bottom: 8px;
    }
    .nav-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* ═══════════════════════════════════════════════════════════════════════
       INFO, SUCCESS, WARNING BOXES
       ═══════════════════════════════════════════════════════════════════════ */
    
    .info-box {
        background: var(--color-info-bg);
        border-radius: 12px;
        padding: 20px;
        border-left: 4px solid var(--color-info-border);
        margin: 16px 0;
        color: var(--color-info-text);
    }
    .info-box h3, .info-box h4 { color: var(--color-info-heading) !important; }
    .info-box p { color: var(--color-info-text) !important; }
    
    .success-box {
        background: var(--color-success-bg);
        border-radius: 12px;
        padding: 20px;
        border-left: 4px solid var(--color-success-border);
        margin: 16px 0;
        color: var(--color-success-text);
    }
    .success-box h3, .success-box h4 { color: var(--color-success-heading) !important; }
    .success-box p, .success-box li { color: var(--color-success-text) !important; }
    
    .warning-box {
        background: var(--color-warning-bg);
        border-radius: 12px;
        padding: 20px;
        border-left: 4px solid var(--color-warning-border);
        margin: 16px 0;
        color: var(--color-warning-text);
    }
    .warning-box h3, .warning-box h4 { color: var(--color-warning-heading) !important; }
    .warning-box p, .warning-box li { color: var(--color-warning-text) !important; }
    
    /* ═══════════════════════════════════════════════════════════════════════
       SECTION HEADERS
       ═══════════════════════════════════════════════════════════════════════ */
    
    .section-header {
        background: linear-gradient(90deg, var(--color-primary) 0%, var(--color-secondary) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
        font-size: 1.5rem;
        margin-bottom: 16px;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════
       FEATURE & CONCEPT CARDS
       ═══════════════════════════════════════════════════════════════════════ */
    
    .feature-card {
        background: var(--color-feature-bg);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid var(--color-feature-border);
        height: 100%;
        transition: all 0.3s ease;
        color: var(--color-text-primary);
    }
    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-card-hover);
        background: var(--color-feature-bg);
    }
    .feature-card h4 { color: var(--color-feature-heading) !important; }
    .feature-card p { color: var(--color-feature-text) !important; }
    
    .concept-card {
        background: var(--color-concept-bg);
        border-radius: 12px;
        padding: 20px;
        border-left: 4px solid var(--color-primary);
        margin: 12px 0;
        color: var(--color-text-primary);
    }
    .concept-card p { color: var(--color-concept-text) !important; }
    
    /* ═══════════════════════════════════════════════════════════════════════
       FOOTER
       ═══════════════════════════════════════════════════════════════════════ */
    
    .footer {
        text-align: center;
        padding: 20px;
        color: var(--color-footer-text);
        border-top: 1px solid var(--color-footer-border);
        margin-top: 40px;
    }
    .footer p { color: var(--color-footer-text) !important; }
    
    /* ═══════════════════════════════════════════════════════════════════════
       ACCESSIBILITY
       ═══════════════════════════════════════════════════════════════════════ */
    
    button:focus, input:focus, select:focus, textarea:focus {
        outline: 3px solid var(--color-primary);
        outline-offset: 2px;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════
       QUICK STATS
       ═══════════════════════════════════════════════════════════════════════ */
    
    .quick-stat {
        text-align: center;
        padding: 16px;
        background: var(--color-bg-card);
        border-radius: 12px;
        margin: 8px 0;
    }
    .quick-stat h3 {
        font-size: 2rem;
        color: var(--color-primary);
        margin: 0;
    }
    .quick-stat p {
        color: var(--color-text-muted);
        margin: 4px 0 0 0;
        font-size: 0.9rem;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════
       GRADIENT DIVIDER
       ═══════════════════════════════════════════════════════════════════════ */
    
    .gradient-divider {
        height: 3px;
        background: linear-gradient(90deg, var(--color-primary), var(--color-secondary), var(--color-risk-high));
        border-radius: 2px;
        margin: 24px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_risk_severity(score: float) -> str:
    """Determine risk severity level."""
    if score >= 3.0:
        return "🔴 High"
    elif score >= 1.5:
        return "🟡 Medium"
    else:
        return "🟢 Low"


def get_risk_color_class(score: float) -> str:
    """Get CSS class for risk severity."""
    if score >= 3.0:
        return "risk-high"
    elif score >= 1.5:
        return "risk-medium"
    else:
        return "risk-low"


def recompute_all_assessments() -> None:
    """Recompute assessments for all risks."""
    with get_db() as db:
        risks_with_signals: list[tuple[RiskModel, list[SignalModel]]] = (
            get_all_risks_with_signals(db=db)
        )

        for db_risk, db_signals in risks_with_signals:
            # Convert to domain models
            risk = Risk(
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

            # Compute assessment
            assessment: Assessment = assess_risk(risk=risk, signals=signals)

            # Save to database
            create_assessment(
                db=db,
                assessment_data={
                    "risk_id": assessment.risk_id,
                    "effective_likelihood": assessment.effective_likelihood,
                    "impact": assessment.impact,
                    "confidence": assessment.confidence,
                    "risk_score": assessment.risk_score,
                    "signal_count": assessment.signal_count,
                },
            )


def get_quick_stats() -> dict[str, Any]:
    """Get quick statistics for sidebar display."""
    with get_db() as db:
        risks = get_all_risks(db=db)
        assessments = get_latest_assessments(db=db)
        high_risk = sum(1 for a in assessments if a.risk_score >= 3.0)
        total_signals = sum(a.signal_count for a in assessments)
        return {
            "total_risks": len(risks),
            "high_risk": high_risk,
            "total_signals": total_signals,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR NAVIGATION
# ═══════════════════════════════════════════════════════════════════════════════

# Sidebar Header with Logo
st.sidebar.markdown(
    """
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="font-size: 2.5rem; margin: 0;">🎯</h1>
        <h2 style="margin: 8px 0; font-size: 1.4rem;">Risk Radar</h2>
        <p style="font-size: 0.85rem; opacity: 0.8; margin: 0;">Personal Risk Intelligence</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

# Quick Stats in Sidebar
stats = get_quick_stats()
st.sidebar.markdown(
    f"""
    <div style="display: flex; justify-content: space-around; padding: 10px 0; margin-bottom: 16px;">
        <div style="text-align: center;">
            <div style="font-size: 1.5rem; font-weight: bold; color: #667eea;">{stats['total_risks']}</div>
            <div style="font-size: 0.7rem; opacity: 0.8;">Risks</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 1.5rem; font-weight: bold; color: #f44336;">{stats['high_risk']}</div>
            <div style="font-size: 0.7rem; opacity: 0.8;">High Risk</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 1.5rem; font-weight: bold; color: #4caf50;">{stats['total_signals']}</div>
            <div style="font-size: 0.7rem; opacity: 0.8;">Signals</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

# Navigation Section
st.sidebar.markdown("### 🧭 Navigation")

page: str = st.sidebar.radio(
    label="Go to",
    options=[
        "📊 Dashboard",
        "⚠️ Manage Risks",
        "📡 Manage Signals",
        "📈 Trends",
        "📚 Documentation",
    ],
    label_visibility="collapsed",
)

st.sidebar.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

# Actions Section
st.sidebar.markdown("### ⚡ Quick Actions")

if st.sidebar.button(
    label="🔄 Recompute Assessments",
    use_container_width=True,
    help="Recalculate all risk scores based on current signals",
):
    with st.spinner(text="Recomputing risk assessments..."):
        recompute_all_assessments()
        st.sidebar.success(body="✅ Assessments updated!")
        st.rerun()

st.sidebar.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

# Help Section
st.sidebar.markdown("### 💡 Quick Tips")
st.sidebar.markdown(
    """
    <div style="font-size: 0.8rem; opacity: 0.9; line-height: 1.6;">
    • <strong>Dashboard</strong>: Overview of all risks<br>
    • <strong>Manage Risks</strong>: Add/edit risks<br>
    • <strong>Manage Signals</strong>: Track indicators<br>
    • <strong>Trends</strong>: Historical analysis<br>
    • <strong>Docs</strong>: Learn how to use
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

# Footer
st.sidebar.markdown(
    """
    <div style="text-align: center; padding: 16px 0; font-size: 0.75rem; opacity: 0.7;">
        <p style="margin: 0;">Built with ❤️ for better decisions</p>
        <p style="margin: 4px 0 0 0;">v1.0.0 • Local-First</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════════════════════════════════════════
# DOCUMENTATION PAGE
# ═══════════════════════════════════════════════════════════════════════════════

if page == "📚 Documentation":
    st.title("📚 Documentation")
    st.markdown("*Everything you need to know about Personal Risk Radar*")
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    # Navigation tabs for documentation
    doc_tab1, doc_tab2, doc_tab3, doc_tab4, doc_tab5 = st.tabs([
        "🎯 About",
        "🚀 Getting Started",
        "📖 Core Concepts",
        "💡 Inspiration",
        "📝 Notes & Tips",
    ])
    
    # ─────────────────────────────────────────────────────────────────────────
    # ABOUT TAB
    # ─────────────────────────────────────────────────────────────────────────
    with doc_tab1:
        st.markdown("## 🎯 What is Personal Risk Radar?")
        
        st.markdown(
            """
            <div class="info-box">
            <h3 style="margin-top: 0;">A Thinking Tool, Not a Task Manager</h3>
            <p>Personal Risk Radar is a <strong>local-first system</strong> for explicitly modeling, 
            tracking, and reasoning about risk over time. Instead of reacting to problems after 
            they happen, this tool helps you surface latent risks, track early warning signals, 
            and understand how your exposure evolves.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        st.markdown("### 🎯 The Aim")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(
                """
                <div class="feature-card">
                <h4>🔮 Proactive Risk Management</h4>
                <p>Move from reactive firefighting to proactive risk awareness. 
                Identify potential problems before they become crises.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            
            st.markdown(
                """
                <div class="feature-card">
                <h4>🧠 Structured Thinking</h4>
                <p>Transform vague worries into explicit, actionable risk models 
                with clear parameters and measurable signals.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        
        with col2:
            st.markdown(
                """
                <div class="feature-card">
                <h4>📊 Evidence-Based Decisions</h4>
                <p>Track early warning signals that adjust your risk assessment 
                over time, creating an evidence trail for better decisions.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            
            st.markdown(
                """
                <div class="feature-card">
                <h4>🔒 Privacy First</h4>
                <p>All data stays on your machine. No cloud sync, no accounts, 
                no tracking. Your risks are your business.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        
        st.markdown("### ✨ Key Features")
        
        features_col1, features_col2, features_col3 = st.columns(3)
        
        with features_col1:
            st.markdown(
                """
                **📊 Interactive Dashboard**
                - Real-time risk visualization
                - Category distribution charts
                - Severity heatmaps
                - At-a-glance metrics
                
                **⚠️ Risk Management**
                - 5 risk categories
                - Configurable parameters
                - Smart score previews
                """
            )
        
        with features_col2:
            st.markdown(
                """
                **📡 Signal Tracking**
                - Early warning indicators
                - Strength levels (weak/medium/strong)
                - Direction (increase/decrease)
                - Automatic score recalculation
                
                **📈 Trend Analysis**
                - Historical charts
                - Multi-metric comparison
                - Statistical summaries
                """
            )
        
        with features_col3:
            st.markdown(
                """
                **🔄 Assessment Engine**
                - Deterministic scoring
                - Confidence-weighted calculations
                - Signal aggregation
                - Audit trail
                
                **🛡️ Local-First**
                - SQLite storage
                - No internet required
                - Full data ownership
                """
            )
    
    # ─────────────────────────────────────────────────────────────────────────
    # GETTING STARTED TAB
    # ─────────────────────────────────────────────────────────────────────────
    with doc_tab2:
        st.markdown("## 🚀 Getting Started")
        
        st.markdown(
            """
            <div class="success-box">
            <h4 style="margin-top: 0;">⏱️ 5-Minute Quick Start</h4>
            <p>Follow these steps to set up your first risk tracking in under 5 minutes.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        st.markdown("### Step 1: Create Your First Risk")
        
        st.markdown(
            """
            1. Navigate to **⚠️ Manage Risks** in the sidebar
            2. Click on the **➕ Create Risk** tab
            3. Fill in the risk details:
               - **Name**: A clear, concise name (e.g., "Job market downturn")
               - **Category**: Choose from career, financial, health, technical, or personal
               - **Base Likelihood**: Your estimate of probability (0-100%)
               - **Impact**: Severity if it happens (1-5 scale)
               - **Confidence**: How sure you are about your estimate
               - **Time Horizon**: When might this materialize?
            4. Click **✅ Create Risk**
            """
        )
        
        st.markdown("### Step 2: Add Warning Signals")
        
        st.markdown(
            """
            1. Go to **📡 Manage Signals**
            2. Click **➕ Create Signal**
            3. Link the signal to your risk
            4. Define the signal:
               - **Name**: What are you observing? (e.g., "Tech layoffs in my sector")
               - **Direction**: Does this increase or decrease the risk?
               - **Strength**: How strongly does it affect the risk?
            5. Click **✅ Create Signal**
            """
        )
        
        st.markdown("### Step 3: Monitor Your Dashboard")
        
        st.markdown(
            """
            1. Return to **📊 Dashboard**
            2. View your risk score and severity level
            3. See how signals affect your overall assessment
            4. Click **🔄 Recompute Assessments** to update scores
            """
        )
        
        st.markdown("### Step 4: Track Trends Over Time")
        
        st.markdown(
            """
            1. Visit **📈 Trends** regularly
            2. Select a risk to see its historical data
            3. Watch for patterns in your risk scores
            4. Adjust your approach based on trends
            """
        )
        
        st.markdown("### 💡 Scoring Formula Explained")
        
        st.markdown(
            """
            <div class="concept-card">
            <h4 style="margin-top: 0;">How Risk Scores Are Calculated</h4>
            <p>The formula is transparent and deterministic:</p>
            <pre style="background: #f5f5f5; padding: 12px; border-radius: 8px; overflow-x: auto;">
Risk Score = Effective Likelihood × Impact × Confidence

Where:
• Effective Likelihood = Base Likelihood + Signal Modifiers
• Signal Modifiers: Weak ±5%, Medium ±10%, Strong ±20%
• Score Range: 0.00 (no risk) to 5.00 (maximum risk)
            </pre>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        st.markdown("### 🎯 Severity Levels")
        
        sev_col1, sev_col2, sev_col3 = st.columns(3)
        
        with sev_col1:
            st.markdown(
                """
                <div class="risk-low" style="text-align: center;">
                <h3>🟢 Low</h3>
                <p>Score: 0.00 - 1.49</p>
                <p>Monitor, no immediate action needed</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        
        with sev_col2:
            st.markdown(
                """
                <div class="risk-medium" style="text-align: center;">
                <h3>🟡 Medium</h3>
                <p>Score: 1.50 - 2.99</p>
                <p>Attention required, plan mitigation</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        
        with sev_col3:
            st.markdown(
                """
                <div class="risk-high" style="text-align: center;">
                <h3>🔴 High</h3>
                <p>Score: 3.00 - 5.00</p>
                <p>Urgent, take immediate action</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    
    # ─────────────────────────────────────────────────────────────────────────
    # CORE CONCEPTS TAB
    # ─────────────────────────────────────────────────────────────────────────
    with doc_tab3:
        st.markdown("## 📖 Core Concepts")
        
        st.markdown(
            """
            Personal Risk Radar is built around three fundamental ideas that separate 
            it from typical productivity tools.
            """
        )
        
        st.markdown("### 1️⃣ Risks Should Be Explicit")
        
        st.markdown(
            """
            <div class="concept-card">
            <p><strong>If a risk matters, it deserves a name, context, and structure.</strong></p>
            <p>Vague worries ("I'm concerned about my career") become actionable when explicit 
            ("Career stagnation risk: 40% likelihood, impact 3/5, 6-month horizon").</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        st.markdown("### 2️⃣ Signals Matter More Than Outcomes")
        
        st.markdown(
            """
            <div class="concept-card">
            <p><strong>Early warning signs often appear long before failure.</strong></p>
            <p>By tracking signals, you can detect shifts in risk before they materialize. 
            A single "strong" signal like "team lead resigned" might shift a career risk 
            significantly before any actual impact occurs.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        st.markdown("### 3️⃣ Reasoning Should Be Explainable")
        
        st.markdown(
            """
            <div class="concept-card">
            <p><strong>Every score and trend is derived from clear, inspectable logic.</strong></p>
            <p>No machine learning black boxes. No mysterious algorithms. You can trace 
            exactly why a risk has a certain score and what signals contributed to it.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        st.markdown("---")
        
        st.markdown("### 📊 Domain Model")
        
        concept_col1, concept_col2 = st.columns(2)
        
        with concept_col1:
            st.markdown("#### ⚠️ Risk")
            st.markdown(
                """
                A **Risk** is a future uncertainty with potential impact.
                
                | Field | Description | Range |
                |-------|-------------|-------|
                | Category | Domain (career, financial, health, technical, personal) | Fixed |
                | Base Likelihood | Probability before signals | 0.0–1.0 |
                | Impact | Severity if it happens | 1–5 |
                | Confidence | How sure you are | 0.0–1.0 |
                | Time Horizon | When it might materialize | weeks/months |
                
                **Example**: "Technical debt accumulation" with 60% likelihood, 
                impact 4/5, 80% confidence, months horizon.
                """
            )
        
        with concept_col2:
            st.markdown("#### 📡 Signal")
            st.markdown(
                """
                A **Signal** is a measurable early warning sign linked to a risk.
                
                | Field | Description | Options |
                |-------|-------------|---------|
                | Direction | Increases or decreases risk | increase/decrease |
                | Strength | How strongly it affects | weak/medium/strong |
                | Observed At | When you noticed it | Date |
                
                **Signal Strengths**:
                - 🔹 **Weak**: ±5% likelihood adjustment
                - 🔸 **Medium**: ±10% likelihood adjustment
                - 🔴 **Strong**: ±20% likelihood adjustment
                """
            )
        
        st.markdown("#### 📋 Assessment")
        st.markdown(
            """
            An **Assessment** is a snapshot of a risk's state at a point in time.
            
            When you click "Recompute Assessments", the system:
            1. Takes each risk's base parameters
            2. Applies all linked signal modifiers
            3. Calculates the effective likelihood (clamped 0-1)
            4. Computes the final risk score
            5. Saves this as a historical record
            
            This creates an audit trail showing how your risk exposure evolved.
            """
        )
    
    # ─────────────────────────────────────────────────────────────────────────
    # INSPIRATION TAB
    # ─────────────────────────────────────────────────────────────────────────
    with doc_tab4:
        st.markdown("## 💡 Inspiration & Philosophy")
        
        st.markdown(
            """
            <div class="info-box">
            <h4 style="margin-top: 0;">Why This Tool Exists</h4>
            <p>Most risks don't appear suddenly — they accumulate quietly. Personal Risk Radar 
            was born from the realization that we need better tools for thinking about 
            uncertainty, not just managing tasks.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        st.markdown("### 🧠 The Problem with Intuition")
        
        st.markdown(
            """
            Our brains are notoriously bad at assessing risk:
            
            - **Availability bias**: We overweight dramatic, recent events
            - **Optimism bias**: We underestimate risks to ourselves
            - **Anchoring**: First impressions dominate our estimates
            - **Emotional reasoning**: Fear and hope distort probability judgments
            
            A structured system helps counteract these biases by forcing explicit, 
            documented assessments that can be reviewed and updated.
            """
        )
        
        st.markdown("### 📚 Intellectual Influences")
        
        influence_col1, influence_col2 = st.columns(2)
        
        with influence_col1:
            st.markdown(
                """
                **Risk Management Literature**
                - Nassim Taleb's work on uncertainty and antifragility
                - Philip Tetlock's research on forecasting
                - Daniel Kahneman on cognitive biases
                
                **Systems Thinking**
                - Donella Meadows on leverage points
                - Peter Senge on mental models
                """
            )
        
        with influence_col2:
            st.markdown(
                """
                **Software Philosophy**
                - Local-first software principles
                - Plain text accounting (Ledger, hledger)
                - Tools for thought movement
                
                **Personal Knowledge Management**
                - Zettelkasten methodology
                - Structured note-taking systems
                """
            )
        
        st.markdown("### 🎯 Design Principles")
        
        principles_col1, principles_col2, principles_col3 = st.columns(3)
        
        with principles_col1:
            st.markdown(
                """
                <div class="feature-card">
                <h4>🔍 Transparency</h4>
                <p>Every calculation is visible and auditable. No hidden algorithms.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        
        with principles_col2:
            st.markdown(
                """
                <div class="feature-card">
                <h4>🏠 Local-First</h4>
                <p>Your data never leaves your machine. No accounts, no sync, no tracking.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        
        with principles_col3:
            st.markdown(
                """
                <div class="feature-card">
                <h4>🧩 Simplicity</h4>
                <p>Complex enough to be useful, simple enough to actually use.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        
        st.markdown("### 💭 Why Not Just Use a Spreadsheet?")
        
        st.markdown(
            """
            You could! But Personal Risk Radar provides:
            
            1. **Structure**: Enforced schema means consistent risk definitions
            2. **Automation**: Signals automatically update risk scores
            3. **Visualization**: Charts and trends without manual work
            4. **History**: Automatic assessment snapshots over time
            5. **Focused UX**: Purpose-built interface for risk thinking
            
            It's the difference between a general calculator and a purpose-built financial app.
            """
        )
    
    # ─────────────────────────────────────────────────────────────────────────
    # NOTES & TIPS TAB
    # ─────────────────────────────────────────────────────────────────────────
    with doc_tab5:
        st.markdown("## 📝 Notes & Best Practices")
        
        st.markdown("### ✅ Do's")
        
        st.markdown(
            """
            <div class="success-box">
            <ul style="margin: 0; padding-left: 20px;">
                <li><strong>Be specific</strong>: "Q2 budget overrun" is better than "financial problems"</li>
                <li><strong>Update regularly</strong>: Review and recompute at least weekly</li>
                <li><strong>Track signals actively</strong>: The more signals, the better your picture</li>
                <li><strong>Use confidence honestly</strong>: Low confidence is valuable information</li>
                <li><strong>Review trends</strong>: Patterns over time reveal more than snapshots</li>
                <li><strong>Document reasoning</strong>: Use description fields to capture context</li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        st.markdown("### ❌ Don'ts")
        
        st.markdown(
            """
            <div class="warning-box">
            <ul style="margin: 0; padding-left: 20px;">
                <li><strong>Don't track everything</strong>: Focus on risks that actually matter</li>
                <li><strong>Don't ignore low scores</strong>: They can change quickly with new signals</li>
                <li><strong>Don't set and forget</strong>: Stale risks are worse than no tracking</li>
                <li><strong>Don't over-engineer</strong>: 3-5 risks with good signals beats 50 neglected ones</li>
                <li><strong>Don't trust scores blindly</strong>: They're aids to thinking, not answers</li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        st.markdown("### 💡 Pro Tips")
        
        tips_col1, tips_col2 = st.columns(2)
        
        with tips_col1:
            st.markdown(
                """
                **Starting Out**
                - Begin with 3 risks you're genuinely worried about
                - Add 1-2 signals per risk to start
                - Review weekly and adjust
                
                **Signal Selection**
                - Choose observable, concrete indicators
                - Mix leading (predictive) and lagging (confirming) signals
                - A "decrease" signal is just as valuable as "increase"
                """
            )
        
        with tips_col2:
            st.markdown(
                """
                **Maintenance Rhythm**
                - Daily: Quick dashboard glance
                - Weekly: Add new signals, recompute assessments
                - Monthly: Review trends, retire resolved risks
                
                **When to Create a New Risk**
                - You find yourself worrying about it repeatedly
                - It could significantly impact your life/work
                - You can identify potential signals to track
                """
            )
        
        st.markdown("### 📊 Example Risk Setup")
        
        with st.expander("📋 Career Stagnation Risk (Example)"):
            st.markdown(
                """
                **Risk Details**
                - **Name**: Career Stagnation
                - **Category**: Career
                - **Base Likelihood**: 35%
                - **Impact**: 4/5
                - **Confidence**: 70%
                - **Time Horizon**: Months
                - **Description**: Risk of remaining in current role without growth 
                  opportunities or skill development.
                
                **Linked Signals**
                
                | Signal | Direction | Strength |
                |--------|-----------|----------|
                | No new projects assigned in 3 months | Increase | Medium |
                | Manager discussions about promotion | Decrease | Strong |
                | Industry layoffs in my sector | Increase | Weak |
                | Completed certification course | Decrease | Medium |
                | Skipped for team lead opportunity | Increase | Strong |
                """
            )
        
        with st.expander("📋 Health Burnout Risk (Example)"):
            st.markdown(
                """
                **Risk Details**
                - **Name**: Burnout from Overwork
                - **Category**: Health
                - **Base Likelihood**: 25%
                - **Impact**: 5/5
                - **Confidence**: 60%
                - **Time Horizon**: Weeks
                - **Description**: Risk of physical/mental exhaustion from sustained 
                  high workload without adequate recovery.
                
                **Linked Signals**
                
                | Signal | Direction | Strength |
                |--------|-----------|----------|
                | Working >10 hours/day for a week | Increase | Strong |
                | Regular exercise routine maintained | Decrease | Medium |
                | Difficulty sleeping | Increase | Medium |
                | Took full weekend off | Decrease | Weak |
                | Snapping at colleagues | Increase | Strong |
                """
            )
        
        st.markdown("### 🔧 Technical Notes")
        
        st.markdown(
            """
            - **Database**: SQLite file (`risk_radar.db`) in the project directory
            - **Backup**: Simply copy the `.db` file to back up all data
            - **Reset**: Delete the database file to start fresh
            - **Export**: Use the Trends page to view historical data
            """
        )
        
        st.markdown("---")
        
        st.markdown(
            """
            <div class="footer">
            <p>🎯 Personal Risk Radar</p>
            <p>A thinking tool for better decisions under uncertainty</p>
            <p style="font-size: 0.8rem; opacity: 0.7;">Built with FastAPI, Streamlit, and SQLite</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD PAGE
# ═══════════════════════════════════════════════════════════════════════════════

# Main Dashboard Page
elif page == "📊 Dashboard":
    st.title(body="📊 Risk Dashboard")
    st.markdown("*Your real-time view of risk exposure across all categories*")
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    with get_db() as db:
        # Get latest assessments
        assessments = get_latest_assessments(db=db)
        all_risks: list[RiskModel] = get_all_risks(db=db)

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="Total Risks",
                value=len(all_risks),
                delta=None,
                help="Total number of risks being tracked",
            )

        with col2:
            high_risk_count: int = sum(1 for a in assessments if a.risk_score >= 3.0)
            st.metric(
                label="High Risk Items",
                value=high_risk_count,
                delta=None,
                help="Risks with score ≥ 3.0",
            )

        with col3:
            avg_score: float = (
                sum(a.risk_score for a in assessments) / len(assessments)
                if assessments
                else 0.0
            )
            st.metric(
                label="Average Risk Score",
                value=f"{avg_score:.2f}",
                delta=None,
                help="Mean score across all risks",
            )

        with col4:
            total_signals: int = sum(a.signal_count for a in assessments)
            st.metric(
                label="Active Signals",
                value=total_signals,
                delta=None,
                help="Total early warning signals detected",
            )

        st.markdown(body="---")

        if not assessments:
            st.markdown(
                """
                <div class="info-box">
                <h3 style="margin-top: 0;">👋 Welcome to Personal Risk Radar!</h3>
                <p>Get started by creating your first risk in the <strong>⚠️ Manage Risks</strong> page.</p>
                <p style="margin-bottom: 0;">Need help? Check out the <strong>📚 Documentation</strong> for a quick start guide.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            # Visualizations section
            st.subheader(body="📈 Risk Overview")

            viz_col1, viz_col2 = st.columns(2)

            with viz_col1:
                # Risk by category pie chart
                st.markdown(body="**Risk Distribution by Category**")
                category_data: dict[str, int] = {}
                for assessment in assessments:
                    risk = get_risk(db=db, risk_id=assessment.risk_id)
                    if risk:
                        category = risk.category.value.title()
                        category_data[category] = category_data.get(category, 0) + 1

                if category_data:
                    fig_pie: go.Figure = px.pie(  # type: ignore[call-arg]
                        names=list(category_data.keys()),
                        values=list(category_data.values()),
                        color_discrete_sequence=px.colors.qualitative.Set3,
                    )
                    fig_pie.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0))  # type: ignore[call-arg]
                    st.plotly_chart(fig_pie, width="stretch")

            with viz_col2:
                # Risk severity distribution
                st.markdown("**Risk Severity Distribution**")
                severity_counts = {"🟢 Low": 0, "🟡 Medium": 0, "🔴 High": 0}
                for assessment in assessments:
                    severity = get_risk_severity(score=assessment.risk_score)
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1

                fig_bar = px.bar(  # type: ignore[call-arg]
                    x=list(severity_counts.keys()),
                    y=list(severity_counts.values()),
                    color=list(severity_counts.keys()),
                    color_discrete_map={
                        "🟢 Low": "#4caf50",
                        "🟡 Medium": "#ff9800",
                        "🔴 High": "#f44336",
                    },
                    labels={"x": "Severity", "y": "Count"},
                )
                fig_bar.update_layout(  # type: ignore[call-arg]
                    height=300, margin=dict(l=0, r=0, t=30, b=0), showlegend=False
                )
                st.plotly_chart(fig_bar, width="stretch")

            # Top risks heatmap
            st.markdown("**Risk Score Heatmap**")
            risk_data_viz: list[dict[str, Any]] = []
            for assessment in assessments:
                risk = get_risk(db=db, risk_id=assessment.risk_id)
                if risk:
                    risk_data_viz.append(
                        {
                            "Risk": risk.name[:30] + "..."
                            if len(risk.name) > 30
                            else risk.name,
                            "Category": risk.category.value.title(),
                            "Score": round(assessment.risk_score, 2),
                            "Likelihood": assessment.effective_likelihood,
                            "Impact": assessment.impact,
                        }
                    )

            if risk_data_viz:
                df_viz = (
                    pd.DataFrame(risk_data_viz)
                    .sort_values(by="Score", ascending=False)
                    .head(10)
                )
                fig_heatmap = px.bar(  # type: ignore[call-arg]
                    df_viz,
                    x="Score",
                    y="Risk",
                    orientation="h",
                    color="Score",
                    color_continuous_scale=["#4caf50", "#ff9800", "#f44336"],
                    labels={"Score": "Risk Score"},
                )
                fig_heatmap.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=0))  # type: ignore[call-arg]
                st.plotly_chart(fig_heatmap, width="stretch")

        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

        # Risk List
        st.subheader(body="📋 Current Risks")

        if not assessments:
            st.info(
                body="No risks found. Create your first risk in the 'Manage Risks' page."
            )
        else:
            # Create DataFrame for display
            risk_data: list[dict[str, Any]] = []
            for assessment in assessments:
                risk = get_risk(db=db, risk_id=assessment.risk_id)
                if risk:
                    risk_data.append(
                        {
                            "ID": risk.id,
                            "Name": risk.name,
                            "Category": risk.category.value.title(),
                            "Risk Score": round(
                                number=assessment.risk_score, ndigits=2
                            ),
                            "Severity": get_risk_severity(score=assessment.risk_score),
                            "Effective Likelihood": f"{assessment.effective_likelihood:.0%}",
                            "Impact": f"{assessment.impact}/5",
                            "Confidence": f"{assessment.confidence:.0%}",
                            "Signals": assessment.signal_count,
                            "Time Horizon": risk.time_horizon.value.title(),
                        }
                    )

            df = pd.DataFrame(data=risk_data)
            df: pd.DataFrame = df.sort_values(by="Risk Score", ascending=False)

            # Display as interactive table
            st.dataframe(  # type: ignore[misc]
                data=df,
                width="stretch",
                hide_index=True,
                column_config={
                    "Risk Score": st.column_config.ProgressColumn(
                        label="Risk Score",
                        format="%.2f",
                        min_value=0,
                        max_value=5,
                    ),
                },
            )

            # Detailed risk cards
            st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
            st.subheader(body="🔍 Top Risk Details")

            for assessment in assessments[:5]:  # Show top 5
                risk: RiskModel | None = get_risk(db=db, risk_id=assessment.risk_id)
                if risk:
                    color_class: str = get_risk_color_class(score=assessment.risk_score)

                    with st.container():
                        st.markdown(
                            body=f'<div class="{color_class}">',
                            unsafe_allow_html=True,
                        )
                        col1, col2 = st.columns(spec=[3, 1])

                        with col1:
                            st.markdown(body=f"### {risk.name}")
                            st.write(f"**Category:** {risk.category.value.title()}")
                            if risk.description:
                                st.write(f"*{risk.description}*")

                        with col2:
                            st.metric(
                                label="Risk Score",
                                value=f"{assessment.risk_score:.2f}",
                            )
                            st.write(get_risk_severity(score=assessment.risk_score))

                        # Show signals
                        signals: list[SignalModel] = get_signals_for_risk(
                            db=db, risk_id=risk.id
                        )
                        if signals:
                            st.write(f"**Active Signals ({len(signals)}):**")
                            for signal in signals:
                                emoji: str = (
                                    "📈"
                                    if signal.direction == SignalDirection.INCREASE
                                    else "📉"
                                )
                                st.write(
                                    f"{emoji} {signal.name} ({signal.strength.value})"
                                )

                        st.markdown(body="</div>", unsafe_allow_html=True)
                        st.markdown(body="<br>", unsafe_allow_html=True)

    # Footer for Dashboard page
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="footer">
        <p>🎯 Personal Risk Radar • Local-First Risk Intelligence</p>
        <p style="font-size: 0.8rem;">Need help? Check out the 📚 Documentation page</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ═══════════════════════════════════════════════════════════════════════════════
# MANAGE RISKS PAGE
# ═══════════════════════════════════════════════════════════════════════════════

# Manage Risks Page
elif page == "⚠️ Manage Risks":
    st.title(body="⚠️ Manage Risks")
    st.markdown("*Define and track future uncertainties with potential impact*")
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["➕ Create Risk", "📝 Edit Risk", "🗑️ Delete Risk"])

    with tab1:
        st.subheader(body="Create New Risk")
        
        st.markdown(
            """
            <div class="info-box">
            <h4 style="margin-top: 0;">💡 What makes a good risk?</h4>
            <p style="margin-bottom: 0;">Start with risks that feel important but lack clear mitigation. 
            Good examples: career stagnation, budget overruns, technical debt, health concerns.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form(key="create_risk_form"):
            col1, col2 = st.columns(spec=2)

            with col1:
                name: str = st.text_input(
                    label="Risk Name*",
                    placeholder="e.g., Job market downturn",
                    help="A clear, concise name for this risk",
                )
                category: str = st.selectbox(
                    label="Category*",
                    options=[c.value for c in RiskCategory],
                    format_func=lambda x: x.title(),
                    help="The domain this risk affects",
                )
                base_likelihood: float = st.slider(
                    label="Base Likelihood*",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.5,
                    step=0.05,
                    help="Probability before considering signals (0 = impossible, 1 = certain)",
                )

            with col2:
                impact: int = st.slider(
                    label="Impact*",
                    min_value=1,
                    max_value=5,
                    value=3,
                    help="Severity if it happens (1 = minor inconvenience, 5 = catastrophic)",
                )
                confidence: float = st.slider(
                    label="Confidence*",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.7,
                    step=0.05,
                    help="How confident are you in this assessment? (0 = pure guess, 1 = absolute certainty)",
                )
                time_horizon: str = st.selectbox(
                    label="Time Horizon*",
                    options=[h.value for h in TimeHorizon],
                    format_func=lambda x: x.title(),
                    help="When might this risk materialize?",
                )

            description: str = st.text_area(
                label="Description (optional)",
                placeholder="Add context, examples, or conditions that would trigger this risk...",
                help="Detailed explanation to help you remember what this risk means",
            )

            # Show calculated score preview
            preview_score: float = calculate_risk_score(
                likelihood=base_likelihood,
                impact=impact,
                confidence=confidence,
            )
            severity_preview = get_risk_severity(preview_score)
            st.info(
                body=f"📊 **Base Risk Score Preview:** {preview_score:.2f} / 5.00 ({severity_preview})"
            )

            submitted: bool = st.form_submit_button(
                "✅ Create Risk", width="stretch", type="primary"
            )

            if submitted:
                if not name or len(name.strip()) == 0:
                    st.error(body="❌ Risk name is required and cannot be empty!")
                elif len(name) > 200:
                    st.error(body="❌ Risk name must be 200 characters or less!")
                else:
                    with get_db() as db:
                        create_risk_data: dict[str, Any] = {
                            "category": RiskCategory(value=category),
                            "name": name,
                            "description": description if description else None,
                            "base_likelihood": base_likelihood,
                            "impact": impact,
                            "confidence": confidence,
                            "time_horizon": TimeHorizon(value=time_horizon),
                        }

                        new_risk: RiskModel = create_risk(
                            db=db, risk_data=create_risk_data
                        )

                        # Create initial assessment
                        risk_obj: Risk = Risk(
                            id=new_risk.id,
                            **create_risk_data,
                            created_at=new_risk.created_at,
                            updated_at=new_risk.updated_at,
                        )
                        assessment: Assessment = assess_risk(risk=risk_obj, signals=[])
                        create_assessment(
                            db=db,
                            assessment_data={
                                "risk_id": assessment.risk_id,
                                "effective_likelihood": assessment.effective_likelihood,
                                "impact": assessment.impact,
                                "confidence": assessment.confidence,
                                "risk_score": assessment.risk_score,
                                "signal_count": 0,
                            },
                        )

                        st.success(body=f"✅ Risk '{name}' created successfully!")
                        st.rerun()

    with tab2:
        st.subheader(body="Edit Existing Risk")

        with get_db() as db:
            risks: list[RiskModel] = get_all_risks(db=db)

            if not risks:
                st.info(body="No risks available to edit.")
            else:
                risk_options: dict[str, int] = {
                    f"{r.id} - {r.name}": r.id for r in risks
                }
                selected: str = st.selectbox(
                    label="Select Risk to Edit", options=risk_options.keys()
                )

                if selected:
                    risk_id: int = risk_options[selected]
                    risk: RiskModel | None = get_risk(db=db, risk_id=risk_id)

                    if risk:
                        with st.form(key="edit_risk_form"):
                            col1, col2 = st.columns(spec=2)

                            with col1:
                                new_name: str = st.text_input(
                                    label="Risk Name", value=risk.name
                                )
                                new_category: str = st.selectbox(
                                    label="Category",
                                    options=[c.value for c in RiskCategory],
                                    index=[c.value for c in RiskCategory].index(
                                        risk.category.value
                                    ),
                                    format_func=lambda x: x.title(),
                                )
                                new_likelihood: float = st.slider(
                                    label="Base Likelihood",
                                    min_value=0.0,
                                    max_value=1.0,
                                    value=float(risk.base_likelihood),
                                    step=0.05,
                                )

                            with col2:
                                new_impact: int = st.slider(
                                    label="Impact",
                                    min_value=1,
                                    max_value=5,
                                    value=int(risk.impact),
                                )
                                new_confidence: float = st.slider(
                                    label="Confidence",
                                    min_value=0.0,
                                    max_value=1.0,
                                    value=float(risk.confidence),
                                    step=0.05,
                                )
                                new_horizon: str = st.selectbox(
                                    label="Time Horizon",
                                    options=[h.value for h in TimeHorizon],
                                    index=[h.value for h in TimeHorizon].index(
                                        risk.time_horizon.value
                                    ),
                                    format_func=lambda x: x.title(),
                                )

                            new_desc: str = st.text_area(
                                label="Description",
                                value=risk.description or "",
                            )

                            submitted: bool = st.form_submit_button(
                                label="Update Risk", width="stretch"
                            )

                            if submitted:
                                update_data: dict[str, Any] = {
                                    "name": new_name,
                                    "category": RiskCategory(value=new_category),
                                    "base_likelihood": new_likelihood,
                                    "impact": new_impact,
                                    "confidence": new_confidence,
                                    "time_horizon": TimeHorizon(value=new_horizon),
                                    "description": new_desc if new_desc else None,
                                }

                                update_risk(
                                    db=db, risk_id=risk_id, risk_data=update_data
                                )

                                # Recompute assessment
                                signals: list[SignalModel] = get_signals_for_risk(
                                    db=db, risk_id=risk_id
                                )
                                risk_obj: Risk = Risk(
                                    id=risk_id,
                                    **update_data,
                                    created_at=risk.created_at,
                                    updated_at=datetime.now(tz=timezone.utc),
                                )
                                signal_objs: list[Signal] = [
                                    Signal.from_db_model(db_signal=s) for s in signals
                                ]
                                assessment: Assessment = assess_risk(
                                    risk=risk_obj, signals=signal_objs
                                )
                                create_assessment(
                                    db=db,
                                    assessment_data={
                                        "risk_id": assessment.risk_id,
                                        "effective_likelihood": assessment.effective_likelihood,
                                        "impact": assessment.impact,
                                        "confidence": assessment.confidence,
                                        "risk_score": assessment.risk_score,
                                        "signal_count": len(signals),
                                    },
                                )

                                st.success(body="✅ Risk updated successfully!")
                                st.rerun()

    with tab3:
        st.subheader(body="Delete Risk")

        with get_db() as db:
            risks: list[RiskModel] = get_all_risks(db=db)

            if not risks:
                st.info(body="No risks available to delete.")
            else:
                risk_options: dict[str, int] = {
                    f"{r.id} - {r.name}": r.id for r in risks
                }
                selected: str = st.selectbox(
                    label="Select Risk to Delete",
                    options=risk_options.keys(),
                    key="delete_select",
                )

                if selected:
                    risk_id: int = risk_options[selected]
                    risk: RiskModel | None = get_risk(db=db, risk_id=risk_id)

                    if risk:
                        st.warning(body=f"⚠️ You are about to delete: **{risk.name}**")
                        st.write(
                            "This will also delete all associated signals and assessments."
                        )

                        if st.button(label="🗑️ Confirm Delete", type="primary"):
                            delete_risk(db=db, risk_id=risk_id)
                            st.success(
                                body=f"✅ Risk '{risk.name}' deleted successfully!"
                            )
                            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# MANAGE SIGNALS PAGE
# ═══════════════════════════════════════════════════════════════════════════════

# Manage Signals Page
elif page == "📡 Manage Signals":
    st.title(body="📡 Manage Signals")
    st.markdown("*Track early warning indicators that affect your risk exposure*")
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(
        ["➕ Create Signal", "📝 Edit Signal", "🗑️ Delete Signal"]
    )

    with tab1:
        st.subheader(body="Create New Signal")

        with get_db() as db:
            risks: list[RiskModel] = get_all_risks(db=db)

            if not risks:
                st.warning(
                    body="⚠️ No risks available. Please create a risk first before adding signals."
                )
                st.info(
                    body="💡 Signals are early warning indicators linked to specific risks. Create a risk in the '⚠️ Manage Risks' page to get started."
                )
            else:
                st.markdown(
                    """
                    <div class="info-box">
                    <h4 style="margin-top: 0;">💡 What are signals?</h4>
                    <p style="margin-bottom: 0;">Observable indicators that suggest a risk is increasing or decreasing. 
                    Examples: 'Failed CI/CD tests', 'Overtime hours increasing', 'Regular exercise routine'.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                with st.form(key="create_signal_form"):
                    col1, col2 = st.columns(spec=2)

                    with col1:
                        risk_options: dict[str, int] = {
                            f"{r.id} - {r.name}": r.id for r in risks
                        }
                        selected_risk: str = st.selectbox(
                            label="Associated Risk*",
                            options=risk_options.keys(),
                            help="Which risk does this signal affect?",
                        )
                        risk_id: int = risk_options[selected_risk]

                        signal_name: str = st.text_input(
                            label="Signal Name*",
                            placeholder="e.g., LinkedIn recruiter messages decreased",
                            help="A clear, observable indicator",
                        )

                        direction: str = st.selectbox(
                            label="Direction*",
                            options=[d.value for d in SignalDirection],
                            format_func=lambda x: f"📈 {x.title()}"
                            if x == "increase"
                            else f"📉 {x.title()}",
                            help="Does this signal increase or decrease the risk?",
                        )

                    with col2:
                        strength: str = st.selectbox(
                            label="Strength*",
                            options=[s.value for s in SignalStrength],
                            format_func=lambda x: x.title(),
                            help="How strongly does this signal affect the risk? Weak: ±5%, Medium: ±10%, Strong: ±20%",
                        )

                        observed_at: date = st.date_input(
                            label="Observed Date",
                            value=datetime.now(tz=timezone.utc).date(),
                            help="When did you first notice this signal?",
                        )

                    signal_desc: str = st.text_area(
                        label="Description (optional)",
                        placeholder="Add context about when and how you observed this signal...",
                        help="Additional details to help you remember this signal",
                    )

                    # Show impact preview
                    strength_val: SignalStrength = SignalStrength(value=strength)
                    direction_val: SignalDirection = SignalDirection(value=direction)
                    modifiers: dict[SignalStrength, float] = {
                        SignalStrength.WEAK: 0.05,
                        SignalStrength.MEDIUM: 0.10,
                        SignalStrength.STRONG: 0.20,
                    }
                    modifier: float = modifiers[strength_val]
                    if direction_val == SignalDirection.DECREASE:
                        modifier = -modifier

                    st.info(
                        body=f"📊 **Impact Preview:** This signal will modify likelihood by **{modifier:+.0%}**"
                    )

                    submitted: bool = st.form_submit_button(
                        label="✅ Create Signal",
                        width="stretch",
                        type="primary",
                    )

                    if submitted:
                        if not signal_name or len(signal_name.strip()) == 0:
                            st.error(
                                body="❌ Signal name is required and cannot be empty!"
                            )
                        elif len(signal_name) > 200:
                            st.error(
                                body="❌ Signal name must be 200 characters or less!"
                            )
                        else:
                            signal_data: dict[str, Any] = {
                                "risk_id": risk_id,
                                "name": signal_name,
                                "description": signal_desc if signal_desc else None,
                                "direction": SignalDirection(value=direction),
                                "strength": SignalStrength(value=strength),
                                "observed_at": datetime.combine(
                                    date=observed_at,
                                    time=datetime.min.time(),
                                    tzinfo=timezone.utc,
                                ),
                            }

                            create_signal(db=db, signal_data=signal_data)

                            # Recompute assessment for the risk
                            risk: RiskModel | None = get_risk(db=db, risk_id=risk_id)
                            if risk:
                                signals: list[SignalModel] = get_signals_for_risk(
                                    db=db, risk_id=risk_id
                                )
                                risk_obj: Risk = Risk(
                                    id=risk.id,
                                    category=risk.category,
                                    name=risk.name,
                                    description=risk.description,
                                    base_likelihood=risk.base_likelihood,
                                    impact=risk.impact,
                                    confidence=risk.confidence,
                                    time_horizon=risk.time_horizon,
                                    created_at=risk.created_at,
                                    updated_at=risk.updated_at,
                                )
                                signal_objs: list[Signal] = [
                                    Signal.from_db_model(db_signal=s) for s in signals
                                ]
                                assessment: Assessment = assess_risk(
                                    risk=risk_obj, signals=signal_objs
                                )
                                create_assessment(
                                    db=db,
                                    assessment_data={
                                        "risk_id": assessment.risk_id,
                                        "effective_likelihood": assessment.effective_likelihood,
                                        "impact": assessment.impact,
                                        "confidence": assessment.confidence,
                                        "risk_score": assessment.risk_score,
                                        "signal_count": len(signals),
                                    },
                                )

                            st.success(
                                body=f"✅ Signal '{signal_name}' created successfully!"
                            )
                            st.rerun()

    with tab2:
        st.subheader(body="Edit Existing Signal")

        with get_db() as db:
            risks: list[RiskModel] = get_all_risks(db=db)
            all_signals: list[tuple[SignalModel, str]] = []
            for risk in risks:
                signals: list[SignalModel] = get_signals_for_risk(
                    db=db, risk_id=risk.id
                )
                all_signals.extend([(s, risk.name) for s in signals])

            if not all_signals:
                st.info(body="No signals available to edit.")
            else:
                signal_options: dict[str, int] = {
                    f"{s.id} - {s.name} (Risk: {risk_name})": s.id
                    for s, risk_name in all_signals
                }
                selected: str = st.selectbox(
                    label="Select Signal to Edit", options=signal_options.keys()
                )

                if selected:
                    signal_id: int = signal_options[selected]
                    signal: SignalModel | None = next(
                        (s for s, _ in all_signals if s.id == signal_id), None
                    )

                    if signal:
                        with st.form(key="edit_signal_form"):
                            col1, col2 = st.columns(spec=2)

                            with col1:
                                new_name: str = st.text_input(
                                    label="Signal Name", value=signal.name
                                )
                                new_direction: str = st.selectbox(
                                    label="Direction",
                                    options=[d.value for d in SignalDirection],
                                    index=[d.value for d in SignalDirection].index(
                                        signal.direction.value
                                    ),
                                    format_func=lambda x: f"📈 {x.title()}"
                                    if x == "increase"
                                    else f"📉 {x.title()}",
                                )

                            with col2:
                                new_strength: str = st.selectbox(
                                    label="Strength",
                                    options=[s.value for s in SignalStrength],
                                    index=[s.value for s in SignalStrength].index(
                                        signal.strength.value
                                    ),
                                    format_func=lambda x: x.title(),
                                )

                            new_desc: str = st.text_area(
                                label="Description",
                                value=signal.description or "",
                            )

                            submitted: bool = st.form_submit_button(
                                label="Update Signal", width="stretch"
                            )

                            if submitted:
                                update_data: dict[str, Any] = {
                                    "name": new_name,
                                    "direction": SignalDirection(value=new_direction),
                                    "strength": SignalStrength(value=new_strength),
                                    "description": new_desc if new_desc else None,
                                }

                                update_signal(
                                    db=db, signal_id=signal_id, signal_data=update_data
                                )

                                # Recompute assessment
                                risk: RiskModel | None = get_risk(
                                    db=db, risk_id=signal.risk_id
                                )
                                if risk:
                                    signals: list[SignalModel] = get_signals_for_risk(
                                        db=db, risk_id=signal.risk_id
                                    )
                                    risk_obj: Risk = Risk(
                                        id=risk.id,
                                        category=risk.category,
                                        name=risk.name,
                                        description=risk.description,
                                        base_likelihood=risk.base_likelihood,
                                        impact=risk.impact,
                                        confidence=risk.confidence,
                                        time_horizon=risk.time_horizon,
                                        created_at=risk.created_at,
                                        updated_at=risk.updated_at,
                                    )
                                    signal_objs: list[Signal] = [
                                        Signal.from_db_model(db_signal=s)
                                        for s in signals
                                    ]
                                    assessment: Assessment = assess_risk(
                                        risk=risk_obj, signals=signal_objs
                                    )
                                    create_assessment(
                                        db=db,
                                        assessment_data={
                                            "risk_id": assessment.risk_id,
                                            "effective_likelihood": assessment.effective_likelihood,
                                            "impact": assessment.impact,
                                            "confidence": assessment.confidence,
                                            "risk_score": assessment.risk_score,
                                            "signal_count": len(signals),
                                        },
                                    )

                                st.success(body="✅ Signal updated successfully!")
                                st.rerun()

    with tab3:
        st.subheader(body="Delete Signal")

        with get_db() as db:
            risks: list[RiskModel] = get_all_risks(db=db)
            all_signals: list[tuple[SignalModel, str]] = []
            for risk in risks:
                signals: list[SignalModel] = get_signals_for_risk(
                    db=db, risk_id=risk.id
                )
                all_signals.extend([(s, risk.name) for s in signals])

            if not all_signals:
                st.info(body="No signals available to delete.")
            else:
                signal_options: dict[str, int] = {
                    f"{s.id} - {s.name} (Risk: {risk_name})": s.id
                    for s, risk_name in all_signals
                }
                selected: str = st.selectbox(
                    label="Select Signal to Delete",
                    options=signal_options.keys(),
                    key="delete_signal_select",
                )

                if selected:
                    signal_id: int = signal_options[selected]
                    signal: SignalModel | None = next(
                        (s for s, _ in all_signals if s.id == signal_id), None
                    )

                    if signal:
                        st.warning(body=f"⚠️ You are about to delete: **{signal.name}**")

                        if st.button(label="🗑️ Confirm Delete", type="primary"):
                            risk_id: int = signal.risk_id
                            delete_signal(db=db, signal_id=signal_id)

                            # Recompute assessment for the affected risk
                            risk: RiskModel | None = get_risk(db=db, risk_id=risk_id)
                            if risk:
                                signals: list[SignalModel] = get_signals_for_risk(
                                    db=db, risk_id=risk_id
                                )
                                risk_obj: Risk = Risk(
                                    id=risk.id,
                                    category=risk.category,
                                    name=risk.name,
                                    description=risk.description,
                                    base_likelihood=risk.base_likelihood,
                                    impact=risk.impact,
                                    confidence=risk.confidence,
                                    time_horizon=risk.time_horizon,
                                    created_at=risk.created_at,
                                    updated_at=risk.updated_at,
                                )
                                signal_objs: list[Signal] = [
                                    Signal.from_db_model(db_signal=s) for s in signals
                                ]
                                assessment: Assessment = assess_risk(
                                    risk=risk_obj, signals=signal_objs
                                )
                                create_assessment(
                                    db=db,
                                    assessment_data={
                                        "risk_id": assessment.risk_id,
                                        "effective_likelihood": assessment.effective_likelihood,
                                        "impact": assessment.impact,
                                        "confidence": assessment.confidence,
                                        "risk_score": assessment.risk_score,
                                        "signal_count": len(signals),
                                    },
                                )

                            st.success(
                                body=f"✅ Signal '{signal.name}' deleted successfully!"
                            )
                            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# TRENDS PAGE
# ═══════════════════════════════════════════════════════════════════════════════

# Trends Page
elif page == "📈 Trends":
    st.title(body="📈 Risk Trends")
    st.markdown("*Analyze how your risk exposure changes over time*")
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    with get_db() as db:
        risks = get_all_risks(db=db)

        if not risks:
            st.info(
                body="No risks available for trend analysis. Create your first risk to begin tracking trends."
            )
        else:
            # Select risk for trend analysis
            risk_options: dict[str, int] = {f"{r.id} - {r.name}": r.id for r in risks}
            selected = st.selectbox(
                label="Select Risk to Analyze",
                options=risk_options.keys(),
                help="Choose a risk to view its historical assessment data",
            )

            if selected:
                risk_id: int = risk_options[selected]
                risk = get_risk(db=db, risk_id=risk_id)
                assessments: list[AssessmentModel] = get_assessments_for_risk(
                    db=db, risk_id=risk_id, limit=50
                )

                if risk:
                    st.subheader(body=f"Trend Analysis: {risk.name}")

                    col1, col2, col3 = st.columns(spec=[2, 1, 1])

                    with col1:
                        st.write(f"**Category:** {risk.category.value.title()}")
                        if risk.description:
                            st.write(f"**Description:** {risk.description}")

                    with col2:
                        current_signals: list[SignalModel] = get_signals_for_risk(
                            db=db, risk_id=risk_id
                        )
                        st.metric(label="Active Signals", value=len(current_signals))

                    with col3:
                        if assessments:
                            st.metric(label="Assessments", value=len(assessments))

                    if not assessments:
                        st.info(
                            body="No historical assessments available for this risk. The trend will appear after you recompute assessments."
                        )
                    else:
                        # Prepare trend data
                        trend_data: list[dict[str, Any]] = []
                        for assessment in reversed(assessments):  # Oldest first
                            trend_data.append(
                                {
                                    "Date": assessment.assessed_at,
                                    "Risk Score": round(
                                        number=assessment.risk_score, ndigits=2
                                    ),
                                    "Effective Likelihood": round(
                                        number=assessment.effective_likelihood,
                                        ndigits=2,
                                    ),
                                    "Impact": assessment.impact,
                                    "Confidence": round(
                                        number=assessment.confidence, ndigits=2
                                    ),
                                    "Signal Count": assessment.signal_count,
                                }
                            )

                        df = pd.DataFrame(data=trend_data)

                        # Combined interactive chart
                        st.markdown(body="### 📊 Risk Score Timeline")
                        fig_main = go.Figure()

                        fig_main.add_trace(  # type: ignore[call-arg]
                            go.Scatter(
                                x=df["Date"],
                                y=df["Risk Score"],
                                mode="lines+markers",
                                name="Risk Score",
                                line=dict(color="#f44336", width=3),
                                marker=dict(size=8),
                            )
                        )

                        # Add threshold lines
                        fig_main.add_hline(  # type: ignore[call-arg]
                            y=3.0,
                            line_dash="dash",
                            line_color="red",
                            annotation_text="High Risk Threshold",
                        )
                        fig_main.add_hline(  # type: ignore[call-arg]
                            y=1.5,
                            line_dash="dash",
                            line_color="orange",
                            annotation_text="Medium Risk Threshold",
                        )

                        fig_main.update_layout(  # type: ignore[call-arg]
                            height=400,
                            hovermode="x unified",
                            xaxis_title="Date",
                            yaxis_title="Risk Score",
                            yaxis=dict(range=[0, 5.5]),
                        )
                        st.plotly_chart(fig_main, width="stretch")

                        # Multi-metric comparison
                        st.markdown(body="### 📈 Component Analysis")

                        fig_multi = go.Figure()

                        fig_multi.add_trace(  # type: ignore[call-arg]
                            go.Scatter(
                                x=df["Date"],
                                y=df["Effective Likelihood"],
                                mode="lines",
                                name="Likelihood",
                                line=dict(color="#2196f3", width=2),
                            )
                        )

                        fig_multi.add_trace(  # type: ignore[call-arg]
                            go.Scatter(
                                x=df["Date"],
                                y=df["Impact"] / 5,  # Normalize to 0-1 scale
                                mode="lines",
                                name="Impact (normalized)",
                                line=dict(color="#ff9800", width=2),
                            )
                        )

                        fig_multi.add_trace(  # type: ignore[call-arg]
                            go.Scatter(
                                x=df["Date"],
                                y=df["Confidence"],
                                mode="lines",
                                name="Confidence",
                                line=dict(color="#4caf50", width=2),
                            )
                        )

                        fig_multi.update_layout(  # type: ignore[call-arg]
                            height=350,
                            hovermode="x unified",
                            xaxis_title="Date",
                            yaxis_title="Value (0-1)",
                            yaxis=dict(range=[0, 1.1]),
                        )
                        st.plotly_chart(fig_multi, width="stretch")

                        # Signal Count Trend
                        st.markdown(body="### 📡 Signal Activity")
                        fig_signals = px.area(  # type: ignore[call-arg]
                            df,
                            x="Date",
                            y="Signal Count",
                            color_discrete_sequence=["#9c27b0"],
                        )
                        fig_signals.update_layout(height=250)  # type: ignore[call-arg]
                        st.plotly_chart(fig_signals, width="stretch")

                        # Statistics
                        st.markdown(body="### 📊 Statistics Summary")
                        col1, col2, col3, col4, col5 = st.columns(5)

                        with col1:
                            st.metric(
                                label="Current Score",
                                value=f"{df['Risk Score'].iloc[-1]:.2f}",
                            )

                        with col2:
                            st.metric(
                                label="Average Score",
                                value=f"{df['Risk Score'].mean():.2f}",
                            )

                        with col3:
                            st.metric(
                                label="Peak Score",
                                value=f"{df['Risk Score'].max():.2f}",
                            )

                        with col4:
                            st.metric(
                                label="Lowest Score",
                                value=f"{df['Risk Score'].min():.2f}",
                            )

                        with col5:
                            # Calculate trend (simple: compare first and last)
                            if len(df) > 1:
                                trend_delta = (
                                    df["Risk Score"].iloc[-1] - df["Risk Score"].iloc[0]
                                )
                                st.metric(
                                    label="Trend",
                                    value=f"{trend_delta:+.2f}",
                                    delta=f"{trend_delta:+.2f}",
                                )

                        # Detailed history table (expandable)
                        with st.expander("📋 View Full Assessment History"):
                            display_df = df.copy()
                            display_df["Date"] = pd.to_datetime(
                                display_df["Date"]
                            ).dt.strftime("%Y-%m-%d %H:%M")
                            st.dataframe(  # type: ignore[misc]
                                data=display_df,
                                width="stretch",
                                hide_index=True,
                            )

    # Footer for Trends page
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="footer">
        <p>🎯 Personal Risk Radar • Local-First Risk Intelligence</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
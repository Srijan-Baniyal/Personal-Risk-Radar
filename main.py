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

# Custom CSS for better styling
st.markdown(
    body="""
    <style>
    .risk-high { background-color: #ffebee; padding: 10px; border-radius: 5px; border-left: 4px solid #f44336; }
    .risk-medium { background-color: #fff3e0; padding: 10px; border-radius: 5px; border-left: 4px solid #ff9800; }
    .risk-low { background-color: #e8f5e9; padding: 10px; border-radius: 5px; border-left: 4px solid #4caf50; }
    .metric-card { padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
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


# Sidebar Navigation
st.sidebar.title(body="🎯 Risk Radar")
page: str = st.sidebar.radio(
    label="Navigate",
    options=["📊 Dashboard", "⚠️ Manage Risks", "📡 Manage Signals", "📈 Trends"],
)

# Sidebar actions
st.sidebar.markdown(body="---")
if st.sidebar.button(label="🔄 Recompute All Assessments", width="stretch"):
    with st.spinner(text="Recomputing risk assessments..."):
        recompute_all_assessments()
        st.sidebar.success(body="✅ Assessments updated!")
        st.rerun()

# Main Dashboard Page
if page == "📊 Dashboard":
    st.title(body="📊 Risk Dashboard")
    st.markdown(body="*Real-time view of your risk exposure across all categories*")

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
            st.info(
                body="👋 Welcome! Get started by creating your first risk in the '⚠️ Manage Risks' page."
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

        st.markdown(body="---")

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
            st.markdown(body="---")
            st.subheader(body="🔍 Risk Details")

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

# Manage Risks Page
elif page == "⚠️ Manage Risks":
    st.title(body="⚠️ Manage Risks")
    st.markdown(body="*Define and track future uncertainties with potential impact*")

    tab1, tab2, tab3 = st.tabs(["➕ Create Risk", "📝 Edit Risk", "🗑️ Delete Risk"])

    with tab1:
        st.subheader(body="Create New Risk")
        st.info(
            "💡 **Tip:** Start with risks that feel important but lack clear mitigation. Good examples: career stagnation, budget overruns, technical debt."
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

# Manage Signals Page
elif page == "📡 Manage Signals":
    st.title(body="📡 Manage Signals")
    st.markdown(body="*Track early warning indicators that increase or decrease risk*")

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
                st.info(
                    "💡 **What are signals?** Observable indicators that suggest a risk is increasing or decreasing. Examples: 'Failed CI/CD tests', 'Overtime hours increasing', 'Regular exercise routine'."
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

# Trends Page
elif page == "📈 Trends":
    st.title(body="📈 Risk Trends")
    st.markdown(body="*Track how your risk exposure changes over time*")

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

# 🧭 Personal Risk Radar

> A local-first system for explicitly modeling, tracking, and reasoning about risk over time.

[![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.53+-red.svg)](https://streamlit.io/)

Instead of reacting to problems after they happen, this tool helps you surface latent risks, track early warning signals, and understand how your exposure evolves across different areas of life or work.

**This is not a task manager, habit tracker, or productivity app. It is a thinking tool.**

---

## 🧠 Core Idea

Most risks don't appear suddenly — they accumulate quietly.

Personal Risk Radar is built around three ideas:

1. **Risks should be explicit** — If a risk matters, it deserves a name, context, and structure.
2. **Signals matter more than outcomes** — Early warning signs often appear long before failure.
3. **Reasoning should be explainable** — Every score and trend is derived from clear, inspectable logic — no black boxes.

---

## ✨ Features

### 📊 Interactive Dashboard

- Real-time risk score visualization
- Category-based risk distribution charts
- Severity heatmaps and trends
- Summary metrics at a glance

### ⚠️ Risk Management

- Define risks across 5 categories (career, financial, health, technical, personal)
- Assign likelihood, impact, confidence, and time horizon
- Full CRUD operations with validation
- Smart form previews showing calculated risk scores

### 📡 Signal Tracking

- Link early warning indicators to specific risks
- Track signal strength (weak/medium/strong) and direction (increase/decrease)
- Automatic risk score recalculation when signals change
- Visual impact preview before saving

### 📈 Trend Analysis

- Interactive time-series charts with Plotly
- Multi-metric comparison (likelihood, impact, confidence)
- Signal activity visualization
- Statistical summaries and trend detection
- Historical assessment data

### 🔄 Assessment Engine

- Deterministic, explainable scoring logic
- Confidence-weighted risk calculations
- Signal modifier aggregation
- Automatic assessment snapshots

---

## 🧩 Core Concepts

### 1. Risk

A future uncertainty with potential impact.

Each risk includes:

| Field           | Description                                    | Range    |
| --------------- | ---------------------------------------------- | -------- |
| Category        | career, financial, health, technical, personal | Fixed    |
| Base likelihood | Probability before signals                     | 0.0–1.0  |
| Impact          | Severity if it happens                         | 1–5      |
| Confidence      | How sure you are                               | 0.0–1.0  |
| Time horizon    | weeks / months                                 | Fixed    |

**Example:** "Career stagnation" with 40% likelihood, impact 3/5, 70% confidence, months horizon.

### 2. Signal

A measurable early warning sign linked to a risk.

Signals:

- **Increase** or **decrease** risk
- Have **strength**: weak (±5%), medium (±10%), strong (±20%)
- Adjust likelihood, not impact
- Are observable and time-stamped

**Examples:**

- "Working >10h/day for 6 days" → Increases health risk (strong)
- "Regular exercise routine" → Decreases health risk (medium)
- "Failed CI/CD tests" → Increases technical risk (strong)

### 3. Assessment

A snapshot produced by recomputing all risks using current signals and scoring logic.

Contains:

- Effective likelihood (base + signal modifiers)
- Final risk score
- Signal count
- Timestamp

---

## 📐 Risk Scoring (Simple & Explainable)

The system intentionally avoids ML or probabilistic black boxes.

**Baseline formula:**

```text
risk_score = likelihood × impact × confidence
```

**Signal modifiers:**

- Weak: ±5% likelihood
- Medium: ±10% likelihood
- Strong: ±20% likelihood

**Example calculation:**

```python
Base likelihood: 0.50 (50%)
Signals:
  + Strong increase: +0.20 → 0.70
  + Medium decrease: -0.10 → 0.60

Impact: 3
Confidence: 0.80

Risk Score = 0.60 × 3 × 0.80 = 1.44
```

This keeps reasoning:

- ✅ Transparent
- ✅ Auditable
- ✅ Easy to refine

---

## 🏗️ Architecture

The project is split into a typed backend and a visual frontend.

```bash
personal_risk_radar/
├── main.py              # Streamlit dashboard entry point
├── setup.sh             # Quick setup script
├── api/                 # FastAPI routes
│   ├── main.py          # API entry point
│   ├── risks.py         # Risk endpoints
│   ├── signals.py       # Signal endpoints
│   └── data_input.py    # Bulk data import
├── domain/              # Core business logic
│   ├── models.py        # Risk, Signal, Assessment (Pydantic)
│   └── scoring.py       # Risk calculation logic
├── persistence/         # Database layer
│   └── database.py      # SQLite ORM with SQLAlchemy
├── scripts/             # Utility scripts
│   ├── load_examples.py # Load sample data
│   └── run.py           # Quick launcher
├── examples/            # Sample CSV data
│   ├── sample_risks.csv
│   └── sample_signals.csv
├── docs/                # Documentation
│   ├── GETTING_STARTED.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   └── screenshots/     # UI screenshots
└── tests/               # Test suite
    ├── test_domain.py   # Unit tests
    ├── test_recompute.py # Integration tests
    ├── test_api.py      # API tests
    └── verify_system.py # System verification
```

### Backend

- **FastAPI** for API boundaries with automatic OpenAPI docs
- **Explicit domain models** with full type hints (Pydantic)
- **SQLite** (local, file-based storage)
- **Deterministic scoring logic** (no ML, no black boxes)
- **SQLAlchemy** for database ORM

### Frontend

- **Streamlit** for rapid, introspective UI
- **Plotly** for interactive visualizations
- Dashboard-driven interaction
- Real-time data updates
- Visual trend analysis

### Tooling

| Tool           | Purpose                              |
| -------------- | ------------------------------------ |
| `uv`           | Dependency and environment management|
| `ruff`         | Linting and formatting               |
| `Type hinting` | Full static typing throughout        |

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.14+** (recommended) or 3.12+
- **[uv](https://docs.astral.sh/uv/)** package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/Srijan-Baniyal/Personal-Risk-Radar.git
cd personal_risk_radar

# Install dependencies with uv
uv sync
```

### Load Example Data (Optional but Recommended)

```bash
# Load sample risks and signals
uv run python scripts/load_examples.py
```

This creates realistic example data:

- 5 sample risks across different categories
- 9 signals affecting various risks
- Initial assessments for all risks

### Running the Application

#### ⚡ Quick Start (Recommended)

```bash
# Launch Streamlit dashboard
uv run streamlit run main.py
```

Open your browser to **[Dashboard View](http://localhost:8501)**

#### Alternative: Using the launcher

```bash
uv run python scripts/run.py
```

#### Option: FastAPI Server Only

```bash
uv run uvicorn api.main:app --reload
```

API will be available at **[Links to the API's](http://localhost:8000)**

- Interactive docs: **[Interactive Docs Links](http://localhost:8000/docs)**
- Alternative docs: **[Alternate Docs Link](http://localhost:8000/redoc)**

#### Development Mode (Both Services)

```bash
# Terminal 1: Start API server
uv run uvicorn api.main:app --reload

# Terminal 2: Start Streamlit dashboard
uv run streamlit run main.py
```

---

## 📖 Usage Guide

### 1. Dashboard Overview

The **📊 Dashboard** page shows:

- Summary metrics (total risks, high-risk items, average score)
- Risk distribution by category (pie chart)
- Risk severity distribution (bar chart)
- Top risks heatmap
- Detailed risk cards with active signals

### 2. Creating a Risk

Navigate to **⚠️ Manage Risks** → **➕ Create Risk**

Fill in the form:

- **Name**: Descriptive title (e.g., "Career stagnation")
- **Category**: Choose from career, financial, health, technical, personal
- **Base Likelihood**: Probability before signals (0.0 - 1.0)
- **Impact**: Severity if it happens (1 = minor, 5 = catastrophic)
- **Confidence**: How sure you are in your assessment (0.0 - 1.0)
- **Time Horizon**: When it might materialize (weeks/months)
- **Description** (optional): Additional context

The form shows a live preview of the calculated risk score.

### 3. Adding Signals

Navigate to **📡 Manage Signals** → **➕ Create Signal**

Fill in the form:

- **Associated Risk**: Select which risk this signal affects
- **Signal Name**: Observable indicator (e.g., "Working overtime consistently")
- **Direction**: Does this increase or decrease the risk?
- **Strength**: How strongly does it affect the risk?
  - Weak: ±5% likelihood
  - Medium: ±10% likelihood
  - Strong: ±20% likelihood
- **Observed Date**: When you first noticed this signal
- **Description** (optional): Context about the observation

### 4. Tracking Trends

Navigate to **📈 Trends** → Select a risk

View:

- Risk score timeline with threshold lines
- Component analysis (likelihood, impact, confidence over time)
- Signal activity chart
- Statistical summary
- Full assessment history (expandable)

### 5. Recomputing Assessments

Use the **🔄 Recompute All Assessments** button in the sidebar to:

- Recalculate all risk scores with current signals
- Generate new assessment snapshots
- Update the trend data

**When to recompute:**

- After adding/editing/deleting signals
- After changing risk parameters
- When you want a new data point for trends

---

## 🧪 Example Scenarios

### Scenario 1: Career Risk Management

**Risk**: "Career stagnation"

- Category: Career
- Base likelihood: 40%
- Impact: 3/5
- Confidence: 70%
- Time horizon: Months

**Signals to track:**

- ❌ "No skill development for 3 months" (increase, medium)
- ❌ "Declined 2 learning opportunities" (increase, weak)
- ✅ "Completed online certification" (decrease, medium)
- ✅ "Leading a new project" (decrease, strong)

**How it helps**: You see the risk score decrease as you take action, providing clear feedback on your efforts.

### Scenario 2: Technical Debt

**Risk**: "Technical debt accumulation"

- Category: Technical
- Base likelihood: 50%
- Impact: 4/5
- Confidence: 75%
- Time horizon: Months

**Signals to track:**

- ❌ "Failed CI/CD tests" (increase, strong)
- ❌ "No code reviews for 2 weeks" (increase, medium)
- ❌ "Outdated dependencies" (increase, medium)
- ✅ "Refactoring sprint completed" (decrease, strong)
- ✅ "Documentation updated" (decrease, weak)

**How it helps**: Quantifies the cumulative effect of small issues before they become a crisis.

### Scenario 3: Health & Burnout

**Risk**: "Chronic stress and burnout"

- Category: Health
- Base likelihood: 60%
- Impact: 3/5
- Confidence: 90%
- Time horizon: Weeks

**Signals to track:**

- ❌ "Working >10h/day for 6+ days" (increase, strong)
- ❌ "Sleep <6 hours/night" (increase, medium)
- ❌ "Skipped meals 3+ times this week" (increase, weak)
- ✅ "Regular exercise routine" (decrease, medium)
- ✅ "Taking scheduled breaks" (decrease, weak)

**How it helps**: Makes the invisible cost of overwork visible, encouraging proactive recovery.

---

## 🧪 Testing

### Run Unit Tests

```bash
# Test domain models and scoring logic
uv run python tests/test_domain.py
```

### Run Integration Tests

```bash
# Terminal 1: Start the API server
uv run uvicorn api.main:app --reload

# Terminal 2: Run integration tests
uv run python tests/test_recompute.py
```

### Test Coverage

**Unit Tests** ([tests/test_domain.py](tests/test_domain.py)):

- ✅ Signal likelihood modifier calculations
- ✅ Effective likelihood calculation with multiple signals
- ✅ Likelihood clamping to [0.0, 1.0]
- ✅ Risk score formula
- ✅ Full risk assessment workflow
- ✅ Input validation for Risk model

**Integration Tests** ([tests/test_recompute.py](tests/test_recompute.py)):

- ✅ Single risk recompute with signals
- ✅ Recompute all risks endpoint
- ✅ Signal modifier verification
- ✅ Likelihood boundary clamping
- ✅ Assessment persistence in database

---

## 🔧 Development

### Code Quality

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Fix auto-fixable lint issues
uv run ruff check --fix .
```

### Database Management

```bash
# Reset database (WARNING: Deletes all data)
rm personal_risk_radar.db

# Reload examples
uv run python scripts/load_examples.py
```

### Quick API Test

```bash
# Check API health
curl http://localhost:8000/health

# Create a test risk
curl -X POST http://localhost:8000/api/risks/ \
  -H "Content-Type: application/json" \
  -d '{
    "category": "technical",
    "name": "Test Risk",
    "base_likelihood": 0.5,
    "impact": 3,
    "confidence": 0.8,
    "time_horizon": "weeks"
  }'

# Get all risks
curl http://localhost:8000/api/risks/
```

---

## 🧪 Intended Use Cases

- **Career Planning**: Track skill gaps, market changes, job security risks
- **Technical Debt**: Monitor code quality, testing coverage, dependency health
- **Health & Wellbeing**: Recognize burnout signals, sleep patterns, stress indicators
- **Financial Exposure**: Track spending patterns, budget adherence, emergency fund status
- **Personal Development**: Identify growth blockers, relationship strain, time management risks

---

## ❌ What This Is Not

| Not This          | Why                                              |
| ----------------- | ------------------------------------------------ |
| Productivity app  | Focus is on risk awareness, not task completion  |
| Habit tracker     | Signals are risk indicators, not habits to build |
| AI assistant      | All reasoning is explicit and human-driven       |
| Prediction engine | It aids thinking, not forecasting                |

**It is a thinking aid, not a recommendation engine.**

---

## 🔮 Future Extensions (Out of Scope for MVP)

- [ ] Multi-user support with authentication
- [ ] Temporal decay functions for aging signals
- [ ] Scenario simulation and "what-if" analysis
- [ ] Exportable risk reports (PDF/CSV)
- [ ] Plugin-based signal evaluators
- [ ] Mobile app or notifications
- [ ] Integration with external data sources

These are intentionally deferred to keep the core system sharp.

---

## 🎯 Design Philosophy

| Prefer      | Over        |
| ----------- | ----------- |
| Explicit    | Clever      |
| Explainable | Intelligent |
| Local-first | Cloud-first |
| Reasoning   | Automation  |

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with proper type hints
4. Run tests and linting
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Built with:

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Streamlit](https://streamlit.io/) - App framework for ML and data science
- [Plotly](https://plotly.com/) - Interactive visualizations
- [SQLAlchemy](https://www.sqlalchemy.org/) - SQL toolkit and ORM
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation using Python type hints
- [uv](https://docs.astral.sh/uv/) - Extremely fast Python package installer

---

**Built with clarity, not complexity.**

---

## 🚀 Getting Started

### First-Time Setup

Follow these steps to get up and running:

#### 1. Install Dependencies

```bash
uv sync
```

This will install all required packages including:

- FastAPI (API framework)
- Streamlit (Dashboard UI)
- Plotly (Interactive charts)
- SQLAlchemy (Database ORM)
- And more...

#### 2. Load Example Data (Recommended)

```bash
uv run python scripts/load_examples.py
```

This creates:

- 5 realistic sample risks across different categories
- 9 signals affecting these risks
- Initial assessments

**Note**: If you want to start fresh later, just delete `personal_risk_radar.db` and re-run this command.

#### 3. Launch the Dashboard

```bash
uv run streamlit run main.py
```

The browser will automatically open to `http://localhost:8501`

---

## 📚 Quick Tour

### Dashboard (📊)

- See all your risks at a glance
- View risk distribution by category
- Check severity levels
- Explore interactive charts

### Manage Risks (⚠️)

- **Create**: Add new risks with likelihood, impact, confidence
- **Edit**: Update existing risk parameters
- **Delete**: Remove risks (and their signals)

### Manage Signals (📡)

- **Create**: Add early warning indicators
- **Edit**: Adjust signal strength or direction
- **Delete**: Remove obsolete signals

### Trends (📈)

- Select any risk to view its history
- See how risk score changes over time
- Analyze component breakdowns
- View signal activity

### Recompute Assessments (🔄)

- Click the sidebar button after making changes
- Creates new assessment snapshots
- Updates all trend data

---

## 💡 Tips for Effective Use

### 1. Start Small

Don't try to model every risk at once. Start with 2-3 significant risks.

### 2. Be Specific with Signals

Good signals are observable and measurable:

- ✅ "Worked >10 hours/day for 7 days"
- ✅ "Failed 3 CI/CD tests this week"
- ❌ "Feeling stressed" (too vague)

### 3. Update Regularly

- Add new signals as you observe them
- Remove or edit signals that are no longer relevant
- Recompute assessments weekly or bi-weekly

### 4. Review Trends Monthly

Look for patterns:

- Is a risk consistently increasing?
- Do certain signals always precede problems?
- Which risks have you successfully mitigated?

### 5. Keep Confidence Honest

If you're uncertain about a risk assessment, lower the confidence value. This will reduce its weight in the overall score.

---

## 🔄 Common Workflows

### Adding a New Risk

1. Go to **⚠️ Manage Risks** → **➕ Create Risk**
2. Fill in all required fields
3. Use the preview to check the base risk score
4. Click **✅ Create Risk**
5. Optionally add signals immediately

### Tracking a New Signal

1. Go to **📡 Manage Signals** → **➕ Create Signal**
2. Select the associated risk
3. Describe the observable indicator
4. Set direction (increase/decrease)
5. Choose strength (weak/medium/strong)
6. Review the impact preview
7. Click **✅ Create Signal**
8. Click **🔄 Recompute All Assessments** in sidebar

### Analyzing Risk Evolution

1. Go to **📈 Trends**
2. Select a risk from the dropdown
3. Review the charts:
   - Risk score timeline shows overall trend
   - Component analysis shows what's changing
   - Signal activity shows indicator volume
4. Check statistics summary
5. Expand full history if needed

---

## 🛠️ Troubleshooting

### Database Issues

**Problem**: "Database is locked" or similar errors

**Solution**:

```bash
# Close all terminals running the app
# Delete the database
rm personal_risk_radar.db

# Reload examples
uv run python scripts/load_examples.py
```

### No Charts Showing

**Problem**: Charts don't render in dashboard

**Solution**:

```bash
# Ensure plotly is installed
uv sync

# Restart Streamlit
# Press Ctrl+C in terminal, then rerun:
uv run streamlit run main.py
```

### Import Errors

**Problem**: "ModuleNotFoundError" or similar

**Solution**:

```bash
# Reinstall dependencies
uv sync

# If issues persist, try:
rm -rf .venv
uv sync
```

---

## 📸 Screenshots

### Capturing Screenshots

To capture screenshots for the documentation:

1. Start the application:

   ```bash
   uv run streamlit run main.py
   ```

2. Load example data if you haven't already:

   ```bash
   uv run python scripts/load_examples.py
   ```

3. Navigate to each page and capture screenshots:
   - **dashboard.png**: Dashboard overview page with charts and risk cards
   - **create_risk.png**: Create Risk form with filled examples
   - **add_signal.png**: Add Signal form showing the impact preview
   - **trends.png**: Trends page showing interactive charts and statistics

**Recommended Settings:**

- **Browser**: Chrome or Firefox in light mode
- **Window Size**: 1440x900 or larger
- **Quality**: PNG format, high resolution
- **Content**: Show realistic data (use example data)

**Tools:**

- macOS: Cmd+Shift+4 (select area) or Cmd+Shift+5 (screenshot tool)
- Windows: Win+Shift+S (Snipping Tool)
- Linux: Flameshot, GNOME Screenshot, or similar

---

## 📋 Implementation Summary

### Completed Features

#### 1. Visualizations 📊

**Dashboard Enhancements:**

- **Pie Chart**: Risk distribution by category (career, financial, health, technical, personal)
- **Bar Chart**: Risk severity distribution (low, medium, high)
- **Horizontal Bar Chart**: Top 10 risks heatmap with color gradient
- **Interactive tooltips**: Hover details on all charts
- **Responsive layouts**: Charts adapt to screen size

**Trends Page Enhancements:**

- **Risk Score Timeline**: Line chart with threshold markers (high risk at 3.0, medium at 1.5)
- **Component Analysis**: Multi-line chart comparing likelihood, impact (normalized), and confidence over time
- **Signal Activity**: Area chart showing signal count evolution
- **Statistical Dashboard**: 5-metric summary (current, average, peak, lowest, trend)
- **Expandable History Table**: Full assessment data in collapsible section

**Technology**: Plotly for interactive, publication-quality visualizations

#### 2. UX Cleanup & Improvements 🎨

**Form Enhancements:**

- **Contextual Help Text**: Every input field has tooltips explaining purpose and valid ranges
- **Inline Previews**: Real-time risk score calculation before submission
- **Better Placeholders**: Example values in all text inputs
- **Smart Formatting**: Emojis for visual scanning, formatted percentages
- **Info Boxes**: Helpful tips on each page explaining concepts

**Page Improvements:**

- **Dashboard**:
  - Welcome message for empty state
  - Metric cards with help tooltips
  - Section headers with descriptions
  - Top 5 risk detail cards

- **Create/Edit Forms**:
  - Live risk score preview with severity indication
  - Signal impact calculator (shows ±% before creating)
  - Two-column layouts for better information density
  - Primary buttons with emojis for clear actions

- **Trends**:
  - Better date formatting
  - Multi-column statistics
  - Trend delta calculation (shows + or - change)
  - Improved chart labels and legends

**Validation & Error Handling:**

- **Input Validation**:
  - Name required and max length checks
  - Explicit error messages
  - Empty state handling throughout
  - Boundary checking (likelihood 0-1, impact 1-5)

#### 3. Edge Cases Handled 🛡️

**Empty States:**

- Dashboard shows welcoming message when no risks exist
- Forms disable or guide user when prerequisites missing
- Trends page explains why data might be missing

**Validation:**

- String length limits enforced (200 chars for names)
- Required field checks with clear error messages
- Probability value clamping (0.0 to 1.0)
- Impact value validation (1 to 5)

**Database Integrity:**

- Fixed SQLAlchemy enum configuration for SQLite compatibility
- Proper null handling in optional fields
- Cascade deletions (removing risk removes signals and assessments)

---

**Remember**: This tool is a thinking aid. The value comes from the act of modeling and tracking, not from the scores themselves.

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

## ✨ What the System Does

### You can

- Define risks across fixed categories (career, financial, health, technical, personal)
- Assign likelihood, impact, confidence, and time horizon
- Attach signals that increase or decrease risk
- Recompute risk exposure at any point in time
- Observe trends instead of static snapshots

### You get

- A continuously updated risk surface
- Visibility into blind spots
- Early indicators of drift before problems become irreversible

---

## 🧩 Core Concepts

### 1. Risk

A future uncertainty with potential impact.

Each risk includes:

| Field           | Description                                    |
| --------------- | ---------------------------------------------- |
| Category        | career, financial, health, technical, personal |
| Base likelihood | 0–1 (probability)                              |
| Impact          | 1–5 (severity scale)                           |
| Confidence      | How sure you are                               |
| Time horizon    | weeks / months                                 |

### 2. Signal

A measurable early warning sign linked to a risk.

Signals:

- Increase or decrease risk
- Have strength (weak / medium / strong)
- Adjust likelihood, not impact

**Examples:**

- "Working >10h/day for 6 days"
- "Delayed feedback cycles"
- "Declining sleep consistency"

### 3. Assessment

A snapshot produced by recomputing all risks using current signals and scoring logic.

---

## 📐 Risk Scoring (Simple & Explainable)

The system intentionally avoids ML or probabilistic black boxes.

**Baseline formula:**

```text
risk_score = likelihood × impact × confidence
```

Signals adjust the effective likelihood using deterministic rules.

This keeps reasoning:

- ✅ Transparent
- ✅ Auditable
- ✅ Easy to refine

---

## 🏗️ Architecture

The project is split into a typed backend and a visual frontend.

```tree
personal_risk_radar/
├── main.py              # Streamlit entry point
├── api/                 # FastAPI routes
├── domain/              # Core business logic
│   ├── models.py        # Risk, Signal, Assessment
│   └── scoring.py       # Risk calculation
├── persistence/         # Database layer (SQLite)
└── ui/                  # Streamlit components
```

### Backend

- **FastAPI** for API boundaries
- **Explicit domain models** with full type hints
- **SQLite** (local, file-based)
- **Deterministic scoring logic**

### Frontend

- **Streamlit** for rapid, introspective UI
- Dashboard-driven interaction
- Visual trend analysis

### Tooling

| Tool   | Purpose                                   |
| ------ | ----------------------------------------- |
| `uv`   | Dependency and environment management     |
| `ruff` | Linting and formatting                    |
| `ty`   | Strict typing for request/response models |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/Srijan-Baniyal/Personal-Risk-Radar.git
cd personal_risk_radar

# Create virtual environment and install dependencies
uv sync

# Initialize the database
uv run python -c "from persistence.database import init_db; init_db()"
```

### Running the Application

#### Option 1: Streamlit Dashboard (Recommended)

```bash
uv run streamlit run main.py
```

Open your browser to `http://localhost:8501`

#### Option 2: FastAPI Server Only

```bash
uv run uvicorn api.main:app --reload
```

API will be available at `http://localhost:8000`

- Interactive docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

#### Option 3: Both (Development Mode)

```bash
# Terminal 1: Start API server
uv run uvicorn api.main:app --reload

# Terminal 2: Start Streamlit dashboard
uv run streamlit run main.py
```

### Testing

#### Run Unit Tests (No server required)

```bash
# Test domain models and scoring logic
uv run python tests/test_domain.py
```

#### Run Integration Tests (Requires API server)

```bash
# Terminal 1: Start the API server
uv run uvicorn api.main:app --reload

# Terminal 2: Run integration tests
uv run python tests/test_recompute.py
```

#### Run All Tests

```bash
# Run unit tests
uv run python tests/test_domain.py

# Start server in background, run integration tests, then stop server
uv run uvicorn api.main:app --reload &
sleep 3
uv run python tests/test_recompute.py
pkill -f "uvicorn api.main:app"
```

### Development

#### Code Quality

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Fix auto-fixable lint issues
uv run ruff check --fix .

# Type check (if using pyright/myright)
uv run python -m pyright
```

#### Database Management

```bash
# Reset database (WARNING: Deletes all data)
rm personal_risk_radar.db
uv run python -c "from persistence.database import init_db; init_db()"

# Check database exists
ls -lh personal_risk_radar.db
```

#### Quick API Test

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

## 🧪 Test Coverage

### Unit Tests (`tests/test_domain.py`)

Tests domain logic without external dependencies:

- ✅ Signal likelihood modifier calculations
  - WEAK: ±0.05 (5%)
  - MEDIUM: ±0.10 (10%)
  - STRONG: ±0.20 (20%)
- ✅ Effective likelihood calculation with multiple signals
- ✅ Likelihood clamping to [0.0, 1.0]
- ✅ Risk score formula: `likelihood × impact × confidence`
- ✅ Full risk assessment workflow
- ✅ Input validation for Risk model

### Integration Tests (`tests/test_recompute.py`)

Tests API endpoints with database:

- ✅ Single risk recompute with signals
- ✅ Recompute all risks endpoint
- ✅ Signal modifier verification for all strengths/directions
- ✅ Likelihood boundary clamping (upper/lower bounds)
- ✅ Assessment persistence in database

### Example Test Output

```bash
$ uv run python tests/test_domain.py

Running unit tests...

✓ Signal likelihood modifiers correct
✓ Effective likelihood calculation correct
✓ Risk score calculation correct
✓ Risk assessment correct
✓ Risk model validation works

✅ All unit tests passed!
```

```bash
$ uv run python tests/test_recompute.py

Starting recompute endpoint tests...

Created risk with ID: 1
Created signal: Positive Signal
Created signal: Negative Signal

=== Assessment Result ===
Risk ID: 1
Base Likelihood: 0.5
Effective Likelihood: 0.65
Impact: 3
Confidence: 0.8
Risk Score: 1.56
Signal Count: 2

✓ Likelihood calculation correct: 0.65
✓ Risk score calculation correct: 1.56

=== Testing Recompute All ===
Recomputed 1 risks
  - Risk 1: score=1.56, likelihood=0.65, signals=2

✅ All tests passed!
```

---

## 🧪 Intended Use Cases

- Tracking career or technical debt risks
- Monitoring burnout or health drift
- Evaluating long-term personal or project exposure
- Practicing structured decision hygiene
- Learning to reason explicitly about uncertainty

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

- [ ] Multi-user support
- [ ] Temporal decay functions
- [ ] Scenario simulation
- [ ] Exportable risk reports
- [ ] Plugin-based signal evaluators

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

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

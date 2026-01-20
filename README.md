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
git clone https://github.com/yourusername/personal_risk_radar.git
cd personal_risk_radar

# Install dependencies with uv
uv sync

# Run the application
uv run streamlit run main.py
```

### Development

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Type check
uv run ty check
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

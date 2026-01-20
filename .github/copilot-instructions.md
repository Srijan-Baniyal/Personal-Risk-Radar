# Copilot Instructions for Personal Risk Radar

## Project Overview
Personal Risk Radar is a local-first system for modeling, tracking, and reasoning about risk over time. It uses FastAPI for the backend and Streamlit for the frontend.

## Tech Stack
- **Python 3.14+**
- **FastAPI** - API boundaries
- **Streamlit** - Dashboard UI
- **SQLite** - Local database
- **uv** - Package manager
- **ruff** - Linting and formatting
- **ty** - Type checking

## Code Style Guidelines

### Type Hints
- Always use type hints for function parameters and return types
- Use `typing` module for complex types
- Prefer explicit types over `Any`

### Naming Conventions
- Use snake_case for functions and variables
- Use PascalCase for classes
- Use SCREAMING_SNAKE_CASE for constants

### Domain Concepts
- **Risk**: A future uncertainty with potential impact (category, likelihood 0-1, impact 1-5, confidence, time horizon)
- **Signal**: A measurable early warning sign linked to a risk (increases/decreases risk, has strength: weak/medium/strong)
- **Assessment**: A snapshot produced by recomputing all risks using current signals

### Risk Scoring Formula
```python
risk_score = likelihood × impact × confidence
```

### Architecture Patterns
- Keep domain models explicit and typed
- Use deterministic scoring logic (no ML black boxes)
- Separate concerns: API, domain logic, persistence
- Local-first: SQLite file-based storage

## File Structure (Target)
```
personal_risk_radar/
├── main.py              # Streamlit entry point
├── api/                 # FastAPI routes
├── domain/              # Core business logic
│   ├── models.py        # Risk, Signal, Assessment
│   └── scoring.py       # Risk calculation
├── persistence/         # Database layer
└── ui/                  # Streamlit components
```

## Best Practices
- Prefer explicit over clever
- Make reasoning explainable
- Keep scoring logic transparent and auditable
- Write docstrings for public functions

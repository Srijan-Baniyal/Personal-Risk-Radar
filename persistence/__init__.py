"""Initialize persistence package."""

from persistence.database import (
    create_assessment,
    create_risk,
    create_signal,
    delete_risk,
    delete_signal,
    get_all_risks,
    get_assessments_for_risk,
    get_db,
    get_latest_assessments,
    get_risk,
    get_signal,
    get_signals_for_risk,
    init_db,
    update_risk,
    update_signal,
)

__all__: list[str] = [
    "init_db",
    "get_db",
    # Risk CRUD
    "create_risk",
    "get_risk",
    "get_all_risks",
    "update_risk",
    "delete_risk",
    # Signal CRUD
    "create_signal",
    "get_signal",
    "get_signals_for_risk",
    "update_signal",
    "delete_signal",
    # Assessment CRUD
    "create_assessment",
    "get_assessments_for_risk",
    "get_latest_assessments",
]

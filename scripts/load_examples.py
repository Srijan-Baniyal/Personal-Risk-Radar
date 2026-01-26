#!/usr/bin/env python3
"""Load example risk and signal data into the database."""

import csv
from datetime import datetime, timezone
from pathlib import Path

from domain.models import (Assessment, Risk, RiskCategory, Signal,
                           SignalDirection, SignalStrength, TimeHorizon)
from domain.scoring import assess_risk
from persistence.database import (RiskModel, SignalModel, create_assessment,
                                  create_risk, create_signal, get_all_risks,
                                  get_db, get_signals_for_risk, init_db)


def load_example_data() -> None:
    """Load example risks and signals from CSV files."""
    init_db()

    examples_dir: Path = Path(__file__).parent / "examples"
    risks_file: Path = examples_dir / "sample_risks.csv"
    signals_file: Path = examples_dir / "sample_signals.csv"

    if not risks_file.exists():
        print(f"❌ Risks file not found: {risks_file}")
        return

    if not signals_file.exists():
        print(f"❌ Signals file not found: {signals_file}")
        return

    print("🔄 Loading example data...")

    # Load risks
    with get_db() as db:
        existing_risks: list[RiskModel] = get_all_risks(db=db)
        if existing_risks:
            print(
                f"⚠️  Warning: Database already contains {len(existing_risks)} risk(s)."
            )
            response: str = input(
                "Do you want to continue? This will add more risks. (y/N): "
            )
            if response.lower() != "y":
                print("❌ Cancelled.")
                return

        risk_id_mapping: dict[int, int] = {}  # CSV row -> DB ID

        # Load risks from CSV
        with open(file=risks_file, mode="r") as f:
            reader: csv.DictReader[str] = csv.DictReader(f=f)
            csv_row = 1  # Start from 1 for CSV rows (header is row 0)
            for row in reader:
                csv_row += 1
                try:
                    risk_data = {  # type: ignore[var-annotated]
                        "category": RiskCategory(value=row["category"]),
                        "name": row["name"],
                        "description": row["description"]
                        if row["description"]
                        else None,
                        "base_likelihood": float(row["base_likelihood"]),
                        "impact": int(row["impact"]),
                        "confidence": float(row["confidence"]),
                        "time_horizon": TimeHorizon(row["time_horizon"]),
                    }

                    new_risk: RiskModel = create_risk(db=db, risk_data=risk_data)  # type: ignore[arg-type]
                    risk_id_mapping[csv_row - 1] = (
                        new_risk.id
                    )  # Store mapping (CSV row number to DB ID)

                    # Create initial assessment
                    risk_obj = Risk(  # type: ignore[arg-type]
                        id=new_risk.id,
                        **risk_data,  # type: ignore[arg-type]
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

                    print(f"✅ Created risk: {row['name']} (ID: {new_risk.id})")
                except Exception as e:
                    print(f"❌ Error loading risk '{row.get('name', 'unknown')}': {e}")

        # Load signals from CSV
        with open(file=signals_file, mode="r") as f:
            reader: csv.DictReader[str] = csv.DictReader(f=f)
            for row in reader:
                try:
                    # Map CSV risk_id to actual DB risk_id
                    csv_risk_id = int(row["risk_id"])
                    actual_risk_id = risk_id_mapping.get(csv_risk_id)

                    if actual_risk_id is None:
                        print(
                            f"⚠️  Skipping signal '{row['name']}': risk_id {csv_risk_id} not found in mapping"
                        )
                        continue

                    signal_data: dict[str, object] = {
                        "risk_id": actual_risk_id,
                        "name": row["name"],
                        "description": row["description"]
                        if row["description"]
                        else None,
                        "direction": SignalDirection(value=row["direction"]),
                        "strength": SignalStrength(value=row["strength"]),
                        "observed_at": datetime.now(tz=timezone.utc),
                    }

                    create_signal(db=db, signal_data=signal_data)
                    print(
                        f"✅ Created signal: {row['name']} for risk ID {actual_risk_id}"
                    )
                except Exception as e:
                    print(
                        f"❌ Error loading signal '{row.get('name', 'unknown')}': {e}"
                    )

        # Recompute all assessments with signals
        print("\n🔄 Recomputing assessments with signals...")
        risks: list[RiskModel] = get_all_risks(db=db)
        for risk in risks:
            signals: list[SignalModel] = get_signals_for_risk(db=db, risk_id=risk.id)
            risk_obj = Risk(
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
            signal_objs: list[Signal] = [Signal.from_db_model(db_signal=s) for s in signals]
            assessment: Assessment = assess_risk(risk=risk_obj, signals=signal_objs)
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

    print("\n✅ Successfully loaded example data!")
    print(f"📊 Total risks: {len(risk_id_mapping)}")
    print("\n🚀 Run 'streamlit run main.py' to view the dashboard.")


if __name__ == "__main__":
    load_example_data()

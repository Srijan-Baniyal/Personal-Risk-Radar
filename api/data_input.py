"""Data input handlers for CSV, Excel, and form-based uploads."""

import io
from datetime import datetime
from typing import Any, Optional

import pandas as pd
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, ValidationError

from domain.models import (Risk, RiskCategory, Signal, SignalDirection,
                           SignalStrength, TimeHorizon)
from persistence.database import create_risk, create_signal, get_db

router = APIRouter(prefix="/api/data-input", tags=["data-input"])


# Response Models
class DataUploadResponse(BaseModel):
    """Response model for data upload operations."""

    success: bool
    message: str
    records_processed: int
    records_created: int
    errors: list[str] = []


class FormDataResponse(BaseModel):
    """Response model for form-based data input."""

    success: bool
    message: str
    created_id: Optional[int] = None


# Helper Functions
def parse_csv_to_dataframe(file_content: bytes) -> pd.DataFrame:
    """Parse CSV file content to DataFrame."""
    try:
        return pd.read_csv(io.BytesIO(file_content))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse CSV: {str(e)}",
        )


def parse_excel_to_dataframe(file_content: bytes) -> pd.DataFrame:
    """Parse Excel file content to DataFrame."""
    try:
        return pd.read_excel(io.BytesIO(file_content))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse Excel: {str(e)}",
        )


def validate_and_clean_risk_data(row: dict[str, Any]) -> Optional[dict[str, Any]]:
    """
    Validate and clean a row of risk data.

    Returns cleaned data dict or None if validation fails.
    """
    try:
        # Handle different column name variations
        name_fields = ["name", "risk_name", "title", "risk"]
        category_fields = ["category", "risk_category", "type"]
        likelihood_fields = ["base_likelihood", "likelihood", "probability"]
        impact_fields = ["impact", "severity"]
        confidence_fields = ["confidence", "certainty"]
        horizon_fields = ["time_horizon", "horizon", "timeframe"]

        # Extract fields with fallbacks
        name = next((row.get(f) for f in name_fields if row.get(f)), None)
        category = next((row.get(f) for f in category_fields if row.get(f)), None)
        likelihood = next((row.get(f) for f in likelihood_fields if row.get(f) is not None), None)
        impact = next((row.get(f) for f in impact_fields if row.get(f) is not None), None)
        confidence = next((row.get(f) for f in confidence_fields if row.get(f) is not None), None)
        horizon = next((row.get(f) for f in horizon_fields if row.get(f)), None)

        if not all([name, category, likelihood is not None, impact is not None, confidence is not None, horizon]):
            return None

        # Normalize category
        category_str = str(category).lower().strip()
        if category_str not in [c.value for c in RiskCategory]:
            return None

        # Normalize time horizon
        horizon_str = str(horizon).lower().strip()
        if horizon_str not in [h.value for h in TimeHorizon]:
            return None

        # Build cleaned data
        cleaned = {
            "name": str(name).strip(),
            "category": category_str,
            "base_likelihood": float(likelihood),
            "impact": int(impact),
            "confidence": float(confidence),
            "time_horizon": horizon_str,
            "description": row.get("description", ""),
        }

        # Validate using domain model
        Risk(**cleaned)

        return cleaned

    except (ValueError, ValidationError):
        return None


def validate_and_clean_signal_data(row: dict[str, Any]) -> Optional[dict[str, Any]]:
    """
    Validate and clean a row of signal data.

    Returns cleaned data dict or None if validation fails.
    """
    try:
        # Handle different column name variations
        name_fields = ["name", "signal_name", "title", "signal"]
        risk_id_fields = ["risk_id", "riskid", "risk"]
        direction_fields = ["direction", "effect", "impact_direction"]
        strength_fields = ["strength", "intensity", "magnitude"]

        # Extract fields with fallbacks
        name = next((row.get(f) for f in name_fields if row.get(f)), None)
        risk_id = next((row.get(f) for f in risk_id_fields if row.get(f) is not None), None)
        direction = next((row.get(f) for f in direction_fields if row.get(f)), None)
        strength = next((row.get(f) for f in strength_fields if row.get(f)), None)

        if not all([name, risk_id is not None, direction, strength]):
            return None

        # Normalize direction
        direction_str = str(direction).lower().strip()
        if direction_str not in [d.value for d in SignalDirection]:
            return None

        # Normalize strength
        strength_str = str(strength).lower().strip()
        if strength_str not in [s.value for s in SignalStrength]:
            return None

        # Build cleaned data
        cleaned = {
            "name": str(name).strip(),
            "risk_id": int(risk_id),
            "direction": direction_str,
            "strength": strength_str,
            "description": row.get("description", ""),
        }

        # Validate using domain model
        Signal(**cleaned)

        return cleaned

    except (ValueError, ValidationError):
        return None


# Endpoints
@router.post("/upload/risks/csv", response_model=DataUploadResponse)
async def upload_risks_csv(file: UploadFile = File(...)) -> DataUploadResponse:
    """Upload risks from a CSV file."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV",
        )

    content = await file.read()
    df = parse_csv_to_dataframe(content)

    processed = 0
    created = 0
    errors = []

    with get_db() as db:
        for idx, row in df.iterrows():
            processed += 1
            row_dict = row.to_dict()

            cleaned_data = validate_and_clean_risk_data(row_dict)
            if cleaned_data:
                try:
                    create_risk(db, cleaned_data)
                    created += 1
                except Exception as e:
                    errors.append(f"Row {idx + 1}: {str(e)}")
            else:
                errors.append(f"Row {idx + 1}: Invalid or missing data")

    return DataUploadResponse(
        success=created > 0,
        message=f"Processed {processed} rows, created {created} risks",
        records_processed=processed,
        records_created=created,
        errors=errors[:10],  # Limit errors to first 10
    )


@router.post("/upload/risks/excel", response_model=DataUploadResponse)
async def upload_risks_excel(file: UploadFile = File(...)) -> DataUploadResponse:
    """Upload risks from an Excel file."""
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an Excel file",
        )

    content = await file.read()
    df = parse_excel_to_dataframe(content)

    processed = 0
    created = 0
    errors = []

    with get_db() as db:
        for idx, row in df.iterrows():
            processed += 1
            row_dict = row.to_dict()

            cleaned_data = validate_and_clean_risk_data(row_dict)
            if cleaned_data:
                try:
                    create_risk(db, cleaned_data)
                    created += 1
                except Exception as e:
                    errors.append(f"Row {idx + 1}: {str(e)}")
            else:
                errors.append(f"Row {idx + 1}: Invalid or missing data")

    return DataUploadResponse(
        success=created > 0,
        message=f"Processed {processed} rows, created {created} risks",
        records_processed=processed,
        records_created=created,
        errors=errors[:10],
    )


@router.post("/upload/signals/csv", response_model=DataUploadResponse)
async def upload_signals_csv(file: UploadFile = File(...)) -> DataUploadResponse:
    """Upload signals from a CSV file."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV",
        )

    content = await file.read()
    df = parse_csv_to_dataframe(content)

    processed = 0
    created = 0
    errors = []

    with get_db() as db:
        for idx, row in df.iterrows():
            processed += 1
            row_dict = row.to_dict()

            cleaned_data = validate_and_clean_signal_data(row_dict)
            if cleaned_data:
                try:
                    create_signal(db, cleaned_data)
                    created += 1
                except Exception as e:
                    errors.append(f"Row {idx + 1}: {str(e)}")
            else:
                errors.append(f"Row {idx + 1}: Invalid or missing data")

    return DataUploadResponse(
        success=created > 0,
        message=f"Processed {processed} rows, created {created} signals",
        records_processed=processed,
        records_created=created,
        errors=errors[:10],
    )


@router.post("/upload/signals/excel", response_model=DataUploadResponse)
async def upload_signals_excel(file: UploadFile = File(...)) -> DataUploadResponse:
    """Upload signals from an Excel file."""
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an Excel file",
        )

    content = await file.read()
    df = parse_excel_to_dataframe(content)

    processed = 0
    created = 0
    errors = []

    with get_db() as db:
        for idx, row in df.iterrows():
            processed += 1
            row_dict = row.to_dict()

            cleaned_data = validate_and_clean_signal_data(row_dict)
            if cleaned_data:
                try:
                    create_signal(db, cleaned_data)
                    created += 1
                except Exception as e:
                    errors.append(f"Row {idx + 1}: {str(e)}")
            else:
                errors.append(f"Row {idx + 1}: Invalid or missing data")

    return DataUploadResponse(
        success=created > 0,
        message=f"Processed {processed} rows, created {created} signals",
        records_processed=processed,
        records_created=created,
        errors=errors[:10],
    )


@router.post("/form/risk", response_model=FormDataResponse)
async def create_risk_from_form(
    name: str = Form(...),
    category: str = Form(...),
    base_likelihood: float = Form(...),
    impact: int = Form(...),
    confidence: float = Form(...),
    time_horizon: str = Form(...),
    description: str = Form(""),
) -> FormDataResponse:
    """Create a risk from form data."""
    try:
        # Validate and create risk
        risk_data = {
            "name": name,
            "category": category,
            "base_likelihood": base_likelihood,
            "impact": impact,
            "confidence": confidence,
            "time_horizon": time_horizon,
            "description": description,
        }

        # Validate using domain model
        Risk(**risk_data)

        with get_db() as db:
            db_risk = create_risk(db, risk_data)

        return FormDataResponse(
            success=True,
            message="Risk created successfully",
            created_id=db_risk.id,
        )

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create risk: {str(e)}",
        )


@router.post("/form/signal", response_model=FormDataResponse)
async def create_signal_from_form(
    name: str = Form(...),
    risk_id: int = Form(...),
    direction: str = Form(...),
    strength: str = Form(...),
    description: str = Form(""),
) -> FormDataResponse:
    """Create a signal from form data."""
    try:
        # Validate and create signal
        signal_data = {
            "name": name,
            "risk_id": risk_id,
            "direction": direction,
            "strength": strength,
            "description": description,
        }

        # Validate using domain model
        Signal(**signal_data)

        with get_db() as db:
            db_signal = create_signal(db, signal_data)

        return FormDataResponse(
            success=True,
            message="Signal created successfully",
            created_id=db_signal.id,
        )

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create signal: {str(e)}",
        )

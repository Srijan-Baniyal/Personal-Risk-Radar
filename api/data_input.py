"""Data input handlers for CSV, Excel, and form-based uploads."""

import io
from typing import Any, Optional

import pandas as pd
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, ValidationError

from domain.models import (Risk, RiskCategory, Signal, SignalDirection,
                           SignalStrength, TimeHorizon)
from persistence.database import RiskModel, SignalModel, create_risk, create_signal, get_db # type: ignore

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
        return pd.read_csv(filepath_or_buffer=io.BytesIO(initial_bytes=file_content))  # type: ignore[return-value]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse CSV: {str(object=e)}",
        )


def parse_excel_to_dataframe(file_content: bytes) -> pd.DataFrame:
    """Parse Excel file content to DataFrame."""
    try:
        return pd.read_excel(io=io.BytesIO(initial_bytes=file_content))  # type: ignore[return-value]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse Excel: {str(object=e)}",
        )


def validate_and_clean_risk_data(row: dict[str, Any]) -> Optional[dict[str, Any]]:
    """
    Validate and clean a row of risk data.

    Returns cleaned data dict or None if validation fails.
    """
    try:
        # Handle different column name variations
        name_fields: list[str] = ["name", "risk_name", "title", "risk"]
        category_fields: list[str] = ["category", "risk_category", "type"]
        likelihood_fields: list[str] = ["base_likelihood", "likelihood", "probability"]
        impact_fields: list[str] = ["impact", "severity"]
        confidence_fields: list[str] = ["confidence", "certainty"]
        horizon_fields: list[str] = ["time_horizon", "horizon", "timeframe"]
        # Extract fields with fallbacks
        name: Any | None = next((row.get(f) for f in name_fields if row.get(f)), None)
        category: Any | None = next((row.get(f) for f in category_fields if row.get(f)), None)
        likelihood: Any | None = next((row.get(f) for f in likelihood_fields if row.get(f) is not None), None)
        impact: Any | None = next((row.get(f) for f in impact_fields if row.get(f) is not None), None)
        confidence: Any | None = next((row.get(f) for f in confidence_fields if row.get(f) is not None), None)
        horizon: Any | None = next((row.get(f) for f in horizon_fields if row.get(f)), None)

        if not all([name, category, likelihood is not None, impact is not None, confidence is not None, horizon]):
            return None

        # Normalize category
        category_str: str = str(object=category).lower().strip()
        if category_str not in [c.value for c in RiskCategory]:
            return None

        # Normalize time horizon
        horizon_str: str = str(object=horizon).lower().strip()
        if horizon_str not in [h.value for h in TimeHorizon]:
            return None

        # Build cleaned data
        cleaned: dict[str, Any] = {
            "name": str(object=name).strip(),
            "category": category_str,
            "base_likelihood": float(x=likelihood),  # type: ignore[arg-type]
            "impact": int(impact),  # type: ignore[arg-type]
            "confidence": float(x=confidence),  # type: ignore[arg-type]
            "time_horizon": horizon_str,
            "description": row.get("description", ""),
        }

        # Validate using domain model
        Risk(**cleaned)  # type: ignore[arg-type]

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
        name_fields: list[str] = ["name", "signal_name", "title", "signal"]
        risk_id_fields: list[str] = ["risk_id", "riskid", "risk"]
        direction_fields: list[str] = ["direction", "effect", "impact_direction"]
        strength_fields: list[str] = ["strength", "intensity", "magnitude"]

        # Extract fields with fallbacks
        name: Any | None = next((row.get(f) for f in name_fields if row.get(f)), None)
        risk_id: Any | None = next((row.get(f) for f in risk_id_fields if row.get(f) is not None), None)
        direction: Any | None = next((row.get(f) for f in direction_fields if row.get(f)), None)
        strength: Any | None = next((row.get(f) for f in strength_fields if row.get(f)), None)

        if not all([name, risk_id is not None, direction, strength]):
            return None

        # Normalize direction
        direction_str: str = str(object=direction).lower().strip()
        if direction_str not in [d.value for d in SignalDirection]:
            return None

        # Normalize strength
        strength_str: str = str(object=strength).lower().strip()
        if strength_str not in [s.value for s in SignalStrength]:
            return None

        # Build cleaned data
        cleaned: dict[str, Any] = {
            "name": str(object=name).strip(),
            "risk_id": int(risk_id),  # type: ignore[arg-type]
            "direction": direction_str,
            "strength": strength_str,
            "description": row.get("description", ""),
        }

        # Validate using domain model
        Signal(**cleaned)  # type: ignore[arg-type]

        return cleaned

    except (ValueError, ValidationError):
        return None


# Endpoints
@router.post(path="/upload/risks/csv", response_model=DataUploadResponse)
async def upload_risks_csv(file: UploadFile = File(default=...)) -> DataUploadResponse:
    """Upload risks from a CSV file."""
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV",
        )

    content: bytes = await file.read()
    df: pd.DataFrame = parse_csv_to_dataframe(file_content=content)

    processed = 0
    created = 0
    errors: list[str] = []

    with get_db() as db:
        for idx, row in df.iterrows():
            processed += 1
            row_dict: dict[Any, Any] = row.to_dict()  # type: ignore[assignment]

            cleaned_data: dict[str, Any] | None = validate_and_clean_risk_data(row=row_dict)
            if cleaned_data:
                try:
                    create_risk(db=db, risk_data=cleaned_data)  # type: ignore[arg-type]
                    created += 1
                except Exception as e:
                    errors.append(f"Row {int(idx) + 1}: {str(object=e)}")  # type: ignore[arg-type]
            else:
                errors.append(f"Row {int(idx) + 1}: Invalid or missing data")  # type: ignore[arg-type]

    return DataUploadResponse(
        success=created > 0,
        message=f"Processed {processed} rows, created {created} risks",
        records_processed=processed,
        records_created=created,
        errors=errors[:10],  #type: ignore[arg-type]
    )


@router.post(path="/upload/risks/excel", response_model=DataUploadResponse)
async def upload_risks_excel(file: UploadFile = File(default=...)) -> DataUploadResponse:
    """Upload risks from an Excel file."""
    if not file.filename or not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an Excel file",
        )

    content: bytes = await file.read()
    df: pd.DataFrame = parse_excel_to_dataframe(file_content=content)

    processed = 0
    created = 0
    errors: list[str] = []

    with get_db() as db:
        for idx, row in df.iterrows():
            processed += 1
            row_dict: dict[Any, Any] = row.to_dict()  # type: ignore[assignment]

            cleaned_data: dict[str, Any] | None = validate_and_clean_risk_data(row=row_dict)
            if cleaned_data:
                try:
                    create_risk(db=db, risk_data=cleaned_data)  # type: ignore[arg-type]
                    created += 1
                except Exception as e:
                    errors.append(f"Row {int(idx) + 1}: {str(object=e)}")  # type: ignore[arg-type]
            else:
                errors.append(f"Row {int(idx) + 1}: Invalid or missing data")  # type: ignore[arg-type]

    return DataUploadResponse(
        success=created > 0,
        message=f"Processed {processed} rows, created {created} risks",
        records_processed=processed,
        records_created=created,
        errors=errors[:10],  # type: ignore[arg-type]
    )


@router.post(path="/upload/signals/csv", response_model=DataUploadResponse)
async def upload_signals_csv(file: UploadFile = File(default=...)) -> DataUploadResponse:
    """Upload signals from a CSV file."""
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV",
        )

    content: bytes = await file.read()
    df: pd.DataFrame = parse_csv_to_dataframe(file_content=content)

    processed = 0
    created = 0
    errors: list[str] = []

    with get_db() as db:
        for idx, row in df.iterrows():
            processed += 1
            row_dict: dict[Any, Any]     = row.to_dict()  # type: ignore[assignment]

            cleaned_data: dict[str, Any] | None = validate_and_clean_signal_data(row_dict)
            if cleaned_data:
                try:
                    create_signal(db=db, signal_data=cleaned_data)  # type: ignore[arg-type]
                    created += 1
                except Exception as e:
                    errors.append(f"Row {int(idx) + 1}: {str(e)}")  # type: ignore[arg-type]
            else:
                errors.append(f"Row {int(idx) + 1}: Invalid or missing data")  # type: ignore[arg-type]

    return DataUploadResponse(
        success=created > 0,
        message=f"Processed {processed} rows, created {created} signals",
        records_processed=processed,
        records_created=created,
        errors=errors[:10],
    )


@router.post(path="/upload/signals/excel", response_model=DataUploadResponse)
async def upload_signals_excel(file: UploadFile = File(default=...)) -> DataUploadResponse:
    """Upload signals from an Excel file."""
    if not file.filename or not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an Excel file",
        )

    content: bytes = await file.read()
    df: pd.DataFrame = parse_excel_to_dataframe(file_content=content)

    processed = 0
    created = 0
    errors: list[str] = []

    with get_db() as db:
        for idx, row in df.iterrows():
            processed += 1
            row_dict: dict[Any, Any] = row.to_dict()  # type: ignore[assignment]

            cleaned_data: dict[str, Any] | None = validate_and_clean_signal_data(row_dict)
            if cleaned_data:
                try:
                    create_signal(db=db, signal_data=cleaned_data)  # type: ignore[arg-type]
                    created += 1
                except Exception as e:
                    errors.append(f"Row {int(idx) + 1}: {str(e)}")  # type: ignore[arg-type]
            else:
                errors.append(f"Row {int(idx) + 1}: Invalid or missing data")  # type: ignore[arg-type]

    return DataUploadResponse(
        success=created > 0,
        message=f"Processed {processed} rows, created {created} signals",
        records_processed=processed,
        records_created=created,
        errors=errors[:10],
    )


@router.post(path="/form/risk", response_model=FormDataResponse)
async def create_risk_from_form(
    name: str = Form(default=...),
    category: str = Form(default=...),
    base_likelihood: float = Form(default=...),
    impact: int = Form(default=...),
    confidence: float = Form(default=...),
    time_horizon: str = Form(default=...),
    description: str = Form(default=""),
) -> FormDataResponse:
    """Create a risk from form data."""
    try:
        # Validate and create risk
        risk_data: dict[str, Any] = {
            "name": name,
            "category": category,
            "base_likelihood": base_likelihood,
            "impact": impact,
            "confidence": confidence,
            "time_horizon": time_horizon,
            "description": description,
        }

        # Validate using domain model
        Risk(**risk_data)  # type: ignore[arg-type]

        with get_db() as db:
            db_risk: RiskModel = create_risk(db=db, risk_data=risk_data)  # type: ignore[arg-type]

        return FormDataResponse(
            success=True,
            message="Risk created successfully",
            created_id=int(db_risk.id),  # type: ignore[arg-type]
        )

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(object=e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create risk: {str(object=e)}",
        )


@router.post(path="/form/signal", response_model=FormDataResponse)
async def create_signal_from_form(
    name: str = Form(default=...),
    risk_id: int = Form(default=...),
    direction: str = Form(default=...),
    strength: str = Form(default=...),
    description: str = Form(default=""),
) -> FormDataResponse:
    """Create a signal from form data."""
    try:
        # Validate and create signal
        signal_data: dict[str, Any] = {
            "name": name,
            "risk_id": risk_id,
            "direction": direction,
            "strength": strength,
            "description": description,
        }

        # Validate using domain model
        Signal(**signal_data)  # type: ignore[arg-type]

        with get_db() as db:
            db_signal: SignalModel = create_signal(db=db, signal_data=signal_data)  # type: ignore[arg-type]

        return FormDataResponse(
            success=True,
            message="Signal created successfully",
            created_id=int(db_signal.id),  # type: ignore[arg-type]
        )

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(object=e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create signal: {str(object=e)}",
        )

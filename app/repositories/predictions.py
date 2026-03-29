"""Repository for prediction persistence and retrieval."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from app.core.config import Settings
from app.core.exceptions import NotFoundException, ServiceUnavailableException
from app.schemas.prediction import PredictionCreate, PredictionRecord
from app.services.database.supabase_service import SupabaseService


class PredictionRepository:
    """Data access layer for predictions table in Supabase."""

    def __init__(self, db: SupabaseService, settings: Settings) -> None:
        self.db = db
        self.table = settings.predictions_table

    def create_prediction(self, payload: PredictionCreate) -> PredictionRecord:
        """Insert a prediction row and return persisted data."""
        client = self.db.get_client()
        response = client.table(self.table).insert(payload.model_dump(mode="json")).execute()
        rows = response.data or []
        if not rows:
            raise ServiceUnavailableException("Supabase insert returned empty response.")
        return self._to_record(rows[0])

    def list_by_user(self, user_id: str, limit: int = 20, cursor: str | None = None) -> list[PredictionRecord]:
        """Return paginated prediction history by user."""
        client = self.db.get_client()
        query = (
            client.table(self.table)
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
        )
        if cursor:
            query = query.lt("created_at", cursor)

        response = query.execute()
        return [self._to_record(row) for row in (response.data or [])]

    def get_by_user_and_id(self, user_id: str, prediction_id: str) -> PredictionRecord:
        """Return prediction detail by user and prediction id."""
        client = self.db.get_client()
        response = (
            client.table(self.table)
            .select("*")
            .eq("user_id", user_id)
            .eq("id", prediction_id)
            .limit(1)
            .execute()
        )
        rows = response.data or []
        if not rows:
            raise NotFoundException("Prediction history item not found.", code="PREDICTION_NOT_FOUND")
        return self._to_record(rows[0])

    def _to_record(self, row: dict[str, Any]) -> PredictionRecord:
        created_at_raw = row.get("created_at")
        if isinstance(created_at_raw, str):
            created_at = datetime.fromisoformat(created_at_raw.replace("Z", "+00:00"))
        else:
            created_at = created_at_raw

        normalized = {**row, "created_at": created_at}
        return PredictionRecord.model_validate(normalized)

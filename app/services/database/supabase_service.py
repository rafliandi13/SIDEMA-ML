"""Supabase database client service."""

from __future__ import annotations

from supabase import Client, create_client

from app.core.config import Settings
from app.core.exceptions import ServiceUnavailableException


class SupabaseService:
    """Lazy-initialized Supabase client wrapper."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client: Client | None = None

    @property
    def is_configured(self) -> bool:
        """Whether Supabase credentials are available."""
        return bool(self.settings.supabase_url and self.settings.supabase_key)

    def get_client(self) -> Client:
        """Return a connected Supabase client."""
        if not self.is_configured:
            raise ServiceUnavailableException(
                "Supabase credentials are not configured.",
                code="SUPABASE_NOT_CONFIGURED",
            )

        if self._client is None:
            self._client = create_client(self.settings.supabase_url, self.settings.supabase_key)
        return self._client

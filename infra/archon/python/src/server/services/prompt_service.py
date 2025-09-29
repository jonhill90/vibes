"""
Prompt Service Module for Archon

This module provides a singleton service for managing AI agent prompts.
Prompts are loaded from the database at startup and cached in memory for
fast access during agent operations.
"""

# Removed direct logging import - using unified config
from datetime import datetime

from ..config.logfire_config import get_logger
from ..utils import get_supabase_client

logger = get_logger(__name__)


class PromptService:
    """Singleton service for managing AI agent prompts."""

    _instance = None
    _prompts: dict[str, str] = {}
    _last_loaded: datetime | None = None

    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def load_prompts(self) -> None:
        """
        Load all prompts from database into memory.
        This should be called at application startup.
        """
        try:
            logger.info("Loading prompts from database...")
            supabase = get_supabase_client()

            response = supabase.table("archon_prompts").select("*").execute()

            if response.data:
                self._prompts = {
                    prompt["prompt_name"]: prompt["prompt"] for prompt in response.data
                }
                self._last_loaded = datetime.now()
                logger.info(f"Loaded {len(self._prompts)} prompts into memory")
            else:
                logger.warning("No prompts found in database")

        except Exception as e:
            logger.error(f"Failed to load prompts: {e}")
            # Continue with empty prompts rather than crash
            self._prompts = {}

    def get_prompt(self, prompt_name: str, default: str | None = None) -> str:
        """
        Get a prompt by name.

        Args:
            prompt_name: The name of the prompt to retrieve
            default: Default prompt to return if not found

        Returns:
            The prompt text or default value
        """
        if default is None:
            default = "You are a helpful AI assistant."

        prompt = self._prompts.get(prompt_name, default)

        if prompt == default and prompt_name not in self._prompts:
            logger.warning(f"Prompt '{prompt_name}' not found, using default")

        return prompt

    async def reload_prompts(self) -> None:
        """
        Reload prompts from database.
        Useful for refreshing prompts after they've been updated.
        """
        logger.info("Reloading prompts...")
        await self.load_prompts()

    def get_all_prompt_names(self) -> list[str]:
        """Get a list of all available prompt names."""
        return list(self._prompts.keys())

    def get_last_loaded_time(self) -> datetime | None:
        """Get the timestamp of when prompts were last loaded."""
        return self._last_loaded


# Global instance
prompt_service = PromptService()

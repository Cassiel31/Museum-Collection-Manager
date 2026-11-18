"""Compatibility interface for the Metropolitan Museum of Art public API."""
from app.services.met_service import search_artifacts, get_artifact, import_artifact

__all__ = ["search_artifacts", "get_artifact", "import_artifact"]

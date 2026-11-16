"""Tests for the job source repository."""

from coi.models.enums import SourceType
from coi.repositories.source import SourceRepository


def test_get_all_sources() -> None:
    """Test retrieving all default sources."""

    repository = SourceRepository()

    sources = repository.get_all()

    assert len(sources) == 4


def test_get_all_sources_returns_copy() -> None:
    """Test that modifying the returned list does not affect the repository."""

    repository = SourceRepository()

    sources = repository.get_all()
    sources.clear()

    assert len(repository.get_all()) == 4


def test_default_sources_use_manual_type() -> None:
    """Test that all default sources use manual collection."""

    repository = SourceRepository()

    sources = repository.get_all()

    assert all(source.source_type == SourceType.MANUAL for source in sources)

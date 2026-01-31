"""Memory module for AKIRA 2.0 (ASCII only)."""

from .store import (
    EnhancedMemoryStore,
    Episode,
    Pattern,
    Project,
    MemoryType,
)
from .indexer import ProjectIndexer, ProjectMetadata
from .retriever import MemoryRetriever, SearchResult, SearchType
from .compressor import ContextCompressor, CompressedContext
from .episodic import EpisodicMemory, EpisodeEvent
from .patterns import PatternRecognizer, ExtractedPattern, TaskClassification, CausalChain
from .cross_project import CrossProjectIndex, CrossProjectResult
from .pattern_extractor import PatternExtractor

__all__ = [
    "EnhancedMemoryStore",
    "Episode",
    "Pattern",
    "Project",
    "MemoryType",
    "ProjectIndexer",
    "ProjectMetadata",
    "MemoryRetriever",
    "SearchResult",
    "SearchType",
    "ContextCompressor",
    "CompressedContext",
    "EpisodicMemory",
    "EpisodeEvent",
    "PatternRecognizer",
    "ExtractedPattern",
    "TaskClassification",
    "CausalChain",
    "CrossProjectIndex",
    "CrossProjectResult",
    "PatternExtractor",
]

# Backward-compatible alias used across the codebase/tests.
MemoryStore = EnhancedMemoryStore
__all__.append("MemoryStore")

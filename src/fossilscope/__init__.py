"""FossilScope temporal security archaeology."""

# Load the bounded Web-theme compatibility bridge before Web modules are imported.
from . import web_theme as _web_theme  # noqa: F401
from .evolution import ArtifactKind, EvolutionDelta, StaleReferenceCandidate, VersionedArtifactObservation, diff_artifact_versions, find_stale_references
from .lifecycle import EvidenceKind, ExposureLifecycle, LifecycleAssessment, SurfaceEvidence, assess_lifecycle
from .planning import CurrentExposureState, ReobservationCandidate, plan_reobservation
from .reobservation import ReobservationDecision, ReobservationMode, ReobservationReason, ReobservationRequest, ReobservationState, deduplicate_requests, evaluate_reobservation, schedule_retry

__all__ = [
    "ArtifactKind", "CurrentExposureState", "EvidenceKind", "EvolutionDelta", "ExposureLifecycle",
    "LifecycleAssessment", "ReobservationCandidate", "ReobservationDecision", "ReobservationMode",
    "ReobservationReason", "ReobservationRequest", "ReobservationState", "StaleReferenceCandidate",
    "SurfaceEvidence", "VersionedArtifactObservation", "assess_lifecycle", "deduplicate_requests",
    "diff_artifact_versions", "evaluate_reobservation", "find_stale_references", "plan_reobservation",
    "schedule_retry",
]
__version__ = "0.5.15"

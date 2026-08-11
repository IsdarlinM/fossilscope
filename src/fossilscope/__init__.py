"""FossilScope temporal security archaeology."""

# Load bounded compatibility bridges before shared Web modules are imported. Clean
# 0.5.15 installs use the canonical SRIC implementations; these shims only keep an
# existing 0.5.14 runtime repairable during the product-first update transition.
from . import web_theme as _web_theme  # noqa: F401
from .web_catalog_compat import install as _install_web_catalog_compat

_install_web_catalog_compat()

from .evolution import ArtifactKind, EvolutionDelta, StaleReferenceCandidate, VersionedArtifactObservation, diff_artifact_versions, find_stale_references  # noqa: E402
from .lifecycle import EvidenceKind, ExposureLifecycle, LifecycleAssessment, SurfaceEvidence, assess_lifecycle  # noqa: E402
from .planning import CurrentExposureState, ReobservationCandidate, plan_reobservation  # noqa: E402
from .reobservation import ReobservationDecision, ReobservationMode, ReobservationReason, ReobservationRequest, ReobservationState, deduplicate_requests, evaluate_reobservation, schedule_retry  # noqa: E402

__all__ = [
    "ArtifactKind", "CurrentExposureState", "EvidenceKind", "EvolutionDelta", "ExposureLifecycle",
    "LifecycleAssessment", "ReobservationCandidate", "ReobservationDecision", "ReobservationMode",
    "ReobservationReason", "ReobservationRequest", "ReobservationState", "StaleReferenceCandidate",
    "SurfaceEvidence", "VersionedArtifactObservation", "assess_lifecycle", "deduplicate_requests",
    "diff_artifact_versions", "evaluate_reobservation", "find_stale_references", "plan_reobservation",
    "schedule_retry",
]
__version__ = "0.5.15"

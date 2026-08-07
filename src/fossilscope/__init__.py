"""FossilScope temporal security archaeology."""

from .lifecycle import (
    EvidenceKind,
    ExposureLifecycle,
    LifecycleAssessment,
    SurfaceEvidence,
    assess_lifecycle,
)

__all__ = [
    "EvidenceKind",
    "ExposureLifecycle",
    "LifecycleAssessment",
    "SurfaceEvidence",
    "assess_lifecycle",
]
__version__ = "0.3.1"

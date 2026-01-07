"""
Script Director Module
======================

Pre-production planning: layer analysis, action classification, and timeline generation.

Public API:
-----------
- ScriptDirectorConfig: Configuration for timeline planning
- create_timeline(): Factory to generate timeline from layers
- plan_production(): High-level orchestration function
- Timeline, Action, ActionType: Core domain types

Usage:
------
    from domain.modules.script_director import create_timeline, SequencingStrategy

    timeline = create_timeline(layers, strategy=SequencingStrategy.STAGGERED)
    for action in timeline.actions:
        print(action.layer_id, action.start_time)

Internal (DO NOT IMPORT DIRECTLY):
----------------------------------
- action_classifier_module.py
- layer_classifier_module.py
- timeline_planner_module.py
"""

from __future__ import annotations

from ...entities.action_entity import Action, CameraAction
from ...entities.smart_action_entity import SmartAction
from ...entities.timeline_entity import TimelineEntity
from ...value_objects.analysis.classification_result_value import ClassificationResult

# Smart Scheduling
from ...value_objects.analysis.layer_analysis_value import LayerAnalysis

# ============================================================
# Re-exports (Updated for Extreme Modularity)
# ============================================================
from ...value_objects.animation.action_type_value import ActionType
from ...value_objects.animation.layer_classification_value import LayerClassification
from ...value_objects.animation.path_direction_value import PathDirection
from ...value_objects.animation.sequencing_strategy_value import SequencingStrategy

# ============================================================
# Core Exports (Extracted)
# ============================================================
from ...value_objects.configs import ScriptDirectorConfig
from ...value_objects.manifest.compositor_manifest_value import CompositorManifest
from ...value_objects.manifest.layer_manifest_value import LayerManifest
from ...value_objects.visual.orientation_value import Orientation
from .analysis.action_classifier_module import classify_action
from .analysis.layer_analyzer_module import (
    analyze_layer,
    analyze_layers,
    calculate_duration,
    get_orientation,
)
from .analysis.layer_classifier_module import classify_layer
from .generators.manifest_generator_module import (
    generate_and_save_manifest,
    generate_manifest,
    save_manifest,
)

# Note: plan_timeline removed from direct export (use create_timeline)
from .generators.script_generator_module import generate_python_script
from .planners.smart_timeline_planner_module import (
    get_alternating_action_type,
    sort_layers_by_z_index,
)
from .planners.timeline_planner_module import estimate_duration
from .script_orchestrator import (
    create_smart_timeline,  # Orchestrator wrapper
    create_timeline,
    plan_production,
)

# Alias for backward compatibility (using Orchestrator wrapper)
# Alias for backward compatibility (using Orchestrator wrapper)
plan_smart_timeline = create_smart_timeline

# Backward Compatibility Aliases (Renamed/Moved Types)
ActionClassificationResult = ClassificationResult
LayerClassificationResult = ClassificationResult
AnimationType = ActionType


# ============================================================
# Public API
# ============================================================

__all__ = [
    # Configuration
    "ScriptDirectorConfig",
    # Factory Functions (Orchestrator Level)
    "create_timeline",
    "plan_production",
    "create_smart_timeline",
    "plan_smart_timeline",  # Aliased to orchestrator
    # Action Classifier
    "ActionType",
    "classify_action",
    "ActionClassificationResult",
    # Layer Classifier
    "AnimationType",
    "classify_layer",
    "LayerClassification",
    "LayerClassificationResult",
    # Timeline Planner
    "TimelineEntity",
    "Action",
    "CameraAction",
    "SequencingStrategy",
    # 'plan_timeline', # REMOVED: Use create_timeline (Enforcing Manager Pattern)
    "estimate_duration",
    # Script Generator
    "generate_python_script",
    # Smart Scheduling
    "get_orientation",
    "calculate_duration",
    "analyze_layer",
    "analyze_layers",
    "LayerAnalysis",
    "Orientation",
    "generate_manifest",
    "save_manifest",
    "generate_and_save_manifest",
    "CompositorManifest",
    "LayerManifest",
    "SmartAction",
    "PathDirection",
    "sort_layers_by_z_index",
    "get_alternating_action_type",
]

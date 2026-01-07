"""
Missing Import Fixer Strategy
=============================
Fixes F821 (undefined name) by analyzing the error and finding the correct import.
Uses a knowledge base of common imports to auto-resolve undefined names.
"""

import re
from typing import List

from ..core.types import FixResult, LintError
from .base import BaseStrategy

# Knowledge base: undefined name -> (module_path, import_statement_pattern)
IMPORT_KNOWLEDGE_BASE = {
    # Value Objects
    "MediaOutputPath": "....value_objects.resource.media_output_path_value",
    "LayerManifest": "....value_objects.manifest.layer_manifest_value",
    "CompositorManifest": "....value_objects.manifest.compositor_manifest_value",
    "RenderFrame": "....value_objects.animation.render_state_value",
    "BrushPathType": "....value_objects.animation.brush_path_type_value",
    "PathDirection": "....value_objects.animation.path_direction_value",
    "LayerAnalysis": "....value_objects.analysis.layer_analysis_value",
    # Entities
    "LayerEntity": "....entities.layer_entity",
    "WorldEntity": "....entities.world_entity",
    "CameraEntity": "....entities.camera_entity",
    "ViewportEntity": "....entities.viewport_entity",
    # Common stdlib
    "Any": "typing",
    "Dict": "typing",
    "List": "typing",
    "Optional": "typing",
    "Callable": "collections.abc",
    "Image": "PIL",
    "Path": "pathlib",
    "dataclass": "dataclasses",
    "field": "dataclasses",
    "Enum": "enum",
}


class MissingImportFixer(BaseStrategy):
    """
    Fixes F821 undefined name errors by adding missing imports.

    Strategy:
    1. Parse the undefined name from error message
    2. Look up in knowledge base
    3. Add import statement at correct position
    """

    def fix(self, errors: List[LintError]) -> List[FixResult]:
        results: List[FixResult] = []

        # Filter for F821 errors
        f821_errors = [e for e in errors if e.code == "F821"]

        # Group by file
        errors_by_file: dict[str, list[LintError]] = {}
        for err in f821_errors:
            if err.file not in errors_by_file:
                errors_by_file[err.file] = []
            errors_by_file[err.file].append(err)

        for file_path, file_errors in errors_by_file.items():
            try:
                with open(file_path, "r") as f:
                    content = f.read()
                    lines = content.split("\n")

                imports_to_add: list[str] = []

                for err in file_errors:
                    # Extract undefined name from message
                    # Pattern: "Undefined name `XXX`"
                    match = re.search(r"Undefined name `([^`]+)`", err.message)
                    if not match:
                        continue

                    undefined_name = match.group(1)

                    if undefined_name in IMPORT_KNOWLEDGE_BASE:
                        module = IMPORT_KNOWLEDGE_BASE[undefined_name]

                        # Determine import style based on module
                        if module.startswith("...."):
                            # Relative import
                            import_stmt = f"from {module} import {undefined_name}"
                        elif "." in module:
                            # Absolute with submodule
                            import_stmt = f"from {module} import {undefined_name}"
                        else:
                            # Simple import
                            import_stmt = f"from {module} import {undefined_name}"

                        # Check if already imported
                        if (
                            import_stmt not in content
                            and undefined_name not in content.split("import ")[0]
                            if "import " in content
                            else True
                        ):
                            imports_to_add.append(import_stmt)

                if imports_to_add:
                    # Find insertion point (after last import)
                    insert_line = 0
                    for i, line in enumerate(lines):
                        if line.startswith("from ") or line.startswith("import "):
                            insert_line = i + 1

                    # Insert imports
                    for imp in imports_to_add:
                        lines.insert(insert_line, imp)
                        insert_line += 1

                    # Write back
                    with open(file_path, "w") as f:
                        f.write("\n".join(lines))

                    results.append(
                        FixResult(
                            file=file_path,
                            line=0,
                            fixed=True,
                            message=f"Added imports: {', '.join(imports_to_add)}",
                        )
                    )

            except Exception as e:
                results.append(
                    FixResult(file=file_path, line=0, fixed=False, message=f"Error: {e}")
                )

        return results

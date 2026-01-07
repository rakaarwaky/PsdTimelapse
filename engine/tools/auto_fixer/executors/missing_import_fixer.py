"""
Missing Import Fixer Strategy
=============================
Fixes F821 (undefined name) by analyzing the error and finding the correct import.
Uses a knowledge base of common imports to auto-resolve undefined names.
"""

import re

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

    def fix(self, errors: list[LintError]) -> list[FixResult]:
        results: list[FixResult] = []

        # Filter for F821 errors
        f821_errors = [e for e in errors if e.code == "F821"]

        # Group by file
        errors_by_file: dict[str, list[LintError]] = {}
        for err in f821_errors:
            if err.file not in errors_by_file:
                errors_by_file[err.file] = []
            errors_by_file[err.file].append(err)

        for file_path, file_errors in errors_by_file.items():
            fix_result = self._fix_file(file_path, file_errors)
            if fix_result:
                results.append(fix_result)

        return results

    def _fix_file(self, file_path: str, file_errors: list[LintError]) -> FixResult | None:
        try:
            with open(file_path) as f:
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
                import_stmt = self._generate_import_statement(undefined_name)

                if import_stmt and import_stmt not in content and import_stmt not in imports_to_add:
                    imports_to_add.append(import_stmt)

            if imports_to_add:
                self._apply_imports(file_path, lines, imports_to_add)
                return FixResult(
                    file=file_path,
                    fixed=True,
                    strategy="missing_import",
                    details=f"Added imports: {', '.join(imports_to_add)}",
                )

            return None

        except Exception as e:
            return FixResult(
                file=file_path,
                fixed=False,
                strategy="missing_import",
                details=f"Error: {e}",
            )

    def _generate_import_statement(self, name: str) -> str | None:
        if name in IMPORT_KNOWLEDGE_BASE:
            module = IMPORT_KNOWLEDGE_BASE[name]
            return f"from {module} import {name}"
        return None

    def _apply_imports(self, file_path: str, lines: list[str], imports: list[str]) -> None:
        # Find insertion point (after last import)
        insert_line = 0
        for i, line in enumerate(lines):
            if line.startswith("from ") or line.startswith("import "):
                insert_line = i + 1

        # Insert imports
        for imp in imports:
            lines.insert(insert_line, imp)
            insert_line += 1

        # Write back
        with open(file_path, "w") as f:
            f.write("\n".join(lines))

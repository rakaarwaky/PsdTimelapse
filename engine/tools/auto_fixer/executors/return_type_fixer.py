"""
Return Type Fixer Strategy (AST-Based)
======================================
Enterprise-grade fixer for type annotations using Python's Abstract Syntax Tree.
Robustly handles multi-line definitions, decorators, and complex signatures.

Handles:
- no-untyped-def: Functions missing return type annotations
- no-any-return: Functions returning Any implicitly
"""

import ast
from collections import defaultdict
from pathlib import Path
from typing import List, Optional, Union

from ..core.types import FixResult, LintError
from .base import BaseStrategy

# Define Union type for AST nodes we care about
FunctionNode = Union[ast.FunctionDef, ast.AsyncFunctionDef]


class ReturnTypeFixer(BaseStrategy):
    """Fixes missing return type annotations using AST analysis."""

    def fix(self, errors: List[LintError]) -> List[FixResult]:
        results: List[FixResult] = []

        # Filter relevant errors
        relevant = [e for e in errors if e.code in ("no-untyped-def", "no-any-return")]
        if not relevant:
            return results

        # Group by file
        files: dict[str, list[LintError]] = defaultdict(list)
        for err in relevant:
            files[err.file].append(err)

        for file_path, file_errors in files.items():
            path = Path(file_path)
            if not path.exists():
                continue

            try:
                content = path.read_text()
                # Parse AST once per file
                tree = ast.parse(content)
                lines = content.splitlines()
                modified = False
                fixed_count = 0

                # Map line numbers to function nodes
                # ast line numbers are 1-based
                func_nodes: dict[int, FunctionNode] = {}
                for ast_node in ast.walk(tree):
                    if isinstance(ast_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        # We map the starting line of the def
                        func_nodes[ast_node.lineno] = ast_node

                # Sort errors bottom-up to avoid offset issues
                for err in sorted(file_errors, key=lambda e: e.line, reverse=True):
                    # Error line from MyPy usually points to the @decorator or 'def' line
                    func_node: FunctionNode | None = self._find_node_near_line(func_nodes, err.line)

                    if func_node and func_node.returns is None:
                        # Ensure we don't fix __init__ (unless we want to enforce -> None)
                        if func_node.name == "__init__":
                            # __init__ always returns None
                            if self._inject_return_type(lines, func_node, "None"):
                                modified = True
                                fixed_count += 1
                        # For other functions, determine if we can safely add None
                        elif not self._has_return_value(func_node):
                            if self._inject_return_type(lines, func_node, "None"):
                                modified = True
                                fixed_count += 1

                if modified:
                    path.write_text("\n".join(lines) + "\n")
                    results.append(
                        FixResult(
                            file=file_path,
                            fixed=True,
                            strategy="return_type",
                            details=f"Added AST-verified return types to {fixed_count} functions",
                        )
                    )

            except Exception as e:
                results.append(
                    FixResult(
                        file=file_path,
                        fixed=False,
                        strategy="return_type",
                        details=f"AST Parse Error: {e}",
                    )
                )

        return results

    def _find_node_near_line(
        self, func_nodes: dict[int, FunctionNode], line: int
    ) -> Optional[FunctionNode]:
        """Finds a function node that starts near the given line."""
        # Check explicit line first
        if line in func_nodes:
            return func_nodes[line]
        # Check 1-2 lines above (decorators might offset it)
        for offset in range(1, 4):
            if (line + offset) in func_nodes:
                return func_nodes[line + offset]
        return None

    def _has_return_value(self, node: FunctionNode) -> bool:
        """Check if function has any 'return value' statement."""
        for child in ast.walk(node):
            if isinstance(child, ast.Return) and child.value is not None:
                return True
            # Yield usually implies Iterator/Generator, handled separately
            if isinstance(child, (ast.Yield, ast.YieldFrom)):
                return True
        return False

    def _inject_return_type(self, lines: List[str], node: FunctionNode, ret_type: str) -> bool:
        """Injects -> Type into the source lines."""
        # Find the end of validity for the function signature.
        # This is tricky in text. AST gives us node.lineno (start) and body start.
        # We need to find the colon after the arguments.

        # Start searching from the function definition line
        start_idx = node.lineno - 1

        # Heuristic: Scan forward until we find the colon that ends the def
        # We must ignore colons inside parentheses (default args)

        paren_depth = 0
        for i in range(start_idx, len(lines)):
            line = lines[i]
            for j, char in enumerate(line):
                if char == "(":
                    paren_depth += 1
                elif char == ")":
                    paren_depth -= 1
                elif char == ":" and paren_depth == 0:
                    # FOUND IT!
                    # Insert before the colon
                    # Check if -> exists in this area (ignoring inside string literals)
                    # For safety, we just inspect the text created so far

                    # Construct new line segment
                    pre_colon = line[:j].rstrip()
                    post_colon = line[j:]

                    if "->" in pre_colon:
                        return False  # Already exists

                    new_line = f"{pre_colon} -> {ret_type}{post_colon}"
                    lines[i] = new_line
                    return True

            # Safety break if we go too far (into body)
            # node.body[0].lineno usually gives start of body
            if node.body and (i + 1) >= node.body[0].lineno:
                break

        return False

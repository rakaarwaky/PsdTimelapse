"""
PSD Modeler: Asset parser for PSD files using psd-tools library.

Exports:
    - PsdToolsParserAdapter: Main PSD parser
    - PsdModelerAdapter: Alias for core modeler
"""

from .psdtools_parser_adapter import PsdToolsAdapter

# Alias for cleaner naming following brand convention
PsdToolsModelerAdapter = PsdToolsAdapter
PsdModeler = PsdToolsAdapter

__all__ = [
    "PsdToolsAdapter",
    "PsdToolsModelerAdapter",
    "PsdModeler",
]

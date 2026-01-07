"""Driven adapters package - Infrastructure implementations (7-Role Architecture)."""

# New 7-Role Architecture imports
from .cache.in_memory_cache_adapter import InMemoryCacheAdapter
from .encoder import MoviePyAdapter, MoviePyEncoderAdapter
from .filesystem.local_asset_provider_adapter import LocalAssetProviderAdapter
from .filesystem.local_file_system_adapter import LocalFileSystemAdapter
from .image.pillow_image_adapter import PillowImageAdapter  # ImageProcessingPort impl
from .logging.std_logger_adapter import StdLoggerAdapter
from .notifications.console_notification_adapter import ConsoleNotificationAdapter
from .psd_modeler import PsdModeler, PsdToolsAdapter
from .renderers.pillow_renderer_adapter import PillowRenderer  # Legacy compatibility
from .system.system_random_adapter import SystemRandomAdapter
from .system.system_time_adapter import SystemTimeAdapter
from .ui_modeler import PillowModelerAdapter, UIRendererCore

__all__ = [
    # PSD Modeler
    "PsdModeler",
    "PsdToolsAdapter",
    # UI Modeler
    "UIRendererCore",
    "PillowModelerAdapter",
    # Encoder
    "MoviePyEncoderAdapter",
    "MoviePyAdapter",
    # Image Processing
    "PillowImageAdapter",
    # System & Utilities
    "StdLoggerAdapter",
    "ConsoleNotificationAdapter",
    "LocalFileSystemAdapter",
    "SystemTimeAdapter",
    "SystemRandomAdapter",
    "InMemoryCacheAdapter",
    "LocalAssetProviderAdapter",
    # Legacy compatibility
    "PillowRenderer",
]

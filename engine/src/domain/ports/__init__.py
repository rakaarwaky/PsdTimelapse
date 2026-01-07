"""
Domain Ports - Hexagonal Architecture Interfaces

This module exports all port interfaces for the Domain layer.
Ports define the boundaries between the Domain and Infrastructure.

Usage:
    from domain.ports import LoggerPort, NotificationPort, ...
"""

# === Core I/O Ports (Original) ===
from .media.exr_export_port import ExrExportPort
from .media.frame_output_port import FrameOutputPort

# === Image Processing Ports ===
from .media.image_processing_port import ImageProcessingPort

# === UI/Visual Ports ===
from .media.overlay_port import CursorType, NullOverlay, OverlayPort
from .media.psd_port import PsdPort
from .media.video_port import VideoPort
from .render.compositor_port import CompositorPort
from .render.gpu_renderer_port import GpuRendererPort
from .render.renderer_port import RendererPort
from .store.asset_provider_port import AssetProviderPort, NullAssetProvider
from .store.cache_port import CachePort

# === Infrastructure Ports ===
from .store.file_system_port import FileSystemPort

# === Observability Ports ===
from .system.logger_port import LoggerPort, NullLogger
from .system.notification_port import (
    DomainEvent,
    EventPayload,
    InMemoryEventBus,
    NotificationPort,
    NullNotifier,
)
from .system.random_port import DeterministicRandom, RandomPort
from .system.time_port import MockTime, TimePort

__all__ = [
    # Core I/O
    "PsdPort",
    "RendererPort",
    "VideoPort",
    "GpuRendererPort",
    "CompositorPort",
    "ExrExportPort",
    "FrameOutputPort",
    # Observability
    "LoggerPort",
    "NullLogger",
    "NotificationPort",
    "InMemoryEventBus",
    "NullNotifier",
    "DomainEvent",
    "EventPayload",
    # Image Processing
    "ImageProcessingPort",
    "CachePort",
    # UI/Visual
    "OverlayPort",
    "NullOverlay",
    "CursorType",
    "AssetProviderPort",
    "NullAssetProvider",
    # Infrastructure
    "FileSystemPort",
    "RandomPort",
    "DeterministicRandom",
    "TimePort",
    "MockTime",
]

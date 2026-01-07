"""
LocalFileSystemAdapter: Standard local file system implementation of FileSystemPort.
Dependencies: os, shutil, Domain.Ports.FileSystemPort
"""

import os
import shutil

from domain.ports.store.file_system_port import FileSystemPort  # type: ignore[import-not-found]


class LocalFileSystemAdapter(FileSystemPort):  # type: ignore[misc]
    """Standard local file system implementation."""

    def read_bytes(self, path: str) -> bytes:
        with open(path, "rb") as f:
            return f.read()

    def write_bytes(self, path: str, data: bytes) -> None:
        with open(path, "wb") as f:
            f.write(data)

    def read_text(self, path: str, encoding: str = "utf-8") -> str:
        with open(path, encoding=encoding) as f:
            return f.read()

    def write_text(self, path: str, content: str, encoding: str = "utf-8") -> None:
        with open(path, "w", encoding=encoding) as f:
            f.write(content)

    def exists(self, path: str) -> bool:
        return os.path.exists(path)

    def delete(self, path: str) -> None:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)

    def list_directory(self, path: str) -> list[str]:
        return os.listdir(path)

    def create_directory(self, path: str) -> None:
        os.makedirs(path, exist_ok=True)

    def join_path(self, *parts: str) -> str:
        return os.path.join(*parts)

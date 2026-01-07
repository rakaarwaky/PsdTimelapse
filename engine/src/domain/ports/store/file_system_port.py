"""
FileSystemPort: Interface for file I/O operations.
Dependencies: None (Pure Port)
"""

from abc import ABC, abstractmethod


class FileSystemPort(ABC):
    """
    Port interface for file system operations.

    Abstracts file I/O for testability and portability.

    Adapters implementing this port:
    - local_file_system.py (standard disk I/O)
    - memory_file_system.py (in-memory for testing)
    - s3_file_system.py (cloud storage)
    """

    @abstractmethod
    def read_bytes(self, path: str) -> bytes:
        """
        Read file contents as bytes.

        Args:
            path: File path.

        Returns:
            File contents as bytes.

        Raises:
            FileNotFoundError: If file doesn't exist.
        """
        pass

    @abstractmethod
    def write_bytes(self, path: str, data: bytes) -> None:
        """
        Write bytes to file.

        Args:
            path: File path.
            data: Bytes to write.
        """
        pass

    @abstractmethod
    def read_text(self, path: str, encoding: str = "utf-8") -> str:
        """
        Read file contents as text.

        Args:
            path: File path.
            encoding: Text encoding.

        Returns:
            File contents as string.
        """
        pass

    @abstractmethod
    def write_text(self, path: str, content: str, encoding: str = "utf-8") -> None:
        """
        Write text to file.

        Args:
            path: File path.
            content: Text to write.
            encoding: Text encoding.
        """
        pass

    @abstractmethod
    def exists(self, path: str) -> bool:
        """
        Check if path exists.

        Args:
            path: File or directory path.

        Returns:
            True if path exists.
        """
        pass

    @abstractmethod
    def delete(self, path: str) -> None:
        """
        Delete file or directory.

        Args:
            path: Path to delete.
        """
        pass

    @abstractmethod
    def list_directory(self, path: str) -> list[str]:
        """
        List directory contents.

        Args:
            path: Directory path.

        Returns:
            List of filenames in directory.
        """
        pass

    @abstractmethod
    def create_directory(self, path: str) -> None:
        """
        Create directory (including parents).

        Args:
            path: Directory path to create.
        """
        pass

    @abstractmethod
    def join_path(self, *parts: str) -> str:
        """
        Join path components.

        Args:
            parts: Path components.

        Returns:
            Joined path string.
        """
        pass

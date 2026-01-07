import os
import shutil


def create_hold_reference(source_path: str, target_path: str) -> None:
    """
    Create reference for hold frame.
    Tries symlink first, falls back to copy.
    """
    if os.path.exists(target_path):
        os.remove(target_path)
    try:
        os.symlink(source_path, target_path)
    except OSError:
        # Fallback to copy if symlink not supported
        shutil.copy2(source_path, target_path)

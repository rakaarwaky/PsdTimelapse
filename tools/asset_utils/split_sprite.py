#!/usr/bin/env python3
"""
Sprite Sheet Splitter - High Accuracy
Splits a sprite sheet into individual icons using Pillow's crop() method.
"""

import os
import sys

from PIL import Image


def split_sprite_sheet(
    sprite_path: str,
    output_dir: str,
    cols: int,
    rows: int,
    output_size: tuple = None,
    prefix: str = "icon",
) -> list:
    """
    Split sprite sheet into individual icons with high accuracy.

    Args:
        sprite_path: Path to sprite sheet PNG
        output_dir: Directory to save individual icons
        cols: Number of columns in sprite sheet
        rows: Number of rows in sprite sheet
        output_size: Optional tuple (width, height) to resize icons
        prefix: Filename prefix for output icons

    Returns:
        List of saved file paths
    """
    # Load sprite sheet
    img = Image.open(sprite_path).convert("RGBA")
    sheet_width, sheet_height = img.size

    # Calculate cell dimensions
    cell_width = sheet_width // cols
    cell_height = sheet_height // rows

    print(f"Sprite sheet: {sheet_width}x{sheet_height}")
    print(f"Grid: {cols}x{rows}")
    print(f"Cell size: {cell_width}x{cell_height}")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    saved_files = []
    count = 0

    for row in range(rows):
        for col in range(cols):
            # Calculate crop box (left, upper, right, lower)
            left = col * cell_width
            upper = row * cell_height
            right = left + cell_width
            lower = upper + cell_height

            # Crop icon
            icon = img.crop((left, upper, right, lower))

            # Optional: Resize for consistency
            if output_size:
                icon = icon.resize(output_size, Image.Resampling.LANCZOS)

            # Save icon
            filename = f"{prefix}_{count:02d}.png"
            filepath = os.path.join(output_dir, filename)
            icon.save(filepath, "PNG")
            saved_files.append(filepath)

            print(f"  Saved: {filename} (crop: {left},{upper},{right},{lower})")
            count += 1

    return saved_files


def auto_detect_grid(sprite_path: str, min_gap: int = 2) -> tuple:
    """
    Auto-detect grid by finding transparent/same-color gaps.
    Returns (cols, rows) tuple.
    """
    img = Image.open(sprite_path).convert("RGBA")
    width, height = img.size

    # Sample horizontal line at middle
    h_gaps = []
    mid_y = height // 2
    last_alpha = None
    gap_start = None

    for x in range(width):
        pixel = img.getpixel((x, mid_y))
        alpha = pixel[3] if len(pixel) == 4 else 255

        if alpha < 50:  # Transparent
            if gap_start is None:
                gap_start = x
        else:
            if gap_start is not None and (x - gap_start) >= min_gap:
                h_gaps.append((gap_start, x))
            gap_start = None

    # Similar for vertical
    v_gaps = []
    mid_x = width // 2
    gap_start = None

    for y in range(height):
        pixel = img.getpixel((mid_x, y))
        alpha = pixel[3] if len(pixel) == 4 else 255

        if alpha < 50:
            if gap_start is None:
                gap_start = y
        else:
            if gap_start is not None and (y - gap_start) >= min_gap:
                v_gaps.append((gap_start, y))
            gap_start = None

    cols = len(h_gaps) + 1
    rows = len(v_gaps) + 1

    return cols, rows


if __name__ == "__main__":
    # Default paths
    sprite_path = "src/assets/ui_icons/toolbar/toolbar_icons.png"
    output_dir = "src/assets/ui_icons/toolbar/split"

    # Parse arguments
    if len(sys.argv) >= 2:
        sprite_path = sys.argv[1]
    if len(sys.argv) >= 3:
        output_dir = sys.argv[2]

    # For toolbar_icons.png: 4 cols x 3 rows (12 icons total)
    cols, rows = 4, 3

    print(f"\n🔨 Splitting: {sprite_path}")
    print(f"📁 Output: {output_dir}")
    print(f"📐 Grid: {cols}x{rows}\n")

    files = split_sprite_sheet(
        sprite_path=sprite_path,
        output_dir=output_dir,
        cols=cols,
        rows=rows,
        output_size=(64, 64),  # Resize to 64x64 for crisp icons
        prefix="tool",
    )

    print(f"\n✅ Split complete! {len(files)} icons saved.")

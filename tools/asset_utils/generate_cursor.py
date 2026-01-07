from PIL import Image, ImageDraw


def generate_macos_cursor(output_path="macos_cursor.png"):
    """
    Generates a macOS-style mouse cursor (Black Arrow with White Outline).
    Actually, macOS default is Black with White outline (or vice versa depending on mode).
    Standard pointer: Black fill, White outline, Drop shadow.
    """
    # Size 64x64 for good quality
    W, H = 64, 64
    # Create valid RGBA image
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Coordinates for the arrow
    # Tip at (0,0) usually, but let's give some padding for shadow
    # Let's say tip at (4, 4)
    tip = (4, 4)

    # Path points (Approximate macOS cursor shape)
    # Stem is slightly tilted
    points = [
        tip,  # Tip
        (4, 28),  # Left corner
        (10, 22),  # Notch
        (14, 32),  # Stem Left
        (18, 30),  # Stem Bottom
        (14, 20),  # Stem Right
        (22, 20),  # Right Corner
    ]

    # 1. Drop Shadow (Blurred Black)
    shadow_offset = (1, 2)
    shadow_pts = [(p[0] + shadow_offset[0], p[1] + shadow_offset[1]) for p in points]

    # Draw shadow first
    shadow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d_shadow = ImageDraw.Draw(shadow_layer)
    d_shadow.polygon(shadow_pts, fill=(0, 0, 0, 80))
    # Gaussian blur the shadow
    # simple approx: draw larger semi-transparent polygon

    # 2. White Outline (Stroke)
    # Draw larger white polygon behind
    outline_pts = []
    # Simple expansion or just draw thick line
    draw.polygon(points, fill=(255, 255, 255, 255))
    draw.line(points + [points[0]], fill=(255, 255, 255, 255), width=4, joint="curve")

    # 3. Black Fill (Main)
    # Scale points slightly down? No, standard is 1px white border usually.
    # Let's simple draw black polygon on top
    draw.polygon(points, fill=(0, 0, 0, 255))

    # Add shadow layer behind (compositing)
    # Actually shadow is complex, let's stick to clean cursor for now as user asked for "macos cursor"
    # Basic shape: Black arrow, White outline.

    img.save(output_path)
    print(f"Cursor saved to {output_path}")


if __name__ == "__main__":
    generate_macos_cursor("engine/tests/assets/macos_cursor.png")

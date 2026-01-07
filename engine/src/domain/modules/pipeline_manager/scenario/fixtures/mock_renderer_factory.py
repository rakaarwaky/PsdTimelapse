import os
from PIL import Image, ImageDraw

class MockRenderer:
    def __init__(self, asset_dir=None):
        # Handle optional asset dir for cursor loading
        self.cursor_img = None
        if asset_dir:
            cursor_path = os.path.join(asset_dir, 'assets/macos_cursor.png')
            try:
                self.cursor_img = Image.open(cursor_path).convert('RGBA')
            except FileNotFoundError:
                # Silently fail or log warning if needed, but keeping it simple for mock
                pass

    def render_cursor(self, layers, cursor_state, frame):
        if not cursor_state or not cursor_state.position: return
        pos = cursor_state.position
        
        if self.cursor_img:
            x, y = int(pos.x), int(pos.y)
            try:
                frame.paste(self.cursor_img, (x, y), self.cursor_img)
            except Exception:
                pass
        else:
            # Fallback circle cursor
            d = ImageDraw.Draw(frame)
            r = 10
            d.ellipse([pos.x-r, pos.y-r, pos.x+r, pos.y+r], outline=(255, 0, 0, 255), width=3)


class DynamicCursorRenderer:
    """Renders the dynamic cursor (Hand/Brush) onto the canvas content."""
    def render_cursor(self, layer_list, cursor_state, frame):
        if not cursor_state or not cursor_state.position: return
        pos = cursor_state.position
        
        d = ImageDraw.Draw(frame)
        # Simple Cursor Triangle (White with black outline)
        points = [
            (pos.x, pos.y), 
            (pos.x, pos.y + 20), 
            (pos.x + 12, pos.y + 12)
        ]
        d.polygon(points, fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))

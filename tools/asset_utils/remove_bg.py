
from PIL import Image
import os
import glob

def process_image(path):
    print(f"Processing {path}...")
    img = Image.open(path).convert("RGBA")
    data = img.getdata()
    
    new_data = []
    for item in data:
        # item is (r, g, b, a)
        r, g, b, a = item
        
        # Check if it's dark (Background)
        # Assuming background is dark grey/black
        # Threshold: 60
        if r < 60 and g < 60 and b < 60:
            # Make Transparent
            new_data.append((0, 0, 0, 0))
        else:
            # It's an Icon Pixel
            # Make it Pure White, keep original alpha (or maybe boost alpha?)
            # Usually we want solid white icon.
            # But edges might be anti-aliased. 
            # If we just set 255,255,255,a it keeps anti-aliasing if A came from somewhere useful.
            # But here A is 255 for everything.
            # So we rely on intensity as alpha?
            # If it's a greyscale image, Brightness ~ Alpha?
            
            # Strategy: Set RGB to 255,255,255. Set Alpha based on brightness?
            # Or just keep it opaque white if it was bright?
            # Let's keep it simple: Make it White (255,255,255).
            # If it was dim (e.g. 100), making it 255 might be too harsh if it was anti-aliasing.
            # But for 512x512 icons, binary threshold might be jagged.
            
            # Better strategy for high quality: 
            # Use Lightness as Alpha.
            # Pixel (L, L, L) -> White (255, 255, 255) with Alpha = L
            
            # Only do this if we are sure it's white-on-black source.
            # Let's try simple threshold first + White. 
            # If r,g,b > 60 -> White (255, 255, 255, 255)
            # This might look jagged.
            
            # Lets stick to: preserve existing alpha (255) but set color to White.
            # But the input has max 213 (Module output).
            # Let's set it to (255, 255, 255, 255) for now.
            new_data.append((255, 255, 255, 255))
            
    img.putdata(data)
    img.save(path, "PNG")

def main():
    dirs = [
        'src/assets/ui_icons/toolbar',
        'src/assets/ui_icons/layers'
    ]
    
    for d in dirs:
        if not os.path.exists(d):
            continue
            
        files = glob.glob(os.path.join(d, "*.png"))
        for f in files:
            process_image(f)

if __name__ == "__main__":
    main()


import cv2
import numpy as np
from PIL import Image
import os
import glob
import sys

def remove_background_and_center(icon: Image.Image, threshold: int = 60, target_size: int = 512) -> Image.Image:
    """
    Remove dark background, trim, and center on a 512x512 canvas.
    """
    # 1. Remove background
    data = icon.getdata()
    new_data = []
    for pixel in data:
        if len(pixel) == 4:
            r, g, b, a = pixel
        else:
            r, g, b = pixel
            a = 255
            
        # If dark background (adjust threshold as needed)
        if r < threshold and g < threshold and b < threshold:
            new_data.append((0, 0, 0, 0))
        else:
            new_data.append((r, g, b, a))
            
    img_no_bg = Image.new('RGBA', icon.size)
    img_no_bg.putdata(new_data)
    
    # 2. Trim transparency
    bbox = img_no_bg.getbbox()
    if not bbox:
        return Image.new('RGBA', (target_size, target_size), (0,0,0,0))
    
    trimmed = img_no_bg.crop(bbox)
    
    # 3. Resize to fit in target_size (with padding)
    # We want high res, so scale up if needed, or scale down if too big
    # Since we are going 256 -> 512, we likely upscale
    
    # Desired content size within the 512 box (e.g. 400px to leave padding)
    content_size = int(target_size * 0.8)
    
    w, h = trimmed.size
    scale = min(content_size / w, content_size / h)
    
    new_w = int(w * scale)
    new_h = int(h * scale)
    
    # Upscale with LANCZOS
    resized = trimmed.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # 4. Center on canvas
    canvas = Image.new('RGBA', (target_size, target_size), (0, 0, 0, 0))
    x = (target_size - new_w) // 2
    y = (target_size - new_h) // 2
    canvas.paste(resized, (x, y), resized)
    
    return canvas

def denoise_image(pil_img: Image.Image) -> Image.Image:
    """Apply OpenCV Non-Local Means Denoising to RGBA image."""
    r, g, b, a = pil_img.split()
    rgb_img = Image.merge('RGB', (r, g, b))
    
    cv_img = cv2.cvtColor(np.array(rgb_img), cv2.COLOR_RGB2BGR)
    
    # Denoise
    denoised = cv2.fastNlMeansDenoisingColored(cv_img, None, 8, 8, 7, 21)
    
    denoised_rgb = cv2.cvtColor(denoised, cv2.COLOR_BGR2RGB)
    denoised_pil = Image.fromarray(denoised_rgb)
    
    return Image.merge('RGBA', (*denoised_pil.split(), a))

def process_sprite_sheet(filepath, output_dir, name_prefix, cols=4, rows=4, inset=0):
    print(f"Processing {filepath}...")
    
    img = Image.open(filepath).convert('RGBA')
    w, h = img.size
    cell_w, cell_h = w // cols, h // rows
    
    os.makedirs(output_dir, exist_ok=True)
    
    count = 0
    for row in range(rows):
        for col in range(cols):
            # Crop
            left = col * cell_w + inset
            upper = row * cell_h + inset
            right = (col + 1) * cell_w - inset
            lower = (row + 1) * cell_h - inset
            
            icon = img.crop((left, upper, right, lower))
            
            # Clean (remove bg) + Upscale + Center
            clean_upscaled = remove_background_and_center(icon, threshold=50, target_size=512)
            
            # Denoise
            final = denoise_image(clean_upscaled)
            
            # Save
            filename = f"{name_prefix}_{count:02d}.png"
            final.save(os.path.join(output_dir, filename))
            print(f"  Saved {filename}")
            count += 1
            
if __name__ == '__main__':
    # 1. Layer Icons
    process_sprite_sheet(
        'src/assets/ui_icons/layer_icons.png',
        'src/assets/ui_icons/layers/denoised512',
        'layer',
        cols=4, rows=4, inset=0
    )
    
    # 2. Sidebar Icons
    process_sprite_sheet(
        'src/assets/ui_icons/sidebar_icons.png',
        'src/assets/ui_icons/sidebar/denoised512',
        'sidebar',
        cols=4, rows=4, inset=0
    )

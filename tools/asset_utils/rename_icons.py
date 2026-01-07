
import os
import shutil

def rename_icons():
    base_dir = 'src/assets/ui_icons'
    
    # 1. TOOLBAR
    # Location: We suspect src/assets/ui_icons/toolbar/denoised512 or just toolbar
    # Let's find tool_00.png
    toolbar_map = {
        'tool_00.png': 'icon_move.png',
        'tool_01.png': 'icon_marquee.png',
        'tool_02.png': 'icon_lasso.png',
        'tool_03.png': 'icon_wand.png',
        'tool_04.png': 'icon_crop.png',
        'tool_05.png': 'icon_brush.png',
        'tool_06.png': 'icon_eraser.png',
        'tool_07.png': 'icon_gradient.png',
        'tool_08.png': 'icon_text.png',
        'tool_09.png': 'icon_eyedropper.png',
        'tool_10.png': 'icon_hand.png',
        'tool_11.png': 'icon_zoom.png',
         # Assuming these might exist (standard PS toolbar slots)
        'tool_12.png': 'icon_extras_1.png',
        'tool_13.png': 'icon_extras_2.png',
        'tool_14.png': 'icon_extras_3.png',
        'tool_15.png': 'icon_extras_4.png',
    }
    
    # scan for toolbar dir
    toolbar_dir = None
    for root, dirs, files in os.walk(os.path.join(base_dir, 'toolbar')):
        if 'tool_00.png' in files:
            toolbar_dir = root
            break
            
    if toolbar_dir:
        print(f"Found Toolbar icons in: {toolbar_dir}")
        for old, new in toolbar_map.items():
            old_path = os.path.join(toolbar_dir, old)
            new_path = os.path.join(toolbar_dir, new)
            if os.path.exists(old_path):
                os.rename(old_path, new_path)
                print(f"  Renamed {old} -> {new}")
    else:
        print("Could not find toolbar icons!")

    # 2. SIDEBAR
    sidebar_map = {
        'sidebar_00.png': 'icon_layers.png',
        'sidebar_01.png': 'icon_properties.png',
        'sidebar_02.png': 'icon_color.png',
        'sidebar_03.png': 'icon_history.png',
        'sidebar_04.png': 'icon_add.png',
    }
    
    sidebar_dir = None
    for root, dirs, files in os.walk(os.path.join(base_dir, 'sidebar')):
        if 'sidebar_00.png' in files:
            sidebar_dir = root
            break
            
    if sidebar_dir:
        print(f"Found Sidebar icons in: {sidebar_dir}")
        for old, new in sidebar_map.items():
            old_path = os.path.join(sidebar_dir, old)
            new_path = os.path.join(sidebar_dir, new)
            if os.path.exists(old_path):
                os.rename(old_path, new_path)
                print(f"  Renamed {old} -> {new}")
    else:
         print("Could not find sidebar icons!")


    # 3. LAYERS
    layer_map = {
        'layer_00.png': 'icon_eye.png',
        'layer_10.png': 'icon_link.png',
        'layer_11.png': 'icon_fx.png',
        'layer_12.png': 'icon_mask.png',
        'layer_13.png': 'icon_adjustment.png',
        'layer_14.png': 'icon_group.png',
        'layer_15.png': 'icon_delete.png',
    }
    
    layer_dir = None
    for root, dirs, files in os.walk(os.path.join(base_dir, 'layers')):
        if 'layer_00.png' in files:
            layer_dir = root
            break
            
    if layer_dir:
        print(f"Found Layer icons in: {layer_dir}")
        for old, new in layer_map.items():
            old_path = os.path.join(layer_dir, old)
            new_path = os.path.join(layer_dir, new)
            if os.path.exists(old_path):
                os.rename(old_path, new_path)
                print(f"  Renamed {old} -> {new}")
    else:
        print("Could not find layer icons!")

if __name__ == '__main__':
    rename_icons()

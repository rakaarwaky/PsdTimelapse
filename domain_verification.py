import os
import sys

print(f"DEBUG: Current cwd: {os.getcwd()}")
print(f"DEBUG: sys.path: {sys.path}")

# Add repo root to path
sys.path.append("/home/rakaarwaky/Work/App Project/client-app")

try:
    print("DEBUG: Importing engine...")
    import engine

    print(f"DEBUG: engine: {engine}")

    print("DEBUG: Importing engine.src...")
    import engine.src

    print(f"DEBUG: engine.src: {engine.src}")

    print("DEBUG: Importing engine.src.domain...")
    from engine.src import domain

    print(f"DEBUG: engine.src.domain: {domain}")

    expected_attributes = [
        # Entities
        "LayerEntity",
        "SceneEntity",
        "SmartAction",
        # Value Objects
        "Vector2",
        "Color",
        # Ports
        "PsdPort",
        "RendererPort",
        "ExrExportPort",
        # Core
        "ProducerEngine",
        # Modules
        "AnimationController",
        "DirectorEngine",
    ]

    missing = []
    for attr in expected_attributes:
        if not hasattr(domain, attr):
            missing.append(attr)

    if missing:
        print(f"FAILED: Missing exports: {missing}")
        sys.exit(1)

    print("SUCCESS: All expected attributes found in domain package.")

except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)

import os
import sys

# 1. Check Dependencies
try:
    import bezier
    import numpy
    import psd_tools
    from PIL import Image
    import moviepy
    # Check local module import
    from src.domain.modules.animator.bezier_solver_module import cubic_bezier
except ImportError as e:
    print(f"CRITICAL ERROR: Missing dependency. {e}")
    sys.exit(1)

# 2. Check Configuration Files
required_files = ['pyproject.toml', '.pre-commit-config.yaml', '.importlinter']
missing_files = [f for f in required_files if not os.path.exists(f)]

if missing_files:
    print(f"ERROR: Missing configuration files: {missing_files}")
    sys.exit(1)

print("SUCCESS: \n- All dependencies installed.\n- Configuration files present.\n- Environment ready for development.")

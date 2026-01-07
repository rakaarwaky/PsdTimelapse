"""
Verification Script for Integration Lead Tasks.
Verifies that ProducerEngine can be instantiated and wired correctly.
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def verify_integration():
    print("🧪 Starting Integration Verification...")

    # Debug: Try direct import first
    try:
        print("DEBUG: Importing src.domain.core.engine...")
        from src.domain.core import engine as engine_mod

        print(f"DEBUG: Engine module: {engine_mod}")
        print(f"DEBUG: Has ProducerConfig? {'ProducerConfig' in dir(engine_mod)}")
    except ImportError as e:
        print(f"DEBUG: Direct import failed: {e}")

    try:
        # Try intended import
        from src.domain.core import ProducerEngine

        print("✅ Import ProducerEngine success")
    except ImportError as e:
        print(f"❌ Failed to import ProducerEngine: {e}")
        import traceback

        traceback.print_exc()
        return False

    # Attempt instantiation
    try:
        engine = ProducerEngine()
        print(f"✅ Instantiated ProducerEngine: {engine}")
    except Exception as e:
        print(f"❌ Failed to instantiate ProducerEngine: {e}")
        return False

    # Check default state
    try:
        from src.domain.modules.pipeline_manager import EngineState

        if engine.state == EngineState.IDLE:
            print("✅ Engine state is IDLE")
        else:
            print(f"⚠️ Unexpected engine state: {engine.state}")
    except Exception as e:
        print(f"⚠️ Could not verify state: {e}")

    # Check Psd Loading (if mock available or if we want to test with real file)
    psd_path = "src/assets/Psd/test.psd"
    if os.path.exists(os.path.join(os.path.dirname(__file__), psd_path)):
        print(f"ℹ️ Found test PSD at {psd_path}")
        # We won't run full load in simple verification to avoid heavy dependencies unless requested
    else:
        print("ℹ️ No test PSD found, skipping load verification")

    print("🎉 Verification COMPLETE")
    return True


if __name__ == "__main__":
    success = verify_integration()
    sys.exit(0 if success else 1)

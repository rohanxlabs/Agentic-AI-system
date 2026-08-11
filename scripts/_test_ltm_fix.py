#!/usr/bin/env python3
"""Verify sentence-transformers import is fixed."""

import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_ltm_import():
    """Test that LTM can load embedder without errors."""
    try:
        from memory.long_term import LongTermMemory
        print("✓ LongTermMemory imported successfully")
        
        # Create a test LTM instance
        ltm = LongTermMemory("test_memory.json")
        print("✓ LTM instance created successfully")
        
        # Test embedder loading
        ltm._load_embedder()
        print("✓ Embedder loaded successfully")
        
        # Test save/recall (without actual embedding if model takes time)
        ltm.save("Test memory entry")
        print("✓ LTM save works")
        
        # Clean up test file
        import os
        if os.path.exists("test_memory.json"):
            os.remove("test_memory.json")
            print("✓ Test file cleaned up")
        
        print("\n✅ All LTM checks passed — sentence-transformers is installed correctly")
        return 0
        
    except ModuleNotFoundError as e:
        print(f"❌ FAILED: {e}")
        print("\nsentence-transformers is not installed.")
        print("Run: pip install sentence-transformers==3.3.1")
        return 1
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(test_ltm_import())

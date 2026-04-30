# /**************************************************************************/
# /*  test_runner.py                                                        */
# /**************************************************************************/

"""Test runner for Aseprite Lua tests."""

import sys
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path (parent of engine folder)
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from engine.tools.pixel_art_editor.scripting import run_lua_test

import logging



logger = logging.getLogger(__name__)

def run_all_tests(test_dir: Path) -> List[Dict[str, Any]]:
    """Run all Lua tests in directory."""
    results = []
    
    if not test_dir.exists():
        print(f"Test directory not found: {test_dir}")
        return results
    
    lua_files = sorted(test_dir.glob("*.lua"))
    print(f"Found {len(lua_files)} test files")
    
    for i, lua_file in enumerate(lua_files, 1):
        print(f"\n[{i}/{len(lua_files)}] Running {lua_file.name}...")
        
        result = run_lua_test(lua_file)
        results.append(result)
        
        if result["success"]:
            print(f"  [PASS]")
        else:
            print(f"  [FAIL] {result.get('error', 'Unknown error')}")
        
        if result.get("output"):
            for line in result["output"].split("\n"):
                print(f"    {line}")
    
    return results


def print_summary(results: List[Dict[str, Any]]) -> None:
    """Print test summary."""
    passed = sum(1 for r in results if r["success"])
    failed = len(results) - passed
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Total:  {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print("=" * 50)
    
    if failed > 0:
        print("\nFailed tests:")
        for r in results:
            if not r["success"]:
                print(f"  - {r['file']}: {r.get('error', '')}")
        sys.exit(1)
    else:
        print("\nAll tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    # Default test directory
    test_dir = Path(__file__).resolve().parent.parent.parent.parent.parent / "tests" / "scripts"
    
    print("=" * 50)
    print("Aseprite Lua Test Runner")
    print("=" * 50)
    print(f"Test directory: {test_dir}")
    
    results = run_all_tests(test_dir)
    print_summary(results)

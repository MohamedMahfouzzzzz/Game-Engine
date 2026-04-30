# /**************************************************************************/
# /*  run_tests.py                                                          */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Python runner for Lua script tests.

Executes Lua test files using the engine's Lua runtime.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from engine.tools.pixel_art_editor.scripting import AsepriteAPI
from engine.tools.pixel_art_editor.scripting.api.lua_wrapper import run_lua_test


class LuaTestRunner:
    """Runner for Lua API tests."""
    
    def __init__(self):
        self.scripts_dir = Path(__file__).parent
        self.results = []
    
    def run_test_file(self, filename: str) -> bool:
        """Run a single Lua test file."""
        test_path = self.scripts_dir / filename
        
        if not test_path.exists():
            print(f"❌ Test file not found: {filename}")
            return False
        
        print(f"\n{'='*60}")
        print(f"Running: {filename}")
        print('='*60)
        
        try:
            # Read the Lua test file
            lua_code = test_path.read_text(encoding='utf-8')
            
            # Execute via Lua runtime
            result = run_lua_test(lua_code)
            
            # Check if test passed (based on output)
            passed = "FAIL" not in str(result) and result is not False
            
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"Result: {status}")
            
            self.results.append({
                'file': filename,
                'passed': passed,
                'result': result
            })
            
            return passed
            
        except Exception as e:
            print(f"✗ ERROR: {e}")
            self.results.append({
                'file': filename,
                'passed': False,
                'error': str(e)
            })
            return False
    
    def run_all_tests(self) -> bool:
        """Run all Lua test files."""
        test_files = [
            'test_sprite_api.lua',
            'test_color_api.lua',
            'test_geometry_api.lua',
            'test_app_api.lua',
        ]
        
        print("\n" + "="*60)
        print("  GAME ENGINE LUA API TEST RUNNER")
        print("="*60)
        
        all_passed = True
        
        for test_file in test_files:
            if not self.run_test_file(test_file):
                all_passed = False
        
        # Summary
        print("\n" + "="*60)
        print("  TEST SUMMARY")
        print("="*60)
        
        passed_count = sum(1 for r in self.results if r['passed'])
        failed_count = len(self.results) - passed_count
        
        print(f"\nTotal: {len(self.results)} test files")
        print(f"Passed: {passed_count}")
        print(f"Failed: {failed_count}")
        
        if failed_count > 0:
            print("\nFailed tests:")
            for r in self.results:
                if not r['passed']:
                    print(f"  - {r['file']}")
        
        print("\n" + ("✓ ALL TESTS PASSED!" if all_passed else "✗ SOME TESTS FAILED"))
        
        return all_passed


def main():
    """Main entry point."""
    runner = LuaTestRunner()
    success = runner.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

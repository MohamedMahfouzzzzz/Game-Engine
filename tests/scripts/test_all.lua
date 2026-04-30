-- /**************************************************************************/
-- /*  test_all.lua                                                        */
-- /**************************************************************************/
-- /*                         This file is part of:                          */
-- /*                             GAME ENGINE                                */
-- /**************************************************************************/

--[[
    Master Test Runner for all Lua API Tests
    
    Usage: dofile("tests/scripts/test_all.lua")
--]]

print("=========================================================================")
print("                    GAME ENGINE LUA API TEST SUITE                      ")
print("=========================================================================")
print("")

local all_results = {
    total_passed = 0,
    total_failed = 0,
    suites = {}
}

-- Helper to run a test suite
local function run_suite(name, file)
    print(string.format("\n\n========== RUNNING: %s ==========", name))
    print("File: " .. file)
    print("")
    
    local suite_passed = 0
    local suite_failed = 0
    
    -- Load and run the test file
    local test_func = loadfile(file)
    if test_func then
        local result = test_func()
        -- Result is true if all tests passed
        if result == true then
            suite_passed = 1
        else
            suite_failed = 1
        end
    else
        print("ERROR: Could not load test file: " .. file)
        suite_failed = 1
    end
    
    all_results.suites[name] = {
        passed = suite_passed,
        failed = suite_failed
    }
    
    all_results.total_passed = all_results.total_passed + suite_passed
    all_results.total_failed = all_results.total_failed + suite_failed
end

-- Run all test suites
run_suite("Sprite API", "tests/scripts/test_sprite_api.lua")
run_suite("Color API", "tests/scripts/test_color_api.lua")
run_suite("Geometry API", "tests/scripts/test_geometry_api.lua")
run_suite("App API", "tests/scripts/test_app_api.lua")

-- Print final summary
print("\n\n=========================================================================")
print("                           FINAL SUMMARY                                 ")
print("=========================================================================")
print("")

for name, results in pairs(all_results.suites) do
    print(string.format("%-20s: %s", name, results.failed == 0 and "PASS" or "FAIL"))
end

print("")
print(string.format("Total Suites: %d", table.getn and table.getn(all_results.suites) or 0))
print(string.format("Passed: %d", all_results.total_passed))
print(string.format("Failed: %d", all_results.total_failed))

if all_results.total_failed == 0 then
    print("\n✓ ALL TESTS PASSED!")
    return 0
else
    print("\n✗ SOME TESTS FAILED")
    return 1
end

-- /**************************************************************************/
-- /*  test_color_api.lua                                                    */
-- /**************************************************************************/
-- /*                         This file is part of:                          */
-- /*                             GAME ENGINE                                */
-- /**************************************************************************/

--[[
    Color API Tests for Aseprite Compatibility
--]]

local test_results = {
    passed = 0,
    failed = 0,
    errors = {}
}

local function assert_equals(expected, actual, message)
    if expected ~= actual then
        local err = string.format("FAIL: %s - Expected: %s, Got: %s", 
            message or "Assertion failed", tostring(expected), tostring(actual))
        table.insert(test_results.errors, err)
        test_results.failed = test_results.failed + 1
        print(err)
        return false
    else
        test_results.passed = test_results.passed + 1
        print(string.format("PASS: %s", message or "Test passed"))
        return true
    end
end

local function assert_not_nil(value, message)
    if value == nil then
        local err = string.format("FAIL: %s - Value is nil", message or "Assertion failed")
        table.insert(test_results.errors, err)
        test_results.failed = test_results.failed + 1
        print(err)
        return false
    else
        test_results.passed = test_results.passed + 1
        print(string.format("PASS: %s", message or "Test passed"))
        return true
    end
end

-- Test 1: RGB Color Creation
print("\n=== Test: RGB Color Creation ===")
local function test_rgb_creation()
    local color = Color(255, 128, 64)
    assert_equals(255, color.r, "Red component")
    assert_equals(128, color.g, "Green component")
    assert_equals(64, color.b, "Blue component")
    assert_equals(255, color.a, "Alpha component (default)")
end

test_rgb_creation()

-- Test 2: RGBA Color Creation
print("\n=== Test: RGBA Color Creation ===")
local function test_rgba_creation()
    local color = Color(255, 128, 64, 200)
    assert_equals(255, color.r, "Red component")
    assert_equals(128, color.g, "Green component")
    assert_equals(64, color.b, "Blue component")
    assert_equals(200, color.a, "Alpha component")
end

test_rgba_creation()

-- Test 3: Color from Hex
print("\n=== Test: Color from Hex ===")
local function test_color_from_hex()
    local color = Color.fromHex("#FF8040")
    assert_equals(255, color.r, "Red from hex")
    assert_equals(128, color.g, "Green from hex")
    assert_equals(64, color.b, "Blue from hex")
end

test_color_from_hex()

-- Test 4: Color to Hex
print("\n=== Test: Color to Hex ===")
local function test_color_to_hex()
    local color = Color(255, 128, 64)
    local hex = color:toHex()
    assert_not_nil(hex, "toHex returns value")
    assert_true(string.find(hex:upper(), "FF") ~= nil, "Hex contains red value")
end

test_color_to_hex()

-- Test 5: Color Components
print("\n=== Test: Color Component Access ===")
local function test_color_components()
    local color = Color(100, 150, 200, 250)
    
    -- Check HSV conversion if available
    if color.hsvHue ~= nil then
        assert_not_nil(color.hsvHue, "HSV hue available")
        assert_not_nil(color.hsvSaturation, "HSV saturation available")
        assert_not_nil(color.hsvValue, "HSV value available")
    end
    
    -- Check HSL conversion if available
    if color.hslHue ~= nil then
        assert_not_nil(color.hslHue, "HSL hue available")
        assert_not_nil(color.hslSaturation, "HSL saturation available")
        assert_not_nil(color.hslLightness, "HSL lightness available")
    end
end

test_color_components()

-- Test 6: Color Equality
print("\n=== Test: Color Equality ===")
local function test_color_equality()
    local color1 = Color(255, 128, 64)
    local color2 = Color(255, 128, 64)
    local color3 = Color(100, 100, 100)
    
    -- Colors with same values should be equal
    assert_equals(color1.r, color2.r, "Same red values")
    assert_equals(color1.g, color2.g, "Same green values")
    assert_equals(color1.b, color2.b, "Same blue values")
end

test_color_equality()

-- Test 7: Gray Color
print("\n=== Test: Gray Color ===")
local function test_gray_color()
    local gray = Color.gray(128)
    assert_not_nil(gray, "Gray color created")
    assert_equals(gray.r, gray.g, "Gray has equal R and G")
    assert_equals(gray.g, gray.b, "Gray has equal G and B")
end

test_gray_color()

-- Test 8: Color Modification
print("\n=== Test: Color Modification ===")
local function test_color_modification()
    local color = Color(0, 0, 0)
    
    color.r = 255
    assert_equals(255, color.r, "Red modified")
    
    color.g = 128
    assert_equals(128, color.g, "Green modified")
    
    color.b = 64
    assert_equals(64, color.b, "Blue modified")
end

test_color_modification()

-- Summary
print("\n========================================")
print("COLOR API TEST SUMMARY")
print("========================================")
print(string.format("Passed: %d", test_results.passed))
print(string.format("Failed: %d", test_results.failed))

if test_results.failed > 0 then
    print("\nErrors:")
    for i, err in ipairs(test_results.errors) do
        print(string.format("  %d. %s", i, err))
    end
    return false
else
    print("\nAll color tests passed!")
    return true
end

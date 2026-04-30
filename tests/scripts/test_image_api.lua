-- /**************************************************************************/
-- /*  test_image_api.lua                                                    */
-- /**************************************************************************/
-- /*                         This file is part of:                          */
-- /*                             GAME ENGINE                                */
-- /**************************************************************************/

--[[
    Image API Tests for Aseprite Compatibility
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

local function assert_true(value, message)
    if not value then
        local err = string.format("FAIL: %s - Expected true", message or "Assertion failed")
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

-- Test 1: Image Creation
print("\n=== Test: Image Creation ===")
local function test_image_creation()
    local image = Image(64, 64)
    assert_not_nil(image, "Image created")
    assert_equals(64, image.width, "Image width")
    assert_equals(64, image.height, "Image height")
end

test_image_creation()

-- Test 2: Image from Sprite
print("\n=== Test: Image from Sprite ===")
local function test_image_from_sprite()
    local sprite = Sprite(32, 32)
    local cel = sprite.layers[1]:cel(1)
    
    if cel then
        assert_not_nil(cel.width, "Cel has width")
        assert_not_nil(cel.height, "Cel has height")
    end
end

test_image_from_sprite()

-- Test 3: Image Clone
print("\n=== Test: Image Clone ===")
local function test_image_clone()
    local image = Image(32, 32)
    local clone = image:clone()
    
    assert_not_nil(clone, "Clone created")
    assert_equals(image.width, clone.width, "Clone width matches")
    assert_equals(image.height, clone.height, "Clone height matches")
end

test_image_clone()

-- Test 4: Image Pixel Access
print("\n=== Test: Image Pixel Access ===")
local function test_pixel_access()
    local image = Image(16, 16)
    local color = Color(255, 128, 64)
    
    -- Set pixel
    image:putPixel(0, 0, color)
    
    -- Get pixel
    local retrieved = image:getPixel(0, 0)
    assert_not_nil(retrieved, "Pixel retrieved")
    
    if retrieved.r then
        assert_equals(color.r, retrieved.r, "Pixel red matches")
        assert_equals(color.g, retrieved.g, "Pixel green matches")
        assert_equals(color.b, retrieved.b, "Pixel blue matches")
    end
end

test_pixel_access()

-- Test 5: Image Clear
print("\n=== Test: Image Clear ===")
local function test_image_clear()
    local image = Image(16, 16)
    local color = Color(255, 0, 0)
    
    image:clear(color)
    
    -- Check pixel was cleared
    local pixel = image:getPixel(0, 0)
    if pixel and pixel.r then
        assert_equals(color.r, pixel.r, "Clear set red correctly")
    end
end

test_image_clear()

-- Test 6: Image Draw
print("\n=== Test: Image Draw ===")
local function test_image_draw()
    local dest = Image(32, 32)
    local src = Image(8, 8)
    
    src:clear(Color(255, 0, 0))
    
    -- Draw source onto destination
    dest:drawImage(src, Point(10, 10))
    
    -- Check something was drawn
    local pixel = dest:getPixel(10, 10)
    assert_not_nil(pixel, "Pixel exists at draw location")
end

test_image_draw()

-- Test 7: Image Bounds
print("\n=== Test: Image Bounds ===")
local function test_image_bounds()
    local image = Image(64, 32, ColorMode.RGB)
    
    local bounds = image.bounds
    assert_not_nil(bounds, "Image has bounds")
    assert_equals(64, bounds.width, "Bounds width")
    assert_equals(32, bounds.height, "Bounds height")
    assert_equals(0, bounds.x, "Bounds x")
    assert_equals(0, bounds.y, "Bounds y")
end

test_image_bounds()

-- Test 8: Image Color Mode
print("\n=== Test: Image Color Mode ===")
local function test_color_mode()
    local rgb_image = Image(16, 16, ColorMode.RGB)
    assert_equals(ColorMode.RGB, rgb_image.colorMode, "RGB color mode")
end

test_color_mode()

-- Test 9: Image Spec
print("\n=== Test: Image Spec ===")
local function test_image_spec()
    local image = Image(64, 64, ColorMode.RGB)
    local spec = image.spec
    
    assert_not_nil(spec, "Image has spec")
    assert_equals(64, spec.width, "Spec width")
    assert_equals(64, spec.height, "Spec height")
    assert_equals(ColorMode.RGB, spec.colorMode, "Spec color mode")
end

test_image_spec()

-- Summary
print("\n========================================")
print("IMAGE API TEST SUMMARY")
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
    print("\nAll image tests passed!")
    return true
end

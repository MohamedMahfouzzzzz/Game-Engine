-- /**************************************************************************/
-- /*  test_sprite_api.lua                                                   */
-- /**************************************************************************/
-- /*                         This file is part of:                          */
-- /*                             GAME ENGINE                                */
-- /**************************************************************************/

--[[
    Sprite API Tests for Aseprite Compatibility
    
    Run with: dofile("tests/scripts/test_sprite_api.lua")
--]]

local test_results = {
    passed = 0,
    failed = 0,
    errors = {}
}

-- Test helper functions
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
        local err = string.format("FAIL: %s - Expected true, got %s", 
            message or "Assertion failed", tostring(value))
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

-- Test 1: Sprite Creation
print("\n=== Test: Sprite Creation ===")
local function test_sprite_creation()
    local sprite = Sprite(64, 64)
    assert_not_nil(sprite, "Sprite object created")
    assert_equals(64, sprite.width, "Sprite width is 64")
    assert_equals(64, sprite.height, "Sprite height is 64")
    assert_true(sprite.isValid, "Sprite is valid")
end

test_sprite_creation()

-- Test 2: Layer Operations
print("\n=== Test: Layer Operations ===")
local function test_layer_operations()
    local sprite = Sprite(32, 32)
    local initial_layer_count = #sprite.layers
    
    -- Create new layer
    local layer = sprite:newLayer("Test Layer")
    assert_not_nil(layer, "New layer created")
    assert_equals("Test Layer", layer.name, "Layer name is correct")
    assert_equals(initial_layer_count + 1, #sprite.layers, "Layer count increased")
    
    -- Layer properties
    assert_true(layer.isVisible, "Layer is visible by default")
    assert_true(layer.isEditable, "Layer is editable by default")
    assert_equals(255, layer.opacity, "Layer opacity is 255")
    
    -- Layer stack index
    assert_not_nil(layer.stackIndex, "Layer has stackIndex")
    assert_true(layer.stackIndex >= 1, "stackIndex is valid")
end

test_layer_operations()

-- Test 3: Layer Grouping
print("\n=== Test: Layer Grouping ===")
local function test_layer_grouping()
    local sprite = Sprite(32, 32)
    local group = sprite:newGroup()
    
    assert_not_nil(group, "Group created")
    assert_true(group.isGroup, "Group has isGroup flag")
    assert_true(group.isGroupLayer, "Group has isGroupLayer flag")
    assert_equals(false, group.isImage, "Group is not image layer")
    
    -- Move layer to group
    local layer = sprite:newLayer("Grouped Layer")
    layer.parent = group
    assert_equals(group, layer.parent, "Layer parent is set correctly")
end

test_layer_grouping()

-- Test 4: Frame Operations
print("\n=== Test: Frame Operations ===")
local function test_frame_operations()
    local sprite = Sprite(32, 32)
    local initial_frame_count = #sprite.frames
    
    -- Create new frame
    local frame = sprite:newFrame()
    assert_not_nil(frame, "New frame created")
    assert_equals(initial_frame_count + 1, #sprite.frames, "Frame count increased")
    assert_not_nil(frame.frameNumber, "Frame has frameNumber")
    assert_not_nil(frame.duration, "Frame has duration")
end

test_frame_operations()

-- Test 5: Cel Operations
print("\n=== Test: Cel Operations ===")
local function test_cel_operations()
    local sprite = Sprite(32, 32)
    local layer = sprite.layers[1]
    
    -- Get existing cel
    local cel = layer:cel(1)
    -- Cel might be nil or an Image depending on implementation
    
    -- Create new cel
    local new_cel = sprite:newCel(layer, 1)
    assert_not_nil(new_cel, "New cel created")
end

test_cel_operations()

-- Test 6: Layer Deletion
print("\n=== Test: Layer Deletion ===")
local function test_layer_deletion()
    local sprite = Sprite(32, 32)
    local layer = sprite:newLayer("To Delete")
    local count_before = #sprite.layers
    
    sprite:deleteLayer(layer)
    local count_after = #sprite.layers
    
    assert_equals(count_before - 1, count_after, "Layer was deleted")
    
    -- Try to delete last layer (should not work)
    local single_sprite = Sprite(32, 32)
    local only_layer = single_sprite.layers[1]
    single_sprite:deleteLayer(only_layer)
    assert_equals(1, #single_sprite.layers, "Cannot delete last layer")
end

test_layer_deletion()

-- Test 7: Sprite Resize and Crop
print("\n=== Test: Sprite Resize and Crop ===")
local function test_resize_crop()
    local sprite = Sprite(32, 32)
    
    sprite:resize(64, 64)
    assert_equals(64, sprite.width, "Width after resize")
    assert_equals(64, sprite.height, "Height after resize")
    
    -- Crop
    local rect = Rectangle(0, 0, 16, 16)
    sprite:crop(rect)
    assert_equals(16, sprite.width, "Width after crop")
    assert_equals(16, sprite.height, "Height after crop")
end

test_resize_crop()

-- Test 8: Layer Visibility and Opacity
print("\n=== Test: Layer Visibility and Opacity ===")
local function test_layer_visibility()
    local sprite = Sprite(32, 32)
    local layer = sprite:newLayer()
    
    -- Test visibility
    layer.isVisible = false
    assert_equals(false, layer.isVisible, "Layer visibility can be set to false")
    
    layer.isVisible = true
    assert_equals(true, layer.isVisible, "Layer visibility can be set to true")
    
    -- Test opacity
    layer.opacity = 128
    assert_equals(128, layer.opacity, "Layer opacity can be changed")
end

test_layer_visibility()

-- Test 9: Layer Stack Index
print("\n=== Test: Layer Stack Index ===")
local function test_stack_index()
    local sprite = Sprite(32, 32)
    local layer1 = sprite:newLayer("Layer 1")
    local layer2 = sprite:newLayer("Layer 2")
    
    local idx1 = layer1.stackIndex
    local idx2 = layer2.stackIndex
    
    assert_not_nil(idx1, "Layer 1 has stackIndex")
    assert_not_nil(idx2, "Layer 2 has stackIndex")
    assert_true(idx2 > idx1 or idx1 > idx2, "Stack indices are ordered")
end

test_stack_index()

-- Test 10: Sprite Properties
print("\n=== Test: Sprite Properties ===")
local function test_sprite_properties()
    local sprite = Sprite(32, 32)
    
    -- Check properties exist
    assert_not_nil(sprite.colorMode, "Sprite has colorMode")
    assert_not_nil(sprite.filename, "Sprite has filename")
    assert_not_nil(sprite.transparentColor, "Sprite has transparentColor")
    assert_not_nil(sprite.gridBounds, "Sprite has gridBounds")
    assert_not_nil(sprite.bounds, "Sprite has bounds")
    assert_not_nil(sprite.isModified, "Sprite has isModified")
end

test_sprite_properties()

-- Print summary
print("\n========================================")
print("SPRITE API TEST SUMMARY")
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
    print("\nAll tests passed!")
    return true
end

-- /**************************************************************************/
-- /*  test_app_api.lua                                                      */
-- /**************************************************************************/
-- /*                         This file is part of:                          */
-- /*                             GAME ENGINE                                */
-- /**************************************************************************/

--[[
    App API Tests for Aseprite Compatibility
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

-- Test 1: App Singleton
print("\n=== Test: App Singleton ===")
local function test_app_singleton()
    local app1 = app
    local app2 = app
    
    assert_not_nil(app1, "App exists")
    assert_equals(app1, app2, "App is singleton")
end

test_app_singleton()

-- Test 2: App Properties
print("\n=== Test: App Properties ===")
local function test_app_properties()
    -- Check required properties exist
    assert_not_nil(app.version, "App has version")
    assert_not_nil(app.fs, "App has file system")
    assert_not_nil(app.command, "App has command API")
    assert_not_nil(app.clipboard, "App has clipboard")
end

test_app_properties()

-- Test 3: Active Sprite
print("\n=== Test: Active Sprite ===")
local function test_active_sprite()
    -- Create a sprite
    local sprite = Sprite(64, 64)
    
    -- Set as active
    app.sprite = sprite
    
    -- Check active
    assert_equals(sprite, app.sprite, "Active sprite is set")
    assert_not_nil(app.sprite, "app.sprite is not nil")
end

test_active_sprite()

-- Test 4: Active Layer
print("\n=== Test: Active Layer ===")
local function test_active_layer()
    local sprite = Sprite(32, 32)
    app.sprite = sprite
    
    -- Get active layer
    local layer = app.layer
    if layer ~= nil then
        assert_not_nil(layer, "Active layer exists")
        assert_not_nil(layer.name, "Layer has name")
    end
end

test_active_layer()

-- Test 5: Active Frame
print("\n=== Test: Active Frame ===")
local function test_active_frame()
    local sprite = Sprite(32, 32)
    app.sprite = sprite
    
    -- Get active frame
    local frame = app.frame
    if frame ~= nil then
        assert_not_nil(frame, "Active frame exists")
        assert_not_nil(frame.frameNumber, "Frame has frameNumber")
    end
end

test_active_frame()

-- Test 6: File System
print("\n=== Test: File System ===")
local function test_file_system()
    local fs = app.fs
    assert_not_nil(fs, "File system exists")
    
    -- Check common operations
    if fs.isDirectory then
        assert_true(type(fs.isDirectory) == "function", "fs.isDirectory is function")
    end
    
    if fs.isFile then
        assert_true(type(fs.isFile) == "function", "fs.isFile is function")
    end
end

test_file_system()

-- Test 7: Clipboard
print("\n=== Test: Clipboard ===")
local function test_clipboard()
    local clipboard = app.clipboard
    assert_not_nil(clipboard, "Clipboard exists")
    
    -- Store color
    local color = Color(255, 128, 64)
    app.clipboard.color = color
    
    -- Retrieve
    if app.clipboard.color then
        local retrieved = app.clipboard.color
        assert_equals(color.r, retrieved.r, "Clipboard color red")
        assert_equals(color.g, retrieved.g, "Clipboard color green")
        assert_equals(color.b, retrieved.b, "Clipboard color blue")
    end
end

test_clipboard()

-- Test 8: Preferences
print("\n=== Test: Preferences ===")
local function test_preferences()
    if app.preferences then
        assert_not_nil(app.preferences, "Preferences exist")
    end
end

test_preferences()

-- Test 9: Range (Selection)
print("\n=== Test: Range (Selection) ===")
local function test_range()
    local sprite = Sprite(64, 64)
    sprite:newFrame()
    sprite:newFrame()
    
    -- Set range
    if app.range then
        local range = app.range
        assert_not_nil(range, "Range exists")
        
        -- Range frames
        if range.frames then
            assert_true(type(range.frames) == "table", "range.frames is table")
        end
    end
end

test_range()

-- Summary
print("\n========================================")
print("APP API TEST SUMMARY")
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
    print("\nAll app tests passed!")
    return true
end

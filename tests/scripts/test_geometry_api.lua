-- /**************************************************************************/
-- /*  test_geometry_api.lua                                                 */
-- /**************************************************************************/
-- /*                         This file is part of:                          */
-- /*                             GAME ENGINE                                */
-- /**************************************************************************/

--[[
    Geometry API Tests (Rectangle, Point, Size)
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

-- Test 1: Rectangle Creation
print("\n=== Test: Rectangle Creation ===")
local function test_rectangle_creation()
    local rect = Rectangle(10, 20, 100, 200)
    assert_equals(10, rect.x, "Rectangle x")
    assert_equals(20, rect.y, "Rectangle y")
    assert_equals(100, rect.width, "Rectangle width")
    assert_equals(200, rect.height, "Rectangle height")
end

test_rectangle_creation()

-- Test 2: Rectangle Properties
print("\n=== Test: Rectangle Properties ===")
local function test_rectangle_properties()
    local rect = Rectangle(10, 20, 100, 200)
    
    assert_equals(10, rect.origin.x, "Rectangle origin x")
    assert_equals(20, rect.origin.y, "Rectangle origin y")
    assert_equals(100, rect.size.width, "Rectangle size width")
    assert_equals(200, rect.size.height, "Rectangle size height")
    
    assert_equals(110, rect.x2, "Rectangle x2 (right)")
    assert_equals(220, rect.y2, "Rectangle y2 (bottom)")
end

test_rectangle_properties()

-- Test 3: Point Creation
print("\n=== Test: Point Creation ===")
local function test_point_creation()
    local point = Point(50, 75)
    assert_equals(50, point.x, "Point x")
    assert_equals(75, point.y, "Point y")
end

test_point_creation()

-- Test 4: Size Creation
print("\n=== Test: Size Creation ===")
local function test_size_creation()
    local size = Size(100, 200)
    assert_equals(100, size.width, "Size width")
    assert_equals(200, size.height, "Size height")
end

test_size_creation()

-- Test 5: Point Operations
print("\n=== Test: Point Operations ===")
local function test_point_operations()
    local p1 = Point(10, 20)
    local p2 = Point(30, 40)
    
    -- Distance
    if p1.distanceTo then
        local dist = p1:distanceTo(p2)
        assert_not_nil(dist, "Distance calculated")
        assert_true(dist > 0, "Distance is positive")
    end
    
    -- Offset
    if p1.offset then
        p1:offset(5, 10)
        assert_equals(15, p1.x, "Point offset x")
        assert_equals(30, p1.y, "Point offset y")
    end
end

test_point_operations()

-- Test 6: Rectangle Operations
print("\n=== Test: Rectangle Operations ===")
local function test_rectangle_operations()
    local rect = Rectangle(0, 0, 100, 100)
    local point = Point(50, 50)
    
    -- Contains
    if rect.contains then
        local contains = rect:contains(point)
        assert_true(contains, "Rectangle contains point")
        
        local outside = rect:contains(Point(200, 200))
        assert_equals(false, outside, "Rectangle does not contain outside point")
    end
    
    -- Intersects
    local rect2 = Rectangle(50, 50, 100, 100)
    if rect.intersects then
        local intersects = rect:intersects(rect2)
        assert_true(intersects, "Rectangles intersect")
    end
    
    -- Intersection
    if rect.intersection then
        local intersection = rect:intersection(rect2)
        assert_not_nil(intersection, "Intersection exists")
        assert_equals(50, intersection.x, "Intersection x")
        assert_equals(50, intersection.y, "Intersection y")
    end
end

test_rectangle_operations()

-- Test 7: Rectangle Inset/Offset
print("\n=== Test: Rectangle Inset/Offset ===")
local function test_rectangle_inset()
    local rect = Rectangle(0, 0, 100, 100)
    
    if rect.inset then
        rect:inset(10)
        assert_equals(10, rect.x, "Inset x")
        assert_equals(10, rect.y, "Inset y")
        assert_equals(80, rect.width, "Inset width")
        assert_equals(80, rect.height, "Inset height")
    end
    
    if rect.offset then
        rect:offset(5, 5)
        assert_equals(15, rect.x, "Offset x")
        assert_equals(15, rect.y, "Offset y")
    end
end

test_rectangle_inset()

-- Test 8: Point Equality
print("\n=== Test: Point Equality ===")
local function test_point_equality()
    local p1 = Point(10, 20)
    local p2 = Point(10, 20)
    local p3 = Point(30, 40)
    
    assert_equals(p1.x, p2.x, "Points with same x")
    assert_equals(p1.y, p2.y, "Points with same y")
    assert_equals(false, p1.x == p3.x, "Different x values")
end

test_point_equality()

-- Summary
print("\n========================================")
print("GEOMETRY API TEST SUMMARY")
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
    print("\nAll geometry tests passed!")
    return true
end

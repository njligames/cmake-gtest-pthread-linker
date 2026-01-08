mkdir -p include
mkdir -p src
mkdir -p tests

cat <<'EOF' > CMakeLists.txt
cmake_minimum_required(VERSION 3.16)
project(MyProject CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

enable_testing()

# Find Threads (pthreads)
find_package(Threads REQUIRED)

# Fetch GoogleTest automatically
include(FetchContent)

FetchContent_Declare(
    googletest
    URL https://github.com/google/googletest/archive/refs/tags/release-1.17.0.zip
)
# Prevent overriding the parent project's compiler/linker settings
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

# Main library
add_library(MyLibrary
    src/foo.cpp
)
target_include_directories(MyLibrary PUBLIC include)

# Test executable
add_executable(MyLibraryTests
    tests/test_foo.cpp
)

# Link libraries
target_link_libraries(MyLibraryTests
    PRIVATE
        MyLibrary
        GTest::GTest
        GTest::Main
        Threads::Threads
)

# Discover tests
include(GoogleTest)
gtest_discover_tests(MyLibraryTests)
EOF

cat <<'EOF' > include/foo.h
#pragma once

int add(int a, int b);
EOF

cat <<'EOF' > src/foo.cpp
#include "foo.h"

int add(int a, int b) {
    return a + b;
}
EOF

cat <<'EOF' > tests/test_foo.cpp
#include "foo.h"
#include <gtest/gtest.h>

TEST(FooTest, AddPositiveNumbers) {
    EXPECT_EQ(add(2, 3), 5);
}

TEST(FooTest, AddNegativeNumbers) {
    EXPECT_EQ(add(-2, -3), -5);
}
EOF

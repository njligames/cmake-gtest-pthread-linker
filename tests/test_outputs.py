import subprocess
import os
import re
from pathlib import Path

BUILD_DIR = Path("build")


def build_project():
    """
    Build the project using CMake or a build.sh script if present.
    """
    if Path("CMakeLists.txt").exists():
        BUILD_DIR.mkdir(exist_ok=True)
        subprocess.check_call(["cmake", "-S", ".", "-B", str(BUILD_DIR)])
        subprocess.check_call(["cmake", "--build", str(BUILD_DIR)])
    elif Path("build.sh").exists():
        subprocess.check_call(["./build.sh"])
    else:
        raise AssertionError(
            "No CMakeLists.txt or build invocation (e.g. build.sh) found"
        )


def find_test_executable():
    """
    Locate an executable produced by the build.
    """
    candidates = []
    for path in BUILD_DIR.rglob("*"):
        if path.is_file() and os.access(path, os.X_OK):
            candidates.append(path)

    assert candidates, "No executable produced by the build"
    return candidates[0]


def test_position_independent_code_enabled():
    """
    Verifies that POSITION_INDEPENDENT_CODE is set in CMake and object files are compiled with PIC.
    """
    build_project()

    # Inspect CMake cache
    cache_file = BUILD_DIR / "CMakeCache.txt"
    assert cache_file.exists(), "CMakeCache.txt not found; build likely failed"

    with open(cache_file) as f:
        cache_contents = f.read()

    pic_enabled = re.search(r"CMAKE_POSITION_INDEPENDENT_CODE:BOOL=ON", cache_contents)
    assert pic_enabled, "POSITION_INDEPENDENT_CODE is NOT enabled in CMake build"

    # Optional: verify object files have PIC flag using readelf (Linux/GCC/Clang)
    obj_files = list(BUILD_DIR.rglob("*.o"))
    assert obj_files, "No object files found to inspect for PIC"

    for obj in obj_files:
        result = subprocess.run(
            ["readelf", "-h", str(obj)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        # Type: DYN indicates PIC-compatible object
        assert "Type: DYN" in result.stdout or "REL" in result.stdout, (
            f"Object file {obj} may not be compiled with PIC"
        )


def test_explicit_gtest_main_linking():
    """
    Ensures the test executable is linked to GTest::Main.
    """
    exe = find_test_executable()
    result = subprocess.run(
        ["nm", str(exe)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    symbols = result.stdout
    assert "gtest_main" in symbols or "main" in symbols, (
        "Executable does not contain gtest_main symbols; likely not linked to GTest::Main"
    )


def test_explicit_pthread_linking():
    """
    Ensures the test executable is linked to pthread (Threads::Threads).
    """
    exe = find_test_executable()
    result = subprocess.run(
        ["ldd", str(exe)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    linked_libs = result.stdout
    assert "libpthread" in linked_libs, (
        "Executable is not linked to pthread library; likely missing Threads::Threads"
    )


def test_tests_run_successfully():
    """
    Verifies the GoogleTest tests execute and report passing.
    """
    exe = find_test_executable()
    result = subprocess.run(
        [str(exe)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=30,
    )

    # Return code 0 means all tests passed
    assert result.returncode == 0, f"Tests failed:\n{result.stdout}\n{result.stderr}"

    # Basic sanity check: GoogleTest should print test summary
    assert "FAILED" not in result.stdout, f"Some tests failed:\n{result.stdout}"
    assert "PASSED" in result.stdout, f"No tests reported passing:\n{result.stdout}"

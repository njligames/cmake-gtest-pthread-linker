import subprocess
import re
import os
from pathlib import Path

BUILD_DIR = Path("build")


def build_project():
    """
    Instruction:
    'Update CMakeLists.txt (or build invocation)'

    We support BOTH paths.
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


def find_executable():
    """
    Instruction does NOT specify binary name.
    We therefore locate any executable produced by the build.
    """
    candidates = []
    for path in BUILD_DIR.rglob("*"):
        if path.is_file() and os.access(path, os.X_OK):
            candidates.append(path)

    assert candidates, "No executable produced by the build"
    return candidates[0]


def extract_http_status(output: str):
    match = re.search(r"\b\d{3}\b", output)
    return match.group(0) if match else None


def test_builds_successfully():
    """
    Verifies the link-time issue is fixed.
    """
    build_project()
    exe = find_executable()
    assert exe.exists()


def test_connects_and_prints_http_status_code():
    """
    Instruction:
    'verify the resulting HTTPS client connects to example.com
     and prints the HTTP status code'
    """
    exe = find_executable()

    result = subprocess.run(
        [str(exe)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=15,
    )

    assert result.returncode == 0, f"Program failed:\n{result.stderr}"

    status = extract_http_status(result.stdout)
    assert status, f"No HTTP status code printed:\n{result.stdout}"


def test_requires_network_to_produce_status_code():
    """
    Minimal anti-fake check.

    If the program truly 'connects to example.com', then
    disabling networking must prevent it from producing
    an HTTP status code.

    This does NOT enforce a specific failure mode.
    """
    exe = find_executable()

    result = subprocess.run(
        ["unshare", "-n", str(exe)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=15,
    )

    status = extract_http_status(result.stdout)

    assert status is None, (
        "Program produced an HTTP status code with networking disabled; "
        "this suggests no real connection was attempted"
    )

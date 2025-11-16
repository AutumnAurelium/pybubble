"""Performance tests for sandbox creation and execution."""

import asyncio
import time
import pytest
from pybubble import Sandbox


async def run_sandbox_test(sandbox_id: int, work_dir: str, rootfs_location: str):
    """Create a sandbox, run some Python code, and clean it up."""
    sandbox = Sandbox(work_dir=work_dir, rootfs=rootfs_location)
    
    # Run some basic Python code
    code = f"""
import math
result = sum(range(1, 101))
print(f"Sandbox {sandbox_id}: Sum of 1-100 = {{result}}")
print(f"Pi approximation: {{math.pi:.4f}}")
"""
    stdout, stderr = await sandbox.run_python(code)
    
    # Cleanup
    del sandbox
    
    return stdout, stderr


@pytest.mark.asyncio
async def test_sandbox_performance():
    """Test that sandbox creation and execution overhead is under 5ms per sandbox."""
    work_dir = "work"
    rootfs_location = "work/alpine-rootfs-python.tgz"
    num_sandboxes = 100
    
    start_time = time.perf_counter()
    
    # Create and run all sandboxes in parallel
    tasks = [
        run_sandbox_test(i, work_dir, rootfs_location)
        for i in range(num_sandboxes)
    ]
    
    results = await asyncio.gather(*tasks)
    
    end_time = time.perf_counter()
    total_time = end_time - start_time
    overhead_per_sandbox = total_time / num_sandboxes
    
    # Assert that average overhead per sandbox is under 5ms
    assert overhead_per_sandbox < 0.005, (
        f"Average overhead per sandbox ({overhead_per_sandbox*1000:.2f} ms) "
        f"exceeds 5ms threshold. Total time: {total_time:.4f}s for {num_sandboxes} sandboxes."
    )
    
    # Verify that we got results for all sandboxes
    assert len(results) == num_sandboxes


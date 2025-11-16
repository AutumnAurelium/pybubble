import pytest
from pybubble import Sandbox

@pytest.mark.asyncio
async def test_sandbox():
    # TODO: Change this to pull from a location that works off of my workstation
    sandbox = Sandbox(work_dir="work", rootfs="work/alpine-rootfs-python.tgz")
    
    # Test Python and bash functionality
    assert await sandbox.run_python("print('Hello, world!')") == (b"Hello, world!\n", b"")
    assert await sandbox.run("echo 'hello!'") == (b"hello!\n", b"")
    
    # Test network access
    assert (await sandbox.run("ping -c 1 google.com", allow_network=True))[1] == b""
    
    # Test cleanup
    session_dir = sandbox.session_dir
    del sandbox
    
    assert not session_dir.exists()
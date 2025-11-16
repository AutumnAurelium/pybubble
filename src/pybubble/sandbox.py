import asyncio
from pathlib import Path
import shutil
import subprocess
import tempfile
import uuid
import shlex

from pybubble.rootfs import setup_rootfs


class Sandbox:
    def __init__(self, rootfs: str | Path, work_dir: str | Path | None = None, rootfs_path: str | Path | None = None):
        # Create temporary directory if work_dir is not provided
        if work_dir is None:
            self._temp_dir = tempfile.TemporaryDirectory(dir="/tmp")
            self.work_dir = Path(self._temp_dir.name)
        else:
            self._temp_dir = None
            self.work_dir = Path(work_dir)
        
        # Convert rootfs_path to Path if provided, otherwise None (which triggers caching)
        rootfs_path_obj = Path(rootfs_path) if rootfs_path is not None else None
        
        self.rootfs_dir = setup_rootfs(str(rootfs), rootfs_path_obj)
        
        self.uuid = str(uuid.uuid4())
        self.session_dir = self.work_dir / f"session_{self.uuid}"
        Path.mkdir(self.session_dir, parents=True, exist_ok=False)

    async def run(self, command: str, allow_network: bool = False, timeout: float = 10.0) -> tuple[bytes, bytes]:
        """Runs a shell command in the sandbox. Returns (stdout, stderr) if the command succeeds, otherwise raises an exception."""
        built_command: list[str] = [
            "bwrap",
            "--unshare-all",
            "--die-with-parent",
            "--dev", "/dev",
            "--proc", "/proc",
            "--ro-bind", shlex.quote(str(self.rootfs_dir.absolute())), "/",
            "--bind", shlex.quote(str(self.session_dir.absolute())), "/home/sandbox",
            "--setenv", "HOME", "/home/sandbox",
            "--setenv", "PATH", "/usr/bin:/bin",
            "--chdir", "/home/sandbox",
        ]
        
        if allow_network:
            # Bind system DNS config and allow network access
            built_command.extend(["--ro-bind", "/etc/resolv.conf", "/etc/resolv.conf", "--share-net"])
        
        built_command.extend(shlex.split(command))
        
        process = await asyncio.create_subprocess_exec(
            *built_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            raise TimeoutError(f"Command execution exceeded {timeout} seconds")
        
        return stdout or b"", stderr or b""

    async def run_python(self, code: str, allow_network: bool = False, timeout: float = 10.0) -> tuple[bytes, bytes]:
        """Runs a Python script in the sandbox. Returns (stdout, stderr) if the code succeeds, otherwise raises an exception."""
        
        script_path = self.session_dir / "script.py"
        with open(script_path, "w") as f:
            f.write(code)
        
        return await self.run("python script.py", allow_network, timeout)

    def __del__(self):
        """Cleanup the sandbox session directory."""
        if self.session_dir.exists():
            shutil.rmtree(self.session_dir)
        # Cleanup temporary directory if it was created
        if self._temp_dir is not None:
            self._temp_dir.cleanup()
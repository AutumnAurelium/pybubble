"""Custom build backend that wraps hatchling and builds the default rootfs."""
import os
import shutil
import subprocess
import sys
from pathlib import Path
from hatchling.build import build_sdist as _build_sdist
from hatchling.build import build_wheel as _build_wheel
try:
    from hatchling.build import build_editable as _build_editable
except ImportError:
    _build_editable = None

# Import the rootfs generation function from the source
sys.path.insert(0, str(Path(__file__).parent / "src"))
from pybubble.rootfs import generate_rootfs


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    """Build a wheel and then generate the default rootfs."""
    # First, build the wheel using hatchling
    wheel_filename = _build_wheel(wheel_directory, config_settings, metadata_directory)
    
    # After successful wheel build, generate the default rootfs
    try:
        # Get the project root directory (where build_backend.py is located)
        project_root = Path(__file__).parent.absolute()
        
        # Use absolute paths from project root
        temp_tgz = project_root / "dist" / "default.tgz"
        dockerfile = project_root / "default-rootfs.dockerfile"
        dist_dir = project_root / "dist"
        
        # Remove existing default.tgz to ensure fresh build
        if temp_tgz.exists():
            print(f"Removing existing {temp_tgz}", flush=True)
            temp_tgz.unlink()
        
        # Ensure dist directory exists
        dist_dir.mkdir(exist_ok=True)
        
        print(f"Building default rootfs from {dockerfile}...", flush=True)
        
        # Change to project root for docker context
        original_cwd = os.getcwd()
        os.chdir(project_root)
        
        try:
            generate_rootfs(dockerfile, temp_tgz, compress_level=9)
            print(f"Default rootfs built successfully at {temp_tgz}!", flush=True)
            
            # Now copy to the actual dist directory (wheel_directory parent)
            # wheel_directory is where the wheel is being built
            actual_dist = Path(wheel_directory).absolute()
            final_tgz = actual_dist / "default.tgz"
            
            print(f"Copying {temp_tgz} to {final_tgz}...", flush=True)
            shutil.copy2(temp_tgz, final_tgz)
            print(f"Default rootfs copied to {final_tgz}!", flush=True)
            
        finally:
            os.chdir(original_cwd)
            
    except Exception as e:
        print(f"Warning: Failed to build default rootfs: {e}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc()
        # Don't fail the build if rootfs generation fails
    
    return wheel_filename


def build_sdist(sdist_directory, config_settings=None):
    """Build an sdist. The rootfs will be built when build_wheel is called."""
    # Just build the sdist using hatchling
    # The rootfs generation happens in build_wheel since that's called after sdist
    return _build_sdist(sdist_directory, config_settings)


def build_editable(wheel_directory, config_settings=None, metadata_directory=None):
    """Build an editable wheel. Don't build rootfs for editable installs."""
    if _build_editable is None:
        raise NotImplementedError("Editable installs are not supported by this version of hatchling")
    
    # For editable installs, just use hatchling's editable build
    # We don't build the rootfs here since it's a development install
    return _build_editable(wheel_directory, config_settings, metadata_directory)


# Expose the required hooks for the build backend
__all__ = ['build_wheel', 'build_sdist', 'build_editable']


# pybubble

A simple wrapper around `bwrap` to create sandbox environments for executing code. It works without Docker or other daemon-based container runtimes, using shared read-only root filesystems for quick (1-2ms) setup times.

## Setup

Install `bwrap`. On Ubuntu, do:

```bash
sudo apt-get install bubblewrap
```

Install `pybubble`:

```bash
uv add pybubble
```

## Building a root filesystem archive

A root filesystem archive can be generated from any docker image. To generate a root filesystem, ensure you have docker installed and running, then run:

```bash
pybubble rootfs your.dockerfile rootfs.tgz
```

Your root filesystem archive can now be used with sandboxes. Docker does not need to be installed to use this file, only to generate it.

## Run code

Create a sandbox by doing:

```python
from pybubble import Sandbox

async def main():
    s = Sandbox("path/to/rootfs.tgz")

    stdout, stderr = await s.run("echo 'hello'")

    print(stdout.decode("utf-8")) # "hello"

    stdout, stderr = await s.run_python("print('hello, world')")

    print(stdout.decode("utf-8")) # "hello, world"

if __name__ == "__main__":
    asyncio.run(main())
```
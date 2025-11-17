# Building a custom root filesystem archive

A custom root filesystem archive can be generated from any Dockerfile. Ensure your image contains a user named "sandbox" with an empty home directory at `/home/sandbox`. Your ephemeral writable session storage will be mounted at this location.

To generate a root filesystem, ensure you have Docker installed and running, then run:

```bash
pybubble rootfs your.dockerfile rootfs.tgz
```

Your root filesystem archive can now be used with sandboxes. Docker does not need to be installed to use this file, only to generate it.
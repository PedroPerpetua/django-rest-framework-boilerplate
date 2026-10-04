## Docker file pinned versions

### Checking for apt package version
You can check the most recent versions of an apt package by running the command `docker run --rm <python image> bash -c "apt-get update && apt-cache <package>`.

The following packages should be update in the present dockerfiles:
- `uv`;
- `build-essential`;
- `libpq-dev`;
- `libpq5`;
- `nginx` (prod dockerfile only).

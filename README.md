# Alpha-Engine
An automated, multi-region WorldQuant BRAIN alpha generation and management engine.

## Releases

Pushing a `v*` tag builds a Windows executable, a macOS disk image, and Linux AppImage and Debian packages, then attaches them to a GitHub Release. These builds are currently unsigned; your operating system may warn before allowing an installer or app to open. Only install artifacts from a release you trust.

The local database is stored in the user's application-data directory: `%LOCALAPPDATA%\AlphaEngine` on Windows, `~/Library/Application Support/AlphaEngine` on macOS, and `$XDG_DATA_HOME/alpha-engine` (or `~/.local/share/alpha-engine`) on Linux. Set `ALPHA_ENGINE_DATA_DIR` to override the directory.

The app's `GET /api/updates` endpoint checks the latest stable GitHub Release and reports whether it is newer than the running app. It does not download or install updates automatically.

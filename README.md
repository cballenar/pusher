# [❯❯] PUSHER

Pusher is an interactive terminal tool that simplifies repetitive file
transfers. Ideally suited for offloading media to external drives or network
storage, it handles the heavy lifting with `rsync` while you navigate with a
friendly TUI.

- **Keeps Workflows Consistent**, e.g. Move from "Work Folder" to "Archive".
- **Safe**: Verifies checksums and cleans up source files after transfer.
- **Persistent**: Remembers your preferences in `~/.config/pusher/config.json`.
- **Linker Mode**: Optionally create symlinks instead of transferring files.

## Quick Start

Download and install the
[latest binary](https://github.com/cballenar/pusher/releases/latest) for your
architecture to `/usr/local/bin`. For example for Raspberry Pi:

```bash
# Download
sudo wget -O /usr/local/bin/pusher https://github.com/cballenar/pusher/releases/latest/download/pusher-linux-aarch64
sudo chmod +x /usr/local/bin/pusher

# Get pushing!
pusher
```

### Interface

- **First Run**: A setup wizard will guide you to select your **Source** and
  **Target** directories.
- **Navigation**: Use `hjkl` or Arrow keys. `Enter` to go into a folder,
  `Backspace` to go back.
- **Pushing Interface**:
  - `Space` to select files/folders.
  - `Enter` to **Push** or **Link** selected files/folders (requires confirmation; determined by operation mode set in Settings).
  - `s` to change **Settings** (Source/Target paths and operation mode).

### Install from Source

If you need to install from source you'll need Python/pip:

```bash
pip install .

pusher
```

## Development

```bash
# Build and Start
docker compose -f docker-compose.test.yml build

# Run Interactive Shell
docker compose -f docker-compose.test.yml run --rm app bash

# Inside the container
pusher

# Build binary
docker compose -f docker-compose.test.yml run --rm app ./build_binary.sh
```

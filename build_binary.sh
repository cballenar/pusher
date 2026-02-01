#!/bin/bash
set -e

echo "📦 Installing build dependencies..."
if [ -f /etc/debian_version ]; then
    apt-get update && apt-get install -y binutils
fi
pip install pyinstaller

echo "🔨 Building Pusher binary..."
# --onefile: Create a single executable
# --name: Name of the output binary
# --add-data: We don't have extra data files yet, but if we did, they'd go here.
# pusher/main.py: Entry point
pyinstaller --onefile --name pusher pusher/main.py --clean

echo "✅ Build complete!"
echo "🚀 Binary located at: dist/pusher"

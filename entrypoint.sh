#!/bin/bash
set -e

# Re-install in editable mode to ensure egg-info exists after volume mount
# and that changes are reflected.
if [ -f "setup.py" ]; then
    pip install -e . > /dev/null 2>&1
fi

exec "$@"

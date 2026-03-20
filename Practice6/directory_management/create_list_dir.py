import os
import sys
from pathlib import Path

if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
    base = Path(sys.argv[1])
    dir_names = sys.argv[2:]  
else:
    base = Path.cwd()
    dir_names = sys.argv[1:]

if not dir_names:
    dir_names = [line.strip() for line in sys.stdin if line.strip()]

if not dir_names:
    print("No directory names provided.")
    sys.exit(1)

for name in dir_names:
    target = base / name
    try:
        target.mkdir(parents=True, exist_ok=True)
        print(f"Created: {target}")
    except Exception as e:
        print(f"Failed to create {target}: {e}")
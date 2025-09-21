#!/usr/bin/env python3

import sys
from src import pygames

app = pygames.Application()

try:
    app.run(sys.argv[1:])
except pygames.ArgumentError as e:
    sys.stderr.write(f"error: {e}\n")
    exit(1)

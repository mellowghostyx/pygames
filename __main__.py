#!/usr/bin/env python3

import sys
from src.pygames import application

app = application.Application()

try:
    app.run(sys.argv[1:])
except application.ArgumentError as e:
    sys.stderr.write(f"error: {e}\n")
    exit(1)

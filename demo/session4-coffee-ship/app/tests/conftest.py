"""Make the Lambda source importable as ``app`` during tests.

The handler lives in ``src/app.py``; add that directory to sys.path so tests can
``import app`` the same way the Lambda runtime does (CodeUri: src/).
"""

import os
import sys

SRC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

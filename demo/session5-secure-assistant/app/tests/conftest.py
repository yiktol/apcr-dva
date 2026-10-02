"""Make the Lambda sources importable during tests.

Add the app/ root to sys.path so `assistant.pii`, `assistant.tools`,
`refund_confirm.handler`, and `presign.handler` import as packages. Each zip
Lambda's handler.py lives at its own root in the deployed runtime; the __init__
files make them importable as packages for the tests without affecting the
runtime (the deployed handler path is `handler.handler`).
"""
import os
import sys

APP_ROOT = os.path.dirname(os.path.dirname(__file__))
if APP_ROOT not in sys.path:
    sys.path.insert(0, APP_ROOT)

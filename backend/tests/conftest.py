import os

os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-only")
os.environ.setdefault("ENABLE_DEV_ENDPOINTS", "true")

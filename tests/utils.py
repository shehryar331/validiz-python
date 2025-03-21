"""Test utilities for Validiz tests."""
import os
import tempfile


def create_temp_csv_file():
    """Create a temporary CSV file for testing file uploads."""
    fd, path = tempfile.mkstemp(suffix=".csv")
    try:
        with os.fdopen(fd, "w") as tmp:
            tmp.write("email\nvalid@example.com\ninvalid@example.com\n")
        return path
    except Exception:
        os.remove(path)
        raise 
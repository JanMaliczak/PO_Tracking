#!/usr/bin/env python
import os
import sys


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "po_tracking.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django is not installed. Activate .venv and install requirements first."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

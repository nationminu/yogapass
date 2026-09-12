#!/usr/bin/env python
"""Django 관리 명령 진입점. 모든 명령은 developer/site/ 안에서 실행한다."""

import os
import sys


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

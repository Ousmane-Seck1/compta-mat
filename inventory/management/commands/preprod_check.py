from __future__ import annotations

from datetime import datetime
from pathlib import Path
import shutil

from django.conf import settings
from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = "Run pre-production checks: backup DB, check, tests, and collectstatic."

    def add_arguments(self, parser):
        parser.add_argument("--skip-backup", action="store_true", help="Skip database backup step.")
        parser.add_argument("--skip-tests", action="store_true", help="Skip test execution.")
        parser.add_argument("--skip-collectstatic", action="store_true", help="Skip collectstatic.")

    def handle(self, *args, **options):
        if not options.get("skip_backup"):
            self._backup_database()

        self.stdout.write(self.style.NOTICE("[1/3] Running Django checks..."))
        call_command("check")

        if not options.get("skip_tests"):
            self.stdout.write(self.style.NOTICE("[2/3] Running inventory tests..."))
            call_command("test", "inventory.tests")
        else:
            self.stdout.write(self.style.WARNING("[2/3] Tests skipped by option."))

        if not options.get("skip_collectstatic"):
            self.stdout.write(self.style.NOTICE("[3/3] Running collectstatic..."))
            call_command("collectstatic", "--noinput")
        else:
            self.stdout.write(self.style.WARNING("[3/3] collectstatic skipped by option."))

        self.stdout.write(self.style.SUCCESS("Pre-production checks completed successfully."))

    def _backup_database(self) -> None:
        engine = settings.DATABASES["default"].get("ENGINE", "")
        if engine != "django.db.backends.sqlite3":
            self.stdout.write(self.style.WARNING("Database backup step is only implemented for SQLite; skipped."))
            return

        db_path = Path(str(settings.DATABASES["default"]["NAME"]))
        if not db_path.exists():
            self.stdout.write(self.style.WARNING("SQLite database file not found; backup skipped."))
            return

        backup_dir = Path(settings.BASE_DIR) / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"db_backup_{timestamp}.sqlite3"
        shutil.copy2(db_path, backup_path)
        self.stdout.write(self.style.NOTICE(f"Database backup created: {backup_path}"))

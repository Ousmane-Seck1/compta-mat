from __future__ import annotations

from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = "Run core quality checks (system checks + tests)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-tests",
            action="store_true",
            help="Run only Django checks without tests.",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("[1/2] Running django system checks..."))
        call_command("check")

        if not options.get("skip_tests"):
            self.stdout.write(self.style.NOTICE("[2/2] Running inventory test suite..."))
            call_command("test", "inventory.tests")

        self.stdout.write(self.style.SUCCESS("Quality checks completed successfully."))

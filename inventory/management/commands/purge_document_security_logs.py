from __future__ import annotations

from django.conf import settings
from django.core.management import BaseCommand
from django.utils import timezone

from inventory.models import AuditLog


class Command(BaseCommand):
    help = "Purge old DocumentSecurity audit logs using a retention window."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=None,
            help="Retention window in days. Defaults to DOCUMENT_SECURITY_LOG_RETENTION_DAYS.",
        )

    def handle(self, *args, **options):
        configured_days = int(getattr(settings, "DOCUMENT_SECURITY_LOG_RETENTION_DAYS", 180))
        retention_days = options.get("days") if options.get("days") is not None else configured_days

        if retention_days < 1:
            raise ValueError("Retention days must be >= 1.")

        cutoff = timezone.now() - timezone.timedelta(days=retention_days)
        to_delete_qs = AuditLog.objects.filter(entity="DocumentSecurity", created_at__lt=cutoff)
        deleted_count = to_delete_qs.count()
        to_delete_qs.delete()

        AuditLog.objects.create(
            action=AuditLog.ACTION_DELETE,
            entity="DocumentSecurity",
            entity_id="bulk_purge_command",
            description=f"Purge command: logs older than {retention_days} days",
            metadata={
                "retention_days": retention_days,
                "deleted_count": deleted_count,
                "cutoff": cutoff.isoformat(),
                "source": "management_command",
            },
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Purged {deleted_count} DocumentSecurity log(s) older than {retention_days} day(s)."
            )
        )

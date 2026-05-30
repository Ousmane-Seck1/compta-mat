import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'compta_web.settings')
django.setup()

from inventory.models import InternalMovement

total = InternalMovement.objects.filter(movement_type=InternalMovement.TYPE_ASSIGNMENT).count()
print(f"Total InternalMovement TYPE_ASSIGNMENT: {total}")

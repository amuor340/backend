import os
from datetime import datetime
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = "Export a portable JSON backup of database records. Keep backups outside the public media directory."
    def add_arguments(self, parser): parser.add_argument("--output-dir", default=str(settings.BASE_DIR / "backups"))
    def handle(self, *args, **options):
        directory=os.path.abspath(options["output_dir"]); os.makedirs(directory, exist_ok=True)
        path=os.path.join(directory, f"pseudosphere-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json")
        with open(path,"w",encoding="utf-8") as stream: call_command("dumpdata", "--natural-foreign", "--natural-primary", "--indent", "2", stdout=stream)
        self.stdout.write(self.style.SUCCESS(f"Backup written to {path}"))

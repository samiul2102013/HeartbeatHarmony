from django.core.management.base import BaseCommand
from apps.study.models import StudyMaterial
from apps.study.video_utils import moov_at_front, run_faststart


class Command(BaseCommand):
    help = 'Report (default) or --fix MP4s whose moov atom is not at the front.'

    def add_arguments(self, parser):
        parser.add_argument('--fix', action='store_true', help='Remux in place (atomic, keeps original on failure).')

    def handle(self, *args, **opts):
        fixed, skipped, failed, checked = 0, 0, 0, 0
        for m in StudyMaterial.objects.exclude(pdf='').exclude(pdf__isnull=True).order_by('id'):
            path = m.pdf.path
            if not path.lower().endswith('.mp4'):
                skipped += 1
                continue
            checked += 1
            if moov_at_front(path):
                continue
            if not opts['fix']:
                self.stdout.write(f'NEEDS-FIX id={m.id} {path}')
                continue
            try:
                run_faststart(path, path)
                fixed += 1
                self.stdout.write(f'FIXED id={m.id}')
            except Exception as e:
                failed += 1
                self.stderr.write(f'FAILED id={m.id}: {e}')
        self.stdout.write(f'checked={checked} fixed={fixed} skipped(non-mp4)={skipped} failed={failed}')

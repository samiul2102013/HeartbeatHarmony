import os

from django.core.management.base import BaseCommand
from django.conf import settings

MODELS = [
    ("accounts", "User", "avatar"),
    ("community", "CommunityMessage", "file"),
    ("checkins", "MoodCategory", "svg"),
    ("study", "Topic", "thumbnail"),
    ("study", "StudyMaterial", "file"),
    ("study", "StudyMaterial", "pdf"),
    ("habits", "HabitMaterial", "file"),
]


class Command(BaseCommand):
    help = "Upload existing local media files to Cloudflare R2"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Only list files, don't upload")

    def handle(self, *args, **options):
        from django.apps import apps

        dry_run = options["dry_run"]

        required_vars = ("R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_ENDPOINT_URL", "R2_BUCKET_NAME")
        if not all(os.getenv(k) for k in required_vars):
            self.stdout.write(self.style.WARNING("R2 not fully configured. Set R2_ACCESS_KEY_ID, "
                                                  "R2_SECRET_ACCESS_KEY, R2_ENDPOINT_URL, R2_BUCKET_NAME"))
            return

        import boto3

        bucket = os.environ["R2_BUCKET_NAME"]
        s3 = boto3.client(
            "s3",
            endpoint_url=os.environ["R2_ENDPOINT_URL"],
            aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
            region_name="auto",
        )

        total, skipped, failed = 0, 0, 0
        media_root = settings.MEDIA_ROOT

        for app_label, model_name, field_name in MODELS:
            model = apps.get_model(app_label, model_name)
            if not model:
                continue
            qs = model.objects.exclude(**{f"{field_name}__isnull": True}).exclude(**{field_name: ""})
            count = qs.count()
            if not count:
                continue
            self.stdout.write(f"  {app_label}.{model_name}.{field_name} ({count})")

            for instance in qs.iterator():
                file_field = getattr(instance, field_name)
                if not file_field or not file_field.name:
                    continue

                key = file_field.name
                local_path = os.path.join(media_root, key)

                if not os.path.exists(local_path):
                    self.stdout.write(f"    SKIP  (missing): {key}")
                    skipped += 1
                    continue

                if not dry_run:
                    try:
                        s3.head_object(Bucket=bucket, Key=key)
                        skipped += 1
                        continue
                    except Exception:
                        pass

                    try:
                        with open(local_path, "rb") as f:
                            s3.upload_fileobj(f, bucket, key)
                        total += 1
                        if total % 50 == 0:
                            self.stdout.write(f"    ... {total} uploaded")
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"    FAIL: {key} — {e}"))
                        failed += 1
                else:
                    total += 1

        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"\nDry run — {total} files would be uploaded, "
                                                  f"{skipped} skipped (missing local file)"))
        else:
            self.stdout.write(self.style.SUCCESS(f"\nDone — {total} uploaded, {skipped} skipped, "
                                                  f"{failed} failed"))

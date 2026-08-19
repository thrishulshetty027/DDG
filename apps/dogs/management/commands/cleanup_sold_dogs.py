import logging
import cloudinary.uploader
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.dogs.models import Dog, DogImage, SiteConfig

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Deletes sold dogs and their Cloudinary images after the configured grace period.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--grace-days',
            type=int,
            default=None,
            help='Override grace period (default: uses SiteConfig.auto_delete_sold_days)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        # Get grace period from SiteConfig (admin-editable) or CLI override
        if options['grace_days'] is not None:
            grace_days = options['grace_days']
        else:
            config = SiteConfig.load()
            grace_days = config.auto_delete_sold_days

        cutoff_date = timezone.now() - timedelta(days=grace_days)

        self.stdout.write(f'\n🧹 Cleanup Script — Grace period: {grace_days} days')
        self.stdout.write(f'   Cutoff date: {cutoff_date.strftime("%Y-%m-%d %H:%M")}')
        if dry_run:
            self.stdout.write(self.style.WARNING('   🏃 DRY RUN MODE — nothing will be deleted\n'))
        self.stdout.write('')

        # Find sold dogs past grace period
        sold_dogs = Dog.objects.filter(
            status='sold',
            sold_at__isnull=False,
            sold_at__lte=cutoff_date,
        )

        if not sold_dogs.exists():
            self.stdout.write(self.style.SUCCESS('✅ No sold dogs to clean up. All clear!\n'))
            return

        self.stdout.write(f'Found {sold_dogs.count()} sold dog(s) to clean up:\n')

        deleted_dogs = 0
        deleted_images = 0
        failed_images = 0

        for dog in sold_dogs:
            self.stdout.write(
                f'  🐕 {dog.name} ({dog.breed.name}) — '
                f'Sold on {dog.sold_at.strftime("%Y-%m-%d")}'
            )

            # Delete each image from Cloudinary
            images = DogImage.objects.filter(dog=dog)
            for img in images:
                if img.image:
                    public_id = img.image.public_id if hasattr(img.image, 'public_id') else str(img.image)

                    if dry_run:
                        self.stdout.write(f'     [DRY RUN] Would delete image: {public_id}')
                    else:
                        try:
                            result = cloudinary.uploader.destroy(public_id)
                            if result.get('result') == 'ok':
                                self.stdout.write(
                                    self.style.WARNING(f'     🗑️  Deleted image: {public_id}')
                                )
                                deleted_images += 1
                            else:
                                self.stdout.write(
                                    self.style.ERROR(f'     ⚠️  Could not delete: {public_id} — {result}')
                                )
                                failed_images += 1
                        except Exception as e:
                            logger.error(f'Cloudinary delete failed for {public_id}: {e}')
                            self.stdout.write(self.style.ERROR(f'     ❌ Error: {e}'))
                            failed_images += 1

            # Delete dog record (cascades to DogImage rows in DB)
            if dry_run:
                self.stdout.write(f'     [DRY RUN] Would delete dog record: {dog.name}\n')
            else:
                dog_name = dog.name
                dog.delete()
                deleted_dogs += 1
                self.stdout.write(self.style.SUCCESS(f'     ✅ Deleted {dog_name} from database\n'))

        # ── Summary ──
        self.stdout.write(f'\n{"═" * 50}')
        if dry_run:
            self.stdout.write(self.style.WARNING(
                f'\n🏃 DRY RUN SUMMARY:\n'
                f'   Would delete {sold_dogs.count()} dog(s) and their images.\n'
                f'   Run without --dry-run to actually delete.\n'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'\n🎉 CLEANUP COMPLETE:\n'
                f'   Dogs deleted:    {deleted_dogs}\n'
                f'   Images deleted:  {deleted_images}\n'
                f'   Images failed:   {failed_images}\n'
            ))

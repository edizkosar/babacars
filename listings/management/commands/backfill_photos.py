"""
Fotoğrafı olmayan ilanlara Unsplash'tan foto indirip ekler.
(seed_data sırasında Cloudinary hatası olduysa eksik fotoğrafları tamamlar.)

Kullanım:  python manage.py backfill_photos
           python manage.py backfill_photos --count 5
"""
import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db.models import Count
from listings.models import Listing, Photo
from listings.management.commands.seed_data import PHOTO_URLS


class Command(BaseCommand):
    help = 'Fotoğrafı olmayan ilanlara Unsplash fotoğrafı ekler.'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=5,
                            help='İlan başına foto sayısı (varsayılan 5).')

    def handle(self, *args, **options):
        per = options['count']
        # Fotoğrafı olmayan ilanlar
        targets = (Listing.objects
                   .annotate(n=Count('photos'))
                   .filter(n=0))
        total = targets.count()
        if not total:
            self.stdout.write(self.style.SUCCESS('Tüm ilanların fotoğrafı zaten var.'))
            return

        self.stdout.write(f'{total} ilana foto eklenecek (her birine {per} adet)...')
        added, failed = 0, 0

        for i, listing in enumerate(targets, start=1):
            urls = PHOTO_URLS[:per]
            for idx, url in enumerate(urls):
                try:
                    resp = requests.get(url, timeout=20)
                    resp.raise_for_status()
                    photo = Photo(listing=listing, is_cover=(idx == 0), order=idx)
                    photo.image.save(
                        f'{listing.slug}_photo_{idx}.jpg',
                        ContentFile(resp.content),
                        save=True,
                    )
                    added += 1
                except Exception as exc:
                    failed += 1
                    self.stdout.write(self.style.WARNING(
                        f'  Foto eklenemedi (ilan #{listing.id}, foto #{idx}): {exc}'
                    ))
            if i % 5 == 0:
                self.stdout.write(f'  ... {i}/{total} ilan ({added} foto)')

        self.stdout.write(self.style.SUCCESS(
            f'Tamamlandı: {added} foto eklendi, {failed} başarısız.'
        ))

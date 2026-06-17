"""
Aracı olmayan (yarım kalmış) ilanları siler.
Eski bir hatadan dolayı Listing kaydedilip Vehicle oluşturulamayan ilanlar
detay/edit sayfasında hata veriyordu. Bu komut onları temizler.

Kullanım:  python manage.py delete_orphan_listings
"""
from django.core.management.base import BaseCommand
from listings.models import Listing


class Command(BaseCommand):
    help = 'Aracı olmayan (yarım) ilanları siler.'

    def handle(self, *args, **options):
        orphans = Listing.objects.filter(vehicle__isnull=True)
        count = orphans.count()
        if not count:
            self.stdout.write(self.style.SUCCESS('Yarım ilan yok, her şey temiz.'))
            return
        for l in orphans:
            self.stdout.write(f'  siliniyor: {l.slug or l.id} — {l.title}')
        orphans.delete()
        self.stdout.write(self.style.SUCCESS(f'{count} yarım ilan silindi.'))

"""
İlan oluşturmayı GERÇEK WEB YOLU (form + view + middleware) üzerinden test eder
ve hata olursa TAM traceback'i yazar. Canlı DB'ye bağlı çalıştırılınca
web formundaki 500'ün gerçek sebebini gösterir.

Kullanım:
    $env:DATABASE_URL = "postgresql://..."
    $env:DATABASE_SSL = "True"
    $env:CLOUDINARY_URL = "cloudinary://..."
    python manage.py test_create
"""
import io
import traceback
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.test import Client
from listings.models import Listing


class Command(BaseCommand):
    help = 'İlan oluşturmayı web formu üzerinden test eder, hatayı tam gösterir.'

    def handle(self, *args, **options):
        from PIL import Image
        if 'testserver' not in settings.ALLOWED_HOSTS:
            settings.ALLOWED_HOSTS.append('testserver')

        User = get_user_model()
        seller = User.objects.filter(role__in=['seller', 'both']).first()
        if not seller:
            self.stdout.write('Satıcı bulunamadı.')
            return
        self.stdout.write(f'Satıcı: {seller.email}')

        def img(fmt='JPEG', ext='jpg', ct='image/jpeg'):
            b = io.BytesIO()
            Image.new('RGB', (800, 600), (120, 80, 200)).save(b, fmt)
            b.seek(0)
            return SimpleUploadedFile(f'test.{ext}', b.read(), content_type=ct)

        c = Client(raise_request_exception=True)
        c.force_login(seller)

        data = {
            'listing_type': 'sale', 'title': 'WEB TEŞHİS', 'description': 'test aciklama',
            'price': '500000', 'city': 'İstanbul', 'district': 'Kadıköy',
            'make': 'BMW', 'model': 'X5', 'year': '2022', 'mileage': '10000',
            'fuel_type': 'diesel', 'transmission': 'automatic', 'body_type': 'suv',
            'color': 'Siyah',
            'photos': [img(), img(), img(), img()],
        }
        try:
            resp = c.post('/create/', data=data)
            self.stdout.write(f'STATUS: {resp.status_code}')
            if resp.status_code == 302:
                self.stdout.write(self.style.SUCCESS(f'BAŞARILI → {resp["Location"]}'))
                l = Listing.objects.filter(seller=seller, title='WEB TEŞHİS').first()
                if l:
                    l.delete()
                    self.stdout.write('Test ilanı silindi.')
            else:
                # Form hatalarını göster
                body = resp.content.decode('utf-8', 'ignore')
                import re
                errs = re.findall(r'text-red-600[^>]*>(.*?)</div>', body, re.S)
                for e in errs[:5]:
                    self.stdout.write('FORM HATA: ' + re.sub(r'<[^>]+>', ' ', e).strip()[:200])
        except Exception:
            self.stdout.write(self.style.ERROR('HATA — tam traceback:'))
            self.stdout.write(traceback.format_exc())

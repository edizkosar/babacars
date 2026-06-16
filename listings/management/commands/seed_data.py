import random
import time
import requests
from decimal import Decimal
from io import BytesIO

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils.text import slugify
from django.contrib.auth import get_user_model

from accounts.models import SellerProfile
from listings.models import Listing, Vehicle, Photo

User = get_user_model()

CARS = [
    ('BMW', '320i'), ('BMW', '520d'), ('Mercedes', 'C180'),
    ('Mercedes', 'E200'), ('Audi', 'A4'), ('Audi', 'A3'),
    ('Volkswagen', 'Passat'), ('Volkswagen', 'Golf'),
    ('Toyota', 'Corolla'), ('Toyota', 'C-HR'),
    ('Honda', 'Civic'), ('Ford', 'Focus'),
    ('Renault', 'Megane'), ('Renault', 'Clio'),
    ('Fiat', 'Egea'), ('Hyundai', 'i20'),
    ('Hyundai', 'Tucson'), ('Peugeot', '308'),
    ('Opel', 'Astra'), ('Skoda', 'Octavia'),
]

CITIES = [
    'İstanbul', 'Ankara', 'İzmir', 'Bursa',
    'Antalya', 'Adana', 'Konya', 'Eskişehir',
]

COLORS = [
    'Siyah', 'Beyaz', 'Gri', 'Kırmızı', 'Mavi',
    'Lacivert', 'Gümüş', 'Kahverengi', 'Yeşil',
]

FUEL_TYPES = ['gasoline', 'diesel', 'electric', 'hybrid', 'lpg']
TRANSMISSIONS = ['manual', 'automatic', 'semi_auto']
BODY_TYPES = ['sedan', 'hatchback', 'suv', 'coupe', 'wagon']

DESCRIPTIONS_SALE = [
    'Garaj arabası, boyasız, değişensiz, tramersiz.',
    'İlk sahibinden, bakımları düzenli, servis kayıtlı.',
    'Temiz kullanılmış, yeni muayeneli, lastikleri yeni.',
    'Kazasız, kusursuz, tam dolu paket.',
    'Acil satılık, fiyat düşürüldü. Takaslı da olur.',
    'Full + Full donanımlı, sunroof, deri döşeme.',
    'Motor ve şanzıman sorunsuz, klima bakımı yeni yapıldı.',
    'Otomatik park, geri görüş kamerası, çarpışma önleyici.',
]

DESCRIPTIONS_RENTAL = [
    'Günlük, haftalık kiralama yapılır. KM sınırsız.',
    'Kurumsal ve bireysel kiralama imkanı. Sigortalı.',
    'Yeni model araç, temiz ve bakımlı. Teslim hızlı.',
    'Havalimanı teslimatı mevcuttur.',
]

PHOTO_URLS = [
    'https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=800&h=600&fit=crop',
    'https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=800&h=600&fit=crop',
    'https://images.unsplash.com/photo-1542362567-b07e54358753?w=800&h=600&fit=crop',
    'https://images.unsplash.com/photo-1555215695-3004980ad54e?w=800&h=600&fit=crop',
    'https://images.unsplash.com/photo-1525609004556-c46c6c5104b8?w=800&h=600&fit=crop',
    'https://images.unsplash.com/photo-1549317661-bd32c8ce0afa?w=800&h=600&fit=crop',
    'https://images.unsplash.com/photo-1583121274602-3e2820c69888?w=800&h=600&fit=crop',
    'https://images.unsplash.com/photo-1580273916550-e323be2ae537?w=800&h=600&fit=crop',
    'https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=800&h=600&fit=crop',
    'https://images.unsplash.com/photo-1502877338535-766e1452684a?w=800&h=600&fit=crop',
    'https://images.unsplash.com/photo-1511919884226-fd3cad34687c?w=800&h=600&fit=crop',
    'https://images.unsplash.com/photo-1526726538690-5cbf956ae2fd?w=800&h=600&fit=crop',
    'https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=800&h=600&fit=crop',
    'https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=800&h=600&fit=crop',
    'https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=800&h=600&fit=crop',
    'https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=800&h=600&fit=crop',
]


class Command(BaseCommand):
    help = 'Seeds database with 50 demo car listings, 15 users, and photos.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-run even if seed data already exists.',
        )

    def handle(self, *args, **options):
        start_time = time.time()

        if User.objects.filter(email='seller1@babacars.com').exists():
            if not options['force']:
                self.stdout.write(self.style.WARNING(
                    'Seed data already exists (seller1@babacars.com found). '
                    'Use --force to re-run.'
                ))
                return
            self.stdout.write(self.style.WARNING('--force passed. Re-seeding...'))

        with transaction.atomic():
            sellers = self._create_sellers()
            buyers = self._create_buyers()
            listings_count, vehicles_count, photos_count = self._create_listings(sellers)

        elapsed = time.time() - start_time
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('SEED DATA REPORT'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(f'  Sellers created:   {len(sellers)}')
        self.stdout.write(f'  Buyers created:    {len(buyers)}')
        self.stdout.write(f'  Listings created:  {listings_count}')
        self.stdout.write(f'  Vehicles created:  {vehicles_count}')
        self.stdout.write(f'  Photos created:    {photos_count}')
        self.stdout.write(f'  Time elapsed:      {elapsed:.1f}s')
        self.stdout.write(self.style.SUCCESS('=' * 50))

    def _create_sellers(self):
        sellers = []
        for i in range(1, 11):
            email = f'seller{i}@babacars.com'
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email,
                    'role': 'seller',
                    'email_verified': True,
                    'full_name': f'Satıcı {i}',
                    'phone': f'053{random.randint(10000000, 99999999)}',
                }
            )
            if created:
                user.set_password('demo1234')
                user.save()
            profile, _ = SellerProfile.objects.get_or_create(
                user=user,
                defaults={
                    'bio': f'Profesyonel araç satıcısı #{i}.',
                    'is_verified': i <= 6,
                    'id_verified': i <= 4,
                    'total_sales': random.randint(0, 50),
                    'rating': Decimal(str(round(random.uniform(3.5, 5.0), 2))),
                }
            )
            sellers.append(user)
            if created:
                self.stdout.write(f'  + Seller: {email}')
        return sellers

    def _create_buyers(self):
        buyers = []
        for i in range(1, 6):
            email = f'buyer{i}@babacars.com'
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email,
                    'role': 'buyer',
                    'email_verified': True,
                    'full_name': f'Alıcı {i}',
                    'phone': f'054{random.randint(10000000, 99999999)}',
                }
            )
            if created:
                user.set_password('demo1234')
                user.save()
            buyers.append(user)
            if created:
                self.stdout.write(f'  + Buyer: {email}')
        return buyers

    def _create_listings(self, sellers):
        listings_count = 0
        vehicles_count = 0
        photos_count = 0

        for i in range(50):
            make, model = random.choice(CARS)
            is_rental = i >= 35
            listing_type = 'rental' if is_rental else 'sale'
            year = random.randint(2012, 2024)
            city = random.choice(CITIES)
            seller = random.choice(sellers)

            if is_rental:
                price = Decimal(str(random.randint(800, 5000)))
                description = random.choice(DESCRIPTIONS_RENTAL)
            else:
                price = Decimal(str(random.randint(4, 30) * 100000))
                description = random.choice(DESCRIPTIONS_SALE)

            title = f'{year} {make} {model}'
            base_slug = slugify(title)
            slug = f'{base_slug}-{random.randint(1000, 9999)}'

            while Listing.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{random.randint(1000, 9999)}'

            listing = Listing.objects.create(
                seller=seller,
                listing_type=listing_type,
                status='active',
                title=title,
                slug=slug,
                description=description,
                price=price,
                currency='TRY',
                city=city,
                view_count=random.randint(10, 500),
                favorite_count=random.randint(0, 30),
                is_featured=random.random() < 0.15,
            )
            listings_count += 1

            fuel = random.choice(FUEL_TYPES)
            trans = random.choice(TRANSMISSIONS)
            body = random.choice(BODY_TYPES)
            mileage = 0 if year >= 2024 else random.randint(5000, 200000)
            hp = random.randint(90, 400)

            Vehicle.objects.create(
                listing=listing,
                make=make,
                model=model,
                year=year,
                mileage=mileage,
                fuel_type=fuel,
                transmission=trans,
                body_type=body,
                color=random.choice(COLORS),
                engine_cc=random.choice([1200, 1400, 1500, 1600, 1800, 2000, 2500, 3000]),
                horsepower=hp,
                torque=random.randint(150, 600),
                trunk_volume=random.randint(300, 650),
                fuel_consumption=Decimal(str(round(random.uniform(4.5, 9.5), 1))),
                num_doors=random.choice([2, 4, 4, 4, 4]),
                num_seats=random.choice([5, 5, 5, 5, 7]),
                has_damage_record=random.random() < 0.2,
                damage_description='Hafif kaporta hasarı' if random.random() < 0.1 else '',
                paint_changed_parts=random.choice([0, 0, 0, 1, 2]),
                replaced_parts=random.choice([0, 0, 0, 0, 1]),
            )
            vehicles_count += 1

            photo_subset = random.sample(PHOTO_URLS, min(8, len(PHOTO_URLS)))
            for idx, url in enumerate(photo_subset):
                try:
                    resp = requests.get(url, timeout=15)
                    resp.raise_for_status()
                    filename = f'{slug}_photo_{idx}.jpg'
                    photo = Photo(
                        listing=listing,
                        is_cover=(idx == 0),
                        order=idx,
                    )
                    photo.image.save(
                        filename,
                        ContentFile(resp.content),
                        save=True,
                    )
                    photos_count += 1
                except Exception as exc:
                    self.stdout.write(self.style.WARNING(
                        f'  Photo download failed (listing #{i+1}, photo #{idx}): {exc}'
                    ))

            if (i + 1) % 5 == 0:
                self.stdout.write(f'  ... {i + 1}/50 listings created ({photos_count} photos)')

        return listings_count, vehicles_count, photos_count

from django.db import models
from django.conf import settings
from django.utils.text import slugify

LISTING_TYPE_CHOICES = [
    ('sale', 'For Sale'),
    ('rental', 'For Rent'),
]

STATUS_CHOICES = [
    ('active', 'Active'),
    ('sold', 'Sold'),
    ('rented', 'Rented'),
    ('passive', 'Passive'),
    ('pending', 'Pending Review'),
]


class Listing(models.Model):
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='listings',
    )
    listing_type = models.CharField(choices=LISTING_TYPE_CHOICES, max_length=10)
    status = models.CharField(choices=STATUS_CHOICES, max_length=10, default='active')
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='TRY')
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    view_count = models.PositiveIntegerField(default=0)
    favorite_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'listings'
        ordering = ['-created_at']
        verbose_name = 'Listing'
        verbose_name_plural = 'Listings'

    def save(self, *args, **kwargs):
        if not self.slug:
            import random
            base = slugify(self.title)
            slug = base
            while Listing.objects.filter(slug=slug).exists():
                slug = f'{base}-{random.randint(1000, 9999)}'
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.title} ({self.listing_type})"


class Vehicle(models.Model):
    FUEL_CHOICES = [
        ('gasoline', 'Gasoline'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
        ('lpg', 'LPG'),
    ]

    TRANSMISSION_CHOICES = [
        ('manual', 'Manual'),
        ('automatic', 'Automatic'),
        ('semi_auto', 'Semi-Automatic'),
    ]

    BODY_CHOICES = [
        ('sedan', 'Sedan'),
        ('hatchback', 'Hatchback'),
        ('suv', 'SUV'),
        ('coupe', 'Coupe'),
        ('convertible', 'Convertible'),
        ('wagon', 'Wagon'),
        ('van', 'Van'),
        ('pickup', 'Pickup'),
    ]

    listing = models.OneToOneField(
        Listing,
        on_delete=models.CASCADE,
        related_name='vehicle',
    )
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.PositiveSmallIntegerField()
    mileage = models.PositiveIntegerField(help_text='km')
    fuel_type = models.CharField(choices=FUEL_CHOICES, max_length=20)
    transmission = models.CharField(choices=TRANSMISSION_CHOICES, max_length=20)
    body_type = models.CharField(choices=BODY_CHOICES, max_length=20)
    color = models.CharField(max_length=50)
    engine_cc = models.PositiveSmallIntegerField(null=True, blank=True, help_text='cc')
    horsepower = models.PositiveSmallIntegerField(null=True, blank=True, help_text='hp')
    torque = models.PositiveSmallIntegerField(null=True, blank=True, help_text='Nm')
    trunk_volume = models.PositiveSmallIntegerField(null=True, blank=True, help_text='liters')
    fuel_consumption = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        help_text='L/100km',
    )
    num_doors = models.PositiveSmallIntegerField(default=4)
    num_seats = models.PositiveSmallIntegerField(default=5)
    has_damage_record = models.BooleanField(default=False)
    damage_description = models.TextField(blank=True)
    paint_changed_parts = models.PositiveSmallIntegerField(default=0, help_text='Boyalı parça sayısı')
    replaced_parts = models.PositiveSmallIntegerField(default=0, help_text='Değişen parça sayısı')

    class Meta:
        db_table = 'vehicles'
        verbose_name = 'Vehicle'
        verbose_name_plural = 'Vehicles'

    def __str__(self) -> str:
        return f"{self.make} {self.model} {self.year}"


class Photo(models.Model):
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='photos',
    )
    image = models.ImageField(upload_to='listings/photos/')
    is_cover = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'photos'
        ordering = ['order']
        verbose_name = 'Photo'
        verbose_name_plural = 'Photos'

    def __str__(self) -> str:
        return f"Photo({self.listing.title} – #{self.order})"


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites',
    )
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='favorited_by',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'favorites'
        unique_together = ('user', 'listing')
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'

    def __str__(self) -> str:
        return f"Favorite({self.user.email} → {self.listing.title})"


class ListingView(models.Model):
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='views',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'listing_views'
        verbose_name = 'Listing View'
        verbose_name_plural = 'Listing Views'

    def __str__(self) -> str:
        return f"View({self.listing.title} at {self.viewed_at})"


class ListingReport(models.Model):
    REASON_CHOICES = [
        ('fake', 'Sahte İlan'),
        ('sold', 'Satılmış Araç'),
        ('wrong_info', 'Yanlış Bilgi'),
        ('spam', 'Spam'),
        ('other', 'Diğer'),
    ]
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports')
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField(blank=True)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'listing_reports'
        ordering = ['-created_at']
        verbose_name = 'Listing Report'
        verbose_name_plural = 'Listing Reports'

    def __str__(self) -> str:
        return f"Report({self.listing.title} | {self.reason})"


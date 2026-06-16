from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from simple_history.models import HistoricalRecords

ROLE_CHOICES = [
    ('buyer', 'Buyer'),
    ('seller', 'Seller'),
    ('both', 'Both'),
]

RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]


class UserManager(BaseUserManager):
    """Custom manager so we can create users with email instead of username."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        extra_fields.setdefault('username', email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    full_name = models.CharField(max_length=150, blank=True)
    role = models.CharField(choices=ROLE_CHOICES, max_length=10, default='buyer')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    theme_preference = models.CharField(
        max_length=10,
        choices=[('light', 'Light'), ('dark', 'Dark')],
        default='light'
    )
    totp_enabled = models.BooleanField(default=False)
    totp_secret = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def is_seller(self) -> bool:
        return self.role in ['seller', 'both']

    def is_buyer(self) -> bool:
        return self.role in ['buyer', 'both']

    def __str__(self) -> str:
        return self.email


class SellerProfile(models.Model):
    history = HistoricalRecords()

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='seller_profile',
    )
    bio = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    id_verified = models.BooleanField(default=False)
    total_sales = models.PositiveIntegerField(default=0)
    avg_response_time = models.DurationField(null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'seller_profiles'
        verbose_name = 'Seller Profile'
        verbose_name_plural = 'Seller Profiles'

    def __str__(self) -> str:
        return f"SellerProfile({self.user.email})"


class Review(models.Model):
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='given_reviews',
    )
    seller = models.ForeignKey(
        SellerProfile,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reviews'
        unique_together = ('reviewer', 'seller')
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'

    def __str__(self) -> str:
        return f"Review({self.reviewer.email} → {self.seller.user.email})"

from __future__ import annotations
from typing import Optional
import pyotp
from django.contrib.auth import get_user_model
from accounts.models import SellerProfile, Review
from accounts import selectors

User = get_user_model()

def register_user(*, email: str, password: str, phone: str = '', role: str = 'buyer') -> User:
    try:
        selectors.get_user_by_email(email=email)
        raise ValueError('Email already exists')
    except User.DoesNotExist:
        pass
        
    user = User.objects.create_user(email=email, password=password, phone=phone, role=role)
    user.email_verified = False
    user.save(update_fields=['email_verified'])
    send_verification_email(user=user)
    return user

def send_verification_email(*, user: User) -> None:
    from django.core import signing
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    from django.conf import settings

    token = signing.dumps({'user_id': user.id})
    verify_url = f"{getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')}/accounts/verify-email/?token={token}"

    subject = 'BabaCars — E-posta Adresinizi Doğrulayın'
    html_message = render_to_string('accounts/email/verify_email.html', {
        'user': user,
        'verify_url': verify_url,
    })
    plain_message = (
        f"Merhaba,\n\n"
        f"BabaCars hesabınızı doğrulamak için aşağıdaki bağlantıya tıklayın:\n\n"
        f"{verify_url}\n\n"
        f"Bu bağlantı 24 saat geçerlidir.\n\n"
        f"Eğer bu isteği siz yapmadıysanız bu maili görmezden gelin."
    )
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )

def verify_email(*, token: str) -> User:
    from django.core import signing
    try:
        data = signing.loads(token, max_age=86400)
    except signing.BadSignature:
        raise ValueError('Invalid or expired token')
        
    user = selectors.get_user_by_id(user_id=data['user_id'])
    user.email_verified = True
    user.save(update_fields=['email_verified'])
    return user

def change_password(*, user, old_password: str, new_password: str) -> None:
    if not user.check_password(old_password):
        raise ValueError('Mevcut şifre yanlış.')
    user.set_password(new_password)
    user.save(update_fields=['password'])


def update_user_profile(
    *, user: User, email: Optional[str] = None,
    phone: Optional[str] = None, avatar=None,
    full_name: Optional[str] = None
) -> User:
    if email and email != user.email:
        try:
            selectors.get_user_by_email(email=email)
            raise ValueError('Bu e-posta adresi zaten kullanılıyor.')
        except User.DoesNotExist:
            user.email = email
            user.email_verified = False
            send_verification_email(user=user)

    if phone is not None:
        user.phone = phone
    if avatar is not None:
        user.avatar = avatar
    if full_name is not None:
        user.full_name = full_name

    user.save()
    return user

def become_seller(*, user: User) -> SellerProfile:
    if not user.phone:
        raise ValueError('Phone number is required')
    if not user.email_verified:
        raise ValueError('Email must be verified')
        
    if user.role == 'buyer':
        user.role = 'both'
        user.save(update_fields=['role'])
    elif user.role not in ['seller', 'both']:
        user.role = 'both'
        user.save(update_fields=['role'])
        
    profile, created = SellerProfile.objects.get_or_create(user=user)
    if created:
        profile.is_verified = False
        profile.save(update_fields=['is_verified'])
    return profile

def update_seller_profile(*, user: User, bio: Optional[str] = None) -> SellerProfile:
    try:
        profile = selectors.get_seller_profile(user=user)
    except SellerProfile.DoesNotExist:
        raise ValueError('User is not a seller')
        
    if bio is not None:
        profile.bio = bio
        profile.save(update_fields=['bio'])
    return profile

def create_review(*, reviewer: User, seller_profile: SellerProfile, rating: int, comment: str = '') -> Review:
    if reviewer == seller_profile.user:
        raise ValueError('Cannot review yourself')
        
    try:
        selectors.get_review(reviewer=reviewer, seller_profile=seller_profile)
        raise ValueError('Review already exists')
    except Review.DoesNotExist:
        pass
        
    if not (1 <= rating <= 5):
        raise ValueError('Rating must be between 1 and 5')
        
    review = Review.objects.create(
        reviewer=reviewer,
        seller=seller_profile,
        rating=rating,
        comment=comment
    )
    
    # Recalculate average rating
    from django.db.models import Avg
    avg_rating = Review.objects.filter(seller=seller_profile).aggregate(Avg('rating'))['rating__avg']
    seller_profile.rating = avg_rating
    seller_profile.save(update_fields=['rating'])
    
    return review

def generate_totp_secret(*, user: User) -> str:
    """Yeni bir TOTP secret oluşturur ve kullanıcıya kaydeder (henüz aktif etmez)."""
    secret = pyotp.random_base32()
    user.totp_secret = secret
    user.save(update_fields=['totp_secret'])
    return secret


def get_totp_uri(*, user: User) -> str:
    """Google Authenticator için otpauth:// URI döndürür."""
    totp = pyotp.TOTP(user.totp_secret)
    return totp.provisioning_uri(name=user.email, issuer_name='BabaCars')


def verify_totp_code(*, user: User, code: str) -> bool:
    """TOTP kodunu doğrular (±30 saniye toleranslı)."""
    if not user.totp_secret:
        return False
    totp = pyotp.TOTP(user.totp_secret)
    return totp.verify(code, valid_window=1)


def enable_totp(*, user: User, code: str) -> None:
    """Kodu doğrulayarak 2FA'yı aktif eder."""
    if not verify_totp_code(user=user, code=code):
        raise ValueError('Geçersiz doğrulama kodu.')
    user.totp_enabled = True
    user.save(update_fields=['totp_enabled'])


def disable_totp(*, user: User, code: str) -> None:
    """Kodu doğrulayarak 2FA'yı devre dışı bırakır."""
    if not verify_totp_code(user=user, code=code):
        raise ValueError('Geçersiz doğrulama kodu.')
    user.totp_enabled = False
    user.totp_secret = ''
    user.save(update_fields=['totp_enabled', 'totp_secret'])


def delete_review(*, reviewer: User, review_id: int) -> None:
    review = selectors.get_review_by_id(review_id=review_id)
    if reviewer != review.reviewer:
        raise PermissionError('Not authorized to delete this review')
        
    seller_profile = review.seller
    review.delete()
    
    # Recalculate average rating
    from django.db.models import Avg
    avg_rating = Review.objects.filter(seller=seller_profile).aggregate(Avg('rating'))['rating__avg']
    seller_profile.rating = avg_rating or 0.0
    seller_profile.save(update_fields=['rating'])

"""
Sosyal giriş (Google) yapan kullanıcıları otomatik 'doğrulanmış' işaretler.
Google e-postayı zaten doğruladığı için ayrıca doğrulama maili gerekmez.
"""
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver


@receiver(user_logged_in)
def verify_social_email(sender, request, user, **kwargs):
    # Kullanıcının bağlı bir sosyal hesabı varsa ve henüz doğrulanmamışsa doğrula
    if getattr(user, 'email_verified', True):
        return
    try:
        has_social = user.socialaccount_set.exists()
    except Exception:
        has_social = False
    if has_social:
        user.email_verified = True
        user.save(update_fields=['email_verified'])

import io
import base64
import qrcode
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django_ratelimit.decorators import ratelimit
from accounts import services, selectors
from accounts.forms import (
    RegisterForm, LoginForm, ProfileUpdateForm, BecomeSellerForm,
    UserPasswordChangeForm, TwoFactorVerifyForm,
)

User = get_user_model()

@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                services.register_user(
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'],
                    phone=form.cleaned_data['phone']
                )
                return redirect('accounts:verify_email_notice')
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

@require_http_methods(["GET"])
def verify_email_notice_view(request):
    return render(request, 'accounts/verify_email_notice.html')

@require_http_methods(["GET"])
def verify_email_view(request):
    token = request.GET.get('token')
    if not token:
        return render(request, 'accounts/verify_email_failed.html')
    
    try:
        services.verify_email(token=token)
        messages.success(request, 'E-posta adresiniz başarıyla doğrulandı. Giriş yapabilirsiniz.')
        return redirect('accounts:login')
    except ValueError:
        return render(request, 'accounts/verify_email_failed.html')

@ratelimit(key='ip', rate='10/m', method='POST', block=True)
@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            if user is not None:
                if user.totp_enabled:
                    request.session['2fa_pending_user_id'] = user.pk
                    return redirect('accounts:two_factor_verify')
                login(request, user)
                return redirect('listings:index')
            else:
                messages.error(request, 'Geçersiz e-posta veya şifre.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@require_http_methods(["GET", "POST"])
def two_factor_verify_view(request):
    """2FA aktifleştirilmiş kullanıcılar için OTP doğrulama adımı."""
    pending_id = request.session.get('2fa_pending_user_id')
    if not pending_id:
        return redirect('accounts:login')

    if request.method == "POST":
        form = TwoFactorVerifyForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(pk=pending_id)
            except User.DoesNotExist:
                del request.session['2fa_pending_user_id']
                return redirect('accounts:login')

            if services.verify_totp_code(user=user, code=form.cleaned_data['otp_code']):
                del request.session['2fa_pending_user_id']
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect('listings:index')
            else:
                messages.error(request, 'Geçersiz doğrulama kodu. Lütfen tekrar deneyin.')
    else:
        form = TwoFactorVerifyForm()

    return render(request, 'accounts/two_factor_verify.html', {'form': form})


@login_required
@require_http_methods(["GET", "POST"])
def two_factor_setup_view(request):
    """2FA kurulum sayfası: QR kodu göster ve doğrula."""
    user = request.user

    if request.method == "POST":
        form = TwoFactorVerifyForm(request.POST)
        action = request.POST.get('action')

        if action == 'disable' and user.totp_enabled:
            if form.is_valid():
                try:
                    services.disable_totp(user=user, code=form.cleaned_data['otp_code'])
                    messages.success(request, '2FA devre dışı bırakıldı.')
                    return redirect('accounts:two_factor_setup')
                except ValueError as e:
                    messages.error(request, str(e))

        elif action == 'enable' and not user.totp_enabled:
            if form.is_valid():
                try:
                    services.enable_totp(user=user, code=form.cleaned_data['otp_code'])
                    messages.success(request, '2FA başarıyla etkinleştirildi!')
                    return redirect('accounts:two_factor_setup')
                except ValueError as e:
                    messages.error(request, str(e))

        elif action == 'generate':
            services.generate_totp_secret(user=user)
            return redirect('accounts:two_factor_setup')

    else:
        form = TwoFactorVerifyForm()

    qr_image_b64 = None
    if user.totp_secret and not user.totp_enabled:
        uri = services.get_totp_uri(user=user)
        img = qrcode.make(uri)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        qr_image_b64 = base64.b64encode(buf.getvalue()).decode()

    return render(request, 'accounts/two_factor_setup.html', {
        'form': form,
        'qr_image_b64': qr_image_b64,
        'totp_enabled': user.totp_enabled,
        'totp_secret': user.totp_secret if not user.totp_enabled else None,
    })

@login_required
@require_http_methods(["POST"])
def logout_view(request):
    logout(request)
    return redirect('listings:index')

@login_required
@require_http_methods(["GET", "POST"])
def profile_view(request):
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                services.update_user_profile(
                    user=request.user,
                    email=form.cleaned_data['email'],
                    phone=form.cleaned_data['phone'],
                    avatar=form.cleaned_data.get('avatar'),
                    full_name=form.cleaned_data.get('full_name')
                )
                messages.success(request, 'Profiliniz güncellendi.')
                return redirect('accounts:profile')
            except ValueError as e:
                messages.error(request, str(e))
    else:
        initial = {
            'email': request.user.email,
            'phone': request.user.phone,
            'full_name': request.user.full_name,
        }
        form = ProfileUpdateForm(initial=initial)

    try:
        seller_profile = selectors.get_seller_profile(user=request.user)
    except Exception:
        seller_profile = None

    password_form = UserPasswordChangeForm()

    return render(request, 'accounts/profile.html', {
        'form': form,
        'password_form': password_form,
        'seller_profile': seller_profile
    })

@login_required
@require_http_methods(["GET", "POST"])
def become_seller_view(request):
    if request.method == "POST":
        form = BecomeSellerForm(request.POST)
        if form.is_valid():
            try:
                phone = form.cleaned_data.get('phone')
                if phone and phone != request.user.phone:
                    request.user.phone = phone
                    request.user.save(update_fields=['phone'])
                services.become_seller(user=request.user)
                
                bio = form.cleaned_data.get('bio')
                if bio:
                    services.update_seller_profile(user=request.user, bio=bio)
                    
                messages.success(request, 'Satıcı profiliniz başarıyla oluşturuldu.')
                return redirect('accounts:profile')
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = BecomeSellerForm(initial={'phone': request.user.phone})
    return render(request, 'accounts/become_seller.html', {'form': form})

@require_http_methods(["GET"])
def seller_profile_view(request, seller_id):
    try:
        seller_profile = selectors.get_seller_profile_by_id(seller_profile_id=seller_id)
        reviews = selectors.get_reviews_by_seller(seller_profile=seller_profile)
        
        # Access listings logic dynamically since accounts doesn't strictly import listings here in spec, but we do need it
        from listings import selectors as listing_selectors
        listings = listing_selectors.get_listings_by_seller(seller=seller_profile.user)
        
        return render(request, 'accounts/seller_profile.html', {
            'seller_profile': seller_profile,
            'reviews': reviews,
            'listings': listings
        })
    except Exception:
        messages.error(request, 'Satıcı bulunamadı.')
        return redirect('listings:index')

@login_required
@require_http_methods(["POST"])
def create_review_view(request, seller_id):
    try:
        seller_profile = selectors.get_seller_profile_by_id(seller_profile_id=seller_id)
        rating = int(request.POST.get('rating', 0))
        comment = request.POST.get('comment', '')
        
        services.create_review(
            reviewer=request.user,
            seller_profile=seller_profile,
            rating=rating,
            comment=comment
        )
        messages.success(request, 'Değerlendirmeniz kaydedildi.')
    except (ValueError, Exception) as e:
        messages.error(request, str(e))
        
    return redirect('accounts:seller_profile', seller_id=seller_id)

@login_required
@require_http_methods(["POST"])
def delete_review_view(request, review_id):
    try:
        services.delete_review(reviewer=request.user, review_id=review_id)
        messages.success(request, 'Değerlendirme silindi.')
    except PermissionError as e:
        messages.error(request, str(e))
    # We don't have a direct back redirect without HTTP_REFERER, just assume we redirect back somehow
    referer = request.META.get('HTTP_REFERER', '/')
    return redirect(referer)


@login_required
@require_http_methods(["POST"])
def change_password_view(request):
    form = UserPasswordChangeForm(request.POST)
    if form.is_valid():
        try:
            services.change_password(
                user=request.user,
                old_password=form.cleaned_data['old_password'],
                new_password=form.cleaned_data['new_password']
            )
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Şifreniz başarıyla güncellendi.')
        except ValueError as e:
            messages.error(request, str(e))
    else:
        messages.error(request, 'Lütfen formu doğru doldurun.')
    return redirect('accounts:profile')


@login_required
@require_http_methods(["POST"])
def resend_verification_email_view(request):
    user = request.user
    if user.email_verified:
        messages.info(request, 'E-posta adresiniz zaten doğrulanmış.')
        return redirect('accounts:profile')
    try:
        services.send_verification_email(user=user)
        messages.success(request, 'Doğrulama maili gönderildi. Lütfen gelen kutunuzu kontrol edin.')
    except Exception:
        messages.error(request, 'Mail gönderilemedi. Lütfen daha sonra tekrar deneyin.')
    return redirect('accounts:profile')


@login_required
@require_http_methods(["POST"])
def set_theme_view(request):
    import json
    data = json.loads(request.body)
    theme = data.get('theme', 'light')
    if theme in ['light', 'dark']:
        request.user.theme_preference = theme
        request.user.save(update_fields=['theme_preference'])
    return JsonResponse({'theme': theme})

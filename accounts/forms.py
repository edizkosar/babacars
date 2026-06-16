from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'E-posta adresiniz'})
    )
    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Şifre (min. 8 karakter)'})
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Şifreyi tekrar girin'})
    )
    phone = forms.CharField(
        max_length=20, required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Telefon numarası'})
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Şifreler eşleşmiyor.')
        return cleaned_data


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'E-posta adresiniz'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Şifreniz'})
    )


class ProfileUpdateForm(forms.Form):
    full_name = forms.CharField(
        max_length=150, required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ad Soyad'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-input'})
    )
    phone = forms.CharField(
        max_length=20, required=False,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-input'})
    )


class UserPasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Mevcut şifre'})
    )
    new_password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Yeni şifre (min. 8 karakter)'})
    )
    new_password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Yeni şifreyi tekrar girin'})
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password')
        p2 = cleaned_data.get('new_password_confirm')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Yeni şifreler eşleşmiyor.')
        return cleaned_data


class BecomeSellerForm(forms.Form):
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Telefon numarası zorunludur'})
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Kendinizi tanıtın'})
    )


class TwoFactorVerifyForm(forms.Form):
    otp_code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-input text-center text-2xl tracking-widest',
            'placeholder': '000000',
            'autocomplete': 'one-time-code',
            'inputmode': 'numeric',
        })
    )


class ReviewForm(forms.Form):
    rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.RadioSelect(attrs={'class': 'form-radio'})
    )
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Yorumunuz'})
    )

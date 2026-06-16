# forms.md

## Reference
See PROJECT_OVERVIEW.md for full architecture and naming conventions.
See all models MD files for field definitions.

## Purpose
Form validation only. No business logic. No ORM queries.
Views pass cleaned_data to services.py.

## Rules
- All forms use widgets with Tailwind CSS classes
- All error messages in Turkish
- No business logic inside forms — only field-level validation
- ModelForm where possible, Form for custom cases

---

## accounts/forms.py

```python
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


class BecomeSellerForm(forms.Form):
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Telefon numarası zorunludur'})
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Kendinizi tanıtın'})
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
```

---

## listings/forms.py

```python
from django import forms
from listings.models import Listing, Vehicle, Photo

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['listing_type', 'title', 'description', 'price', 'city', 'district']
        widgets = {
            'listing_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'İlan başlığı'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Fiyat (TL)'}),
            'city': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Şehir'}),
            'district': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'İlçe'}),
        }


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        exclude = ['listing']
        widgets = {
            'make': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Marka (BMW, Mercedes...)'}),
            'model': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Model (320i, C180...)'}),
            'year': forms.NumberInput(attrs={'class': 'form-input'}),
            'mileage': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Kilometre'}),
            'fuel_type': forms.Select(attrs={'class': 'form-select'}),
            'transmission': forms.Select(attrs={'class': 'form-select'}),
            'body_type': forms.Select(attrs={'class': 'form-select'}),
            'color': forms.TextInput(attrs={'class': 'form-input'}),
            'horsepower': forms.NumberInput(attrs={'class': 'form-input'}),
            'torque': forms.NumberInput(attrs={'class': 'form-input'}),
            'trunk_volume': forms.NumberInput(attrs={'class': 'form-input'}),
            'fuel_consumption': forms.NumberInput(attrs={'class': 'form-input'}),
        }


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['image', 'is_cover']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-input', 'accept': 'image/*'}),
        }


class SearchForm(forms.Form):
    listing_type = forms.ChoiceField(
        choices=[('', 'Tümü'), ('sale', 'Satılık'), ('rental', 'Kiralık')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    make = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Marka'})
    )
    model = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Model'})
    )
    year_min = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Min. Yıl'})
    )
    year_max = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Max. Yıl'})
    )
    price_min = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Min. Fiyat'})
    )
    price_max = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Max. Fiyat'})
    )
    fuel_type = forms.ChoiceField(
        choices=[('', 'Yakıt Tipi')] + Vehicle.FUEL_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    transmission = forms.ChoiceField(
        choices=[('', 'Vites')] + Vehicle.TRANSMISSION_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    body_type = forms.ChoiceField(
        choices=[('', 'Kasa Tipi')] + Vehicle.BODY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    city = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Şehir'})
    )
    ordering = forms.ChoiceField(
        choices=[
            ('-created_at', 'En Yeni'),
            ('created_at', 'En Eski'),
            ('price', 'En Düşük Fiyat'),
            ('-price', 'En Yüksek Fiyat'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
```

---

## offers/forms.py

```python
from django import forms

class OfferForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=12, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Teklif tutarı (TL)'})
    )
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'Mesajınız (isteğe bağlı)'})
    )
    rental_start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-input', 'type': 'date'})
    )
    rental_end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-input', 'type': 'date'})
    )

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('rental_start_date')
        end = cleaned_data.get('rental_end_date')
        if start and end and end <= start:
            raise forms.ValidationError('Bitiş tarihi başlangıç tarihinden sonra olmalıdır.')
        return cleaned_data


class CounterOfferForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=12, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Karşı teklif tutarı (TL)'})
    )
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'Mesajınız (isteğe bağlı)'})
    )

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError('Teklif tutarı sıfırdan büyük olmalıdır.')
        return amount
```

---

## messaging/forms.py

```python
from django import forms

class MessageForm(forms.Form):
    body = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'rows': 2,
            'placeholder': 'Mesajınızı yazın...',
            'maxlength': 2000,
        })
    )

    def clean_body(self):
        body = self.cleaned_data.get('body', '').strip()
        if not body:
            raise forms.ValidationError('Mesaj boş olamaz.')
        return body
```

---

## Healthcheck
After implementation run:
```bash
python manage.py check
```
Manually verify:
- RegisterForm raises ValidationError when passwords don't match
- OfferForm raises ValidationError when rental_end_date <= rental_start_date
- SearchForm all fields are optional (no required field)
- All form widgets have 'form-input' or 'form-select' CSS class
Expected: 0 errors.
Report any errors before proceeding to next file.

---

## PROMPT

### Context Files (must be read before coding)
- PROJECT_OVERVIEW.md
- AI_CONSTRAINTS.md
- accounts_models.md
- listings_models.md
- offers_models.md
- messaging_models.md

### Task
Implement all form files exactly as defined in this document.

### Files to Create
- accounts/forms.py
- listings/forms.py
- offers/forms.py
- messaging/forms.py

### Rules
1. Validation only. No business logic. No ORM queries.
2. All widgets include Tailwind-compatible CSS class ('form-input' or 'form-select').
3. All error messages in Turkish.
4. Copy code blocks exactly as written above.
5. Do NOT add extra fields or forms.
6. Run Healthcheck after each file.

### Output
One code block per file. No explanations.

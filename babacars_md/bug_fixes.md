# bug_fixes.md

## Reference
See PROJECT_OVERVIEW.md for full architecture.
See AI_CONSTRAINTS.md for all rules.

## Purpose
Critical bug fixes that prevent the application from working correctly.
Apply these fixes before any redesign work.

---

## Fix 1: num_doors and num_seats missing from VehicleForm

### Problem
VehicleForm in listings/forms.py does not include num_doors and num_seats fields.
Model has default=4 and default=5 but form validation fails because fields are required.

### Fix — listings/forms.py
Add num_doors and num_seats to VehicleForm:
```python
class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        exclude = ['listing']
        widgets = {
            'make': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Marka'}),
            'model': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Model'}),
            'year': forms.NumberInput(attrs={'class': 'form-input'}),
            'mileage': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Kilometre'}),
            'fuel_type': forms.Select(attrs={'class': 'form-select'}),
            'transmission': forms.Select(attrs={'class': 'form-select'}),
            'body_type': forms.Select(attrs={'class': 'form-select'}),
            'color': forms.TextInput(attrs={'class': 'form-input'}),
            'horsepower': forms.NumberInput(attrs={'class': 'form-input'}),
            'torque': forms.NumberInput(attrs={'class': 'form-input'}),
            'trunk_volume': forms.NumberInput(attrs={'class': 'form-input'}),
            'fuel_consumption': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.1'}),
            'num_doors': forms.NumberInput(attrs={'class': 'form-input', 'min': '2', 'max': '6'}),
            'num_seats': forms.NumberInput(attrs={'class': 'form-input', 'min': '2', 'max': '9'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['num_doors'].initial = 4
        self.fields['num_seats'].initial = 5
        self.fields['horsepower'].required = False
        self.fields['torque'].required = False
        self.fields['trunk_volume'].required = False
        self.fields['fuel_consumption'].required = False
        self.fields['engine_cc'].required = False
```

---

## Fix 2: Large number input (milyonlu sayı)

### Problem
Price and offer amount fields cannot accept numbers above a certain limit due to missing max attribute.

### Fix — listings/forms.py
Override price field in ListingForm:
```python
class ListingForm(forms.ModelForm):
    price = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'Fiyat (TL)',
            'min': '0',
            'max': '999999999999',
            'step': '0.01',
        })
    )
    class Meta:
        model = Listing
        fields = ['listing_type', 'title', 'description', 'price', 'city', 'district']
        widgets = {
            'listing_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'İlan başlığı'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
            'city': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Şehir'}),
            'district': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'İlçe'}),
        }
```

### Fix — offers/forms.py
Override amount in OfferForm and CounterOfferForm:
```python
class OfferForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'Teklif tutarı (TL)',
            'min': '0',
            'max': '999999999999',
            'step': '0.01',
        })
    )

class CounterOfferForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'Karşı teklif tutarı (TL)',
            'min': '0',
            'max': '999999999999',
            'step': '0.01',
        })
    )
```

---

## Fix 3: Password change and username — accounts

### Problem
User cannot change password or set a display name from profile page.

### Fix — accounts/models.py
Add full_name field to User model:
```python
full_name = models.CharField(max_length=150, blank=True)
```

### Fix — accounts/forms.py
Add PasswordChangeForm and update ProfileUpdateForm:
```python
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm

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
```

### Fix — accounts/services.py
Add change_password and update full_name:
```python
def change_password(*, user, old_password: str, new_password: str) -> None:
    if not user.check_password(old_password):
        raise ValueError('Mevcut şifre yanlış.')
    user.set_password(new_password)
    user.save(update_fields=['password'])

def update_user_profile(*, user, email: str = None, phone: str = None, avatar=None, full_name: str = None):
    if email and email != user.email:
        if get_user_model().objects.filter(email=email).exclude(pk=user.pk).exists():
            raise ValueError('Bu e-posta adresi zaten kullanılıyor.')
        user.email = email
    if phone is not None:
        user.phone = phone
    if avatar:
        user.avatar = avatar
    if full_name is not None:
        user.full_name = full_name
    user.save()
    return user
```

### Fix — accounts/views.py
Add change_password_view:
```python
@login_required
@require_http_methods(["POST"])
def change_password_view(request):
    from accounts.forms import UserPasswordChangeForm
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
```

### Fix — accounts/urls.py
Add password change URL:
```python
path('change-password/', views.change_password_view, name='change_password'),
```

### Fix — accounts/migrations
Run after model change:
```bash
python manage.py makemigrations accounts
python manage.py migrate
```

---

## Fix 4: Theme preference (dark/light mode)

### Problem
No theme toggle exists. User cannot switch between light and dark mode.

### Fix — accounts/models.py
Add theme_preference field:
```python
theme_preference = models.CharField(
    max_length=10,
    choices=[('light', 'Light'), ('dark', 'Dark')],
    default='light'
)
```

### Fix — base.html
Add theme toggle button in navbar and JS logic:
```javascript
// Theme toggle logic
const savedTheme = localStorage.getItem('theme') || 
    document.documentElement.getAttribute('data-theme') || 'light';
document.documentElement.setAttribute('data-theme', savedTheme);

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    // Save to server if authenticated
    fetch('/accounts/set-theme/', {
        method: 'POST',
        headers: { 'X-CSRFToken': getCSRF(), 'Content-Type': 'application/json' },
        body: JSON.stringify({ theme: next })
    });
}
```

### Fix — CSS dark mode overrides in base.html:
```css
[data-theme="dark"] body { background: #0F1117; color: #F1F5F9; }
[data-theme="dark"] .card { background: #1A1F2E; border-color: rgba(255,255,255,0.08); }
[data-theme="dark"] .form-input { background: #1A1F2E; border-color: rgba(255,255,255,0.1); color: #F1F5F9; }
[data-theme="dark"] .form-select { background: #1A1F2E; border-color: rgba(255,255,255,0.1); color: #F1F5F9; }
[data-theme="dark"] header { background: rgba(15,17,23,0.95); border-color: rgba(255,255,255,0.06); }
[data-theme="dark"] .section-title { color: #F1F5F9; }
[data-theme="dark"] footer { background: #060912; }
```

### Fix — accounts/views.py
Add set_theme_view:
```python
@login_required
@require_http_methods(["POST"])
def set_theme_view(request):
    import json
    data = json.loads(request.body)
    theme = data.get('theme', 'light')
    if theme in ['light', 'dark']:
        request.user.theme_preference = theme
        request.user.save(update_fields=['theme_preference'])
    from django.http import JsonResponse
    return JsonResponse({'theme': theme})
```

### Fix — accounts/urls.py
```python
path('set-theme/', views.set_theme_view, name='set_theme'),
```

### Fix — base.html context processor or view
In every view that renders base.html, theme is read from user:
```python
# In base.html <html> tag:
# <html lang="tr" data-theme="{{ request.user.theme_preference|default:'light' }}">
```

---

## Healthcheck
After all fixes run:
```bash
python manage.py makemigrations accounts
python manage.py migrate
python manage.py check
python manage.py runserver
```
Manually verify:
- Listing can be created without num_doors/num_seats error
- Price field accepts 1500000 TL
- Offer amount field accepts 1500000 TL
- Password can be changed from profile page
- Theme toggle switches between light/dark
- full_name field saves correctly
Expected: 0 errors, all fixes working.
Report any errors before proceeding.

---

## PROMPT

### Context Files (must be read before coding)
- PROJECT_OVERVIEW.md
- AI_CONSTRAINTS.md
- accounts_models.md
- listings_models.md
- accounts_services.md

### Task
Apply all bug fixes defined in this document.

### Files to Modify
- listings/forms.py → Fix 1 + Fix 2
- offers/forms.py → Fix 2
- accounts/models.py → Fix 3 (full_name) + Fix 4 (theme_preference)
- accounts/forms.py → Fix 3
- accounts/services.py → Fix 3
- accounts/views.py → Fix 3 + Fix 4
- accounts/urls.py → Fix 3 + Fix 4
- templates/base.html → Fix 4 (theme toggle button + JS + CSS)

### Rules
1. Apply fixes in order: Fix 1 → Fix 2 → Fix 3 → Fix 4.
2. Run migrations after accounts/models.py changes.
3. Do NOT remove existing fields or functions — only add.
4. update_session_auth_hash must be called after password change to keep user logged in.
5. Theme stored in both localStorage (immediate) and server (persistent).
6. Run Healthcheck after all fixes applied.

### Output
One code block per file. No explanations.

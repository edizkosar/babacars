from django import forms
from listings.models import Listing, Vehicle, Photo

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
            'has_damage_record': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'damage_description': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'Hasar detayları (varsa)'}),
            'paint_changed_parts': forms.NumberInput(attrs={'class': 'form-input', 'min': '0', 'max': '20'}),
            'replaced_parts': forms.NumberInput(attrs={'class': 'form-input', 'min': '0', 'max': '20'}),
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
        self.fields['has_damage_record'].required = False
        self.fields['damage_description'].required = False
        self.fields['paint_changed_parts'].required = False
        self.fields['replaced_parts'].required = False


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

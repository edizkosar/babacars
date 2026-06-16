from django import forms

class OfferForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=12, decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'Teklif tutarı (TL)',
            'min': '0',
            'max': '999999999999',
            'step': '0.01',
        })
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
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'Karşı teklif tutarı (TL)',
            'min': '0',
            'max': '999999999999',
            'step': '0.01',
        })
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

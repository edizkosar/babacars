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

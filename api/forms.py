# miapp/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario
class CustomUserCreationForm(UserCreationForm):
    us_nombre = forms.CharField(max_length=100, help_text='Tu nombre completo')
    email = forms.EmailField(max_length=254, help_text='Dirección de correo electrónico')
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = UserCreationForm.Meta.fields + ('us_nombre', 'email',)
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return email
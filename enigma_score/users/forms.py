from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class CustomRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="E-mail адрес", 
                           widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    first_name = forms.CharField(max_length=30, required=True, label="Имя",
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}))
    last_name = forms.CharField(max_length=30, required=True, label="Фамилия",
                              widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}))
    phone = forms.CharField(max_length=20, required=True, label="Телефон",
                          widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Телефон'}))
    birth_date = forms.DateField(required=True, label="Дата рождения",
                               widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    monthly_income = forms.DecimalField(max_digits=10, decimal_places=2, required=True, label="Ежемесячный доход",
                                     widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ежемесячный доход (₽)'}))
    employment_length = forms.IntegerField(required=True, label="Стаж работы (лет)",
                                        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Стаж работы (лет)'}))
    home_ownership = forms.ChoiceField(required=True, label="Тип жилья",
                                       choices=Profile.HOME_OWNERSHIP_CHOICES,
                                       widget=forms.Select(attrs={'class': 'form-control'}),
                                       initial='RENT')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Имя пользователя'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Пароль'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Подтверждение пароля'})
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 
                 'phone', 'birth_date', 'monthly_income', 'employment_length', 'home_ownership')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Пользователь с таким именем уже существует!")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с такой почтой уже существует!")
        return email


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'address', 'birth_date', 'monthly_income', 'employment_length']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'monthly_income': forms.NumberInput(attrs={'step': '0.01'}),
        }
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            clean_p = phone.replace(' ', '').replace('-', '')
            if not clean_p.replace('+', '').isdigit():
                raise forms.ValidationError("Номер телефона должен содержать только цифры, пробелы, дефисы и +!")
            if not (clean_p.startswith('+7') or clean_p.startswith('8')):
                raise forms.ValidationError("Номер должен начинаться с +7 или 8!")
        return phone

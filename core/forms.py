import datetime
from django import forms
from django.contrib.auth.models import User
from django.utils.dateparse import parse_time
from .models import Reservation, Table

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': '••••••••'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'example@mail.com'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Имя пользователя'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class ReservationForm(forms.ModelForm):
    # Позволяем принимать строку вида "10:00-12:00" или "10:00"
    time = forms.CharField(required=True, widget=forms.HiddenInput(attrs={'id': 'time-hidden', 'required': False}))

    class Meta:
        model = Reservation
        fields = ['name', 'phone', 'date', 'time', 'guests', 'table']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Иван Иванов'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+7 (999) 999-99-99'}),
            'date': forms.HiddenInput(attrs={'id': 'date'}),
            'table': forms.HiddenInput(attrs={'id': 'selected-table'}),
            'guests': forms.HiddenInput(attrs={'id': 'guests-hidden', 'required': False}),
        }

    def clean_time(self):
        time_slot = self.cleaned_data.get('time')
        if not time_slot:
            raise forms.ValidationError("Выберите время")

        # Если уже тип time, возвращаем его
        if isinstance(time_slot, (datetime.time, datetime.datetime)):
            return time_slot

        # Очищаем интервал (например, "10:00-12:00" -> "10:00")
        clean_time_str = time_slot.split('-')[0].strip()
        parsed_time = parse_time(clean_time_str)
        if not parsed_time:
            raise forms.ValidationError("Неверный формат времени.")
        return parsed_time

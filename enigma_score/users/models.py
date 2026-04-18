from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    phone = models.CharField('Телефон', max_length=20, blank=True)
    address = models.TextField('Адрес', blank=True)
    birth_date = models.DateField('Дата рождения', null=True, blank=True)
    monthly_income = models.DecimalField('Ежемесячный доход', max_digits=10, decimal_places=2, null=True, blank=True)
    employment_length = models.IntegerField('Стаж работы (лет)', null=True, blank=True)

    HOME_OWNERSHIP_CHOICES = [
        ('RENT', 'Аренда'),
        ('OWN', 'Собственность'),
        ('MORTGAGE', 'Ипотека'),
        ('OTHER', 'Другое'),
    ]
    home_ownership = models.CharField(
        'Тип жилья',
        max_length=20,
        choices=HOME_OWNERSHIP_CHOICES,
        default='RENT'
    )
    
    has_default_history = models.BooleanField(
        'Были ли дефолты',
        default=False,
        help_text='Были ли просрочки/дефолты по кредитам'
    )
    
    credit_score = models.IntegerField(
        'Кредитный рейтинг',
        null=True, blank=True,
        help_text='От 300 до 850'
    )
    

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return f'Профиль: {self.user.username}'

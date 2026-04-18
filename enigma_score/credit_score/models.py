from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import Profile  

class CreditApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credit_applications')
    
    loan_amnt = models.FloatField(
        'Сумма кредита ($)',
        validators=[MinValueValidator(500), MaxValueValidator(35000)]
    )
    
    loan_int_rate = models.FloatField(
        'Процентная ставка (%)',
        validators=[MinValueValidator(5.42), MaxValueValidator(23.22)],
        null=True, blank=True
    )
    
    person_income = models.FloatField(
        'Годовой доход',
        null=True, blank=True
    )
    
    person_emp_length = models.FloatField(
        'Стаж работы (лет)',
        null=True, blank=True
    )
    
    loan_percent_income = models.FloatField(
        'Отношение кредита к доходу',
        null=True, blank=True
    )
    
    person_home_ownership = models.CharField(
        'Тип жилья',
        max_length=20,
        choices=[
            ('RENT', 'Аренда'),
            ('OWN', 'Собственность'),
            ('MORTGAGE', 'Ипотека'),
            ('OTHER', 'Другое'),
        ],
        null=True, blank=True
    )
    
    cb_person_default_on_file = models.CharField(
        'Просрочки по кредитам',
        max_length=1,
        choices=[('Y', 'Да'), ('N', 'Нет')],
        null=True, blank=True
    )
    
    loan_intent = models.CharField(
        'Цель кредита',
        max_length=50,
        choices=[
            ('PERSONAL', 'Личные нужды'),
            ('EDUCATION', 'Образование'),
            ('MEDICAL', 'Медицина'),
            ('VENTURE', 'Бизнес'),
            ('HOMEIMPROVEMENT', 'Ремонт'),
            ('DEBTCONSOLIDATION', 'Рефинансирование'),
        ],
        null=True, blank=True
    )
    
    probability_default = models.FloatField('Вероятность дефолта', null=True, blank=True)
    decision = models.CharField(
        'Решение',
        max_length=10,
        choices=[('APPROVE', 'Одобрено'), ('REJECT', 'Отказано')],
        null=True, blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Кредитная заявка'
        verbose_name_plural = 'Кредитные заявки'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - ${self.loan_amnt} - {self.created_at.date()}"
    
    def get_person_income(self):
        """Получение годового дохода из профиля"""
        if self.user.profile.monthly_income:
            return float(self.user.profile.monthly_income * 12)
        return None
    
    def get_employment_length(self):
        """Получение стажа из профиля"""
        return self.user.profile.employment_length
    
    def get_loan_percent_income(self):
        """Расчет отношения кредита к доходу"""
        annual_income = self.get_person_income()
        if annual_income and annual_income > 0:
            return self.loan_amnt / annual_income
        return None
    
    def prepare_for_ml(self):
        profile = self.user.profile
        
        annual_income = self.get_person_income()
        employment_length = self.get_employment_length()
        
        loan_percent_income = self.get_loan_percent_income()
        
        ml_data = {
            'person_income': annual_income if annual_income else 50000.0,
            'person_emp_length': float(employment_length) if employment_length else 5.0,
            'loan_amnt': self.loan_amnt,
            'loan_int_rate': self.loan_int_rate if self.loan_int_rate else 11.0,
            'loan_percent_income': loan_percent_income if loan_percent_income else 0.2,
            'person_home_ownership': 'RENT',
            'loan_intent': self.loan_intent if self.loan_intent else 'PERSONAL',
            'loan_grade': self.loan_grade if self.loan_grade else 'C',
            'cb_person_default_on_file': 'N'
        }
        
        return ml_data

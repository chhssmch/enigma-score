from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile
from credit_score.models import CreditApplication


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'monthly_income', 'employment_length', 
                   'home_ownership', 'has_default_history', 'credit_score')
    list_filter = ('home_ownership', 'has_default_history')
    search_fields = ('user__username', 'user__email', 'phone')
    readonly_fields = ('credit_score',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'phone', 'address', 'birth_date')
        }),
        ('Финансовые данные', {
            'fields': ('monthly_income', 'employment_length', 'credit_score'),
            'description': 'Доход и стаж работы пользователя'
        }),
        ('Жильё и кредитная история', {
            'fields': ('home_ownership', 'has_default_history'),
            'description': 'Информация о жилье и кредитной истории'
        }),
    )
    
    def user(self, obj):
        return obj.user.username if obj.user else '-'
    user.short_description = 'Пользователь'
    
    def monthly_income(self, obj):
        if obj.monthly_income:
            return f"{obj.monthly_income:,.0f} ₽"
        return "Не указан"
    monthly_income.short_description = 'Ежемесячный доход'
    
    def employment_length(self, obj):
        if obj.employment_length:
            return f"{obj.employment_length} лет"
        return "Не указан"
    employment_length.short_description = 'Стаж работы'

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 
                   'get_profile_income', 'get_home_ownership', 'is_staff')
    list_select_related = ('profile',)
    
    def get_profile_income(self, obj):
        try:
            if obj.profile and obj.profile.monthly_income:
                return f"{obj.profile.monthly_income:,.0f} ₽"
            return "Не указан"
        except:
            return "Ошибка"
    get_profile_income.short_description = 'Доход'
    
    def get_home_ownership(self, obj):
        try:
            if obj.profile:
                return obj.profile.get_home_ownership_display()
            return "-"
        except:
            return "Ошибка"
    get_home_ownership.short_description = 'Тип жилья'

@admin.register(CreditApplication)
class CreditApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'loan_amnt', 'loan_intent', 
                   'decision', 'created_at', 'get_approval_probability')
    list_filter = ('decision', 'loan_intent', 'person_home_ownership', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('person_income', 'person_emp_length', 'loan_percent_income',
                     'probability_default', 'created_at')
    
    fieldsets = (
        ('Информация о заявке', {
            'fields': ('user', 'loan_amnt', 'loan_int_rate', 'loan_intent')
        }),
        ('Данные для скоринга', {
            'fields': ('person_income', 'person_emp_length', 'loan_percent_income',
                       'person_home_ownership', 'cb_person_default_on_file'),
            'description': 'Данные использованные для ML модели'
        }),
        ('Результат скоринга', {
            'fields': ('decision', 'probability_default'),
            'description': 'Результат обработки заявки'
        }),
    )
    
    def get_approval_probability(self, obj):
        if obj.probability_default is not None:
            approval_prob = (1 - obj.probability_default) * 100
            return f"{approval_prob:.1f}%"
        return "Не рассчитано"
    get_approval_probability.short_description = 'Вероятность одобрения'
    
    def user(self, obj):
        return obj.user.username if obj.user else '-'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


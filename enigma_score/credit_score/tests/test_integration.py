import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from users.models import Profile
from credit_score.models import CreditApplication


@pytest.mark.django_db
def test_integration_full_flow_with_real_ml():
    """
    Интеграционный тест: проверяет полный путь от формы до БД
    views.check_credit -> ml_service.predict -> preprocessor -> модель/fallback -> сохранение
    """
    
    # 1. Создаём пользователя и профиль
    user = User.objects.create_user(username='testuser', password='12345')
    Profile.objects.create(
        user=user,
        monthly_income=70000,
        employment_length=3,
        home_ownership='RENT'
    )
    
    # 2. Логинимся через тестовый клиент
    client = Client()
    client.login(username='testuser', password='12345')
    
    # 3. Отправляем POST-запрос (как если бы пользователь нажал кнопку)
    response = client.post(reverse('credit_score:check_credit'), {
        'loan_amount': 50000,
        'loan_intent': 'PERSONAL',
        'loan_int_rate': 12.5,
        'cb_person_default_on_file': 'N'
    }, follow=True)  # follow=True — следуем за редиректом
    
    # 4. Проверяем, что страница загрузилась
    assert response.status_code == 200
    
    # 5. Проверяем, что заявка сохранилась в БД
    assert CreditApplication.objects.filter(user=user).count() == 1
    
    application = CreditApplication.objects.first()
    assert application.loan_amnt == 50000
    assert application.decision in ['APPROVE', 'REJECT']  # любое решение — ок
    assert 0 <= application.probability_default <= 1
    
    # 6. Проверяем, что пользователь получил сообщение (Django messages)
    messages = list(response.context['messages'])
    assert len(messages) > 0
    assert 'Одобрено' in messages[0].message or 'Отказано' in messages[0].message


@pytest.mark.django_db
def test_integration_small_loan_high_income():
    """
    Интеграционный тест: маленький кредит, большой доход
    Проверяет, что fallback-логика (или модель) одобряет
    """
    
    user = User.objects.create_user(username='richuser', password='12345')
    Profile.objects.create(
        user=user,
        monthly_income=200000,  # высокий доход
        employment_length=5,
        home_ownership='OWN'
    )
    
    client = Client()
    client.login(username='richuser', password='12345')
    
    response = client.post(reverse('credit_score:check_credit'), {
        'loan_amount': 10000,   # маленький кредит
        'loan_intent': 'PERSONAL',
        'loan_int_rate': 10.0,
        'cb_person_default_on_file': 'N'
    }, follow=True)
    
    assert response.status_code == 200
    assert CreditApplication.objects.filter(user=user).count() == 1
    
    application = CreditApplication.objects.first()
    print(f"Решение: {application.decision}, Вероятность: {application.probability_default}")
    # Тест не проверяет конкретное решение — просто убеждается, что система ответила


@pytest.mark.django_db
def test_integration_large_loan_high_risk():
    """
    Интеграционный тест: большой кредит, большая ставка, были просрочки
    """
    
    user = User.objects.create_user(username='riskuser', password='12345')
    Profile.objects.create(
        user=user,
        monthly_income=50000,
        employment_length=1,
        home_ownership='RENT'
    )
    
    client = Client()
    client.login(username='riskuser', password='12345')
    
    response = client.post(reverse('credit_score:check_credit'), {
        'loan_amount': 500000,   # большой кредит
        'loan_intent': 'VENTURE', # бизнес
        'loan_int_rate': 25.0,    # высокая ставка
        'cb_person_default_on_file': 'Y'  # были просрочки
    }, follow=True)
    
    assert response.status_code == 200
    assert CreditApplication.objects.filter(user=user).count() == 1
    
    application = CreditApplication.objects.first()
    print(f"Решение: {application.decision}, Вероятность: {application.probability_default}")


@pytest.mark.django_db
def test_integration_invalid_data():
    """
    Интеграционный тест: некорректные данные — заявка НЕ сохраняется
    """
    
    user = User.objects.create_user(username='baduser', password='12345')
    Profile.objects.create(
        user=user,
        monthly_income=70000,
        employment_length=3
    )
    
    client = Client()
    client.login(username='baduser', password='12345')
    
    # Отправляем отрицательную сумму
    response = client.post(reverse('credit_score:check_credit'), {
        'loan_amount': -50000,  # отрицательная сумма
        'loan_intent': 'PERSONAL',
        'loan_int_rate': 12.5,
        'cb_person_default_on_file': 'N'
    }, follow=True)
    
    assert response.status_code == 200
    
    # Заявка НЕ должна сохраниться из-за ошибки валидации
    assert CreditApplication.objects.filter(user=user).count() == 0
    
    # Проверяем, что сообщение об ошибке пришло
    messages = list(response.context['messages'])
    assert any('положительной' in m.message for m in messages)
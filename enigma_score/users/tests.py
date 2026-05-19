import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from users.models import Profile

# 1. Тесты для РЕГИСТРАЦИИ

@pytest.mark.django_db
def test_user_registration_password_mismatch():
    """Если пароли не совпадают, пользователь НЕ создаётся"""
    client = Client()
    
    response = client.post(reverse('users:register'), {
        'username': 'newuser',
        'password1': 'TestPassword123!',
        'password2': 'DifferentPassword123!',
        'email': 'newuser@example.com'
    })
    
    # Пользователь не должен быть создан
    assert not User.objects.filter(username='newuser').exists()


@pytest.mark.django_db
def test_user_registration_duplicate_username():
    # Нельзя зарегистрироваться с уже существующим именем пользователя
    
    # Сначала создаём пользователя
    User.objects.create_user(username='existinguser', password='pass123')
    
    client = Client()
    response = client.post(reverse('users:register'), {
        'username': 'existinguser',
        'password1': 'NewPass123!',
        'password2': 'NewPass123!',
        'email': 'duplicate@example.com'
    })
    
    # Дубликат не должен создаться (должен быть 1 пользователь с этим именем)
    assert User.objects.filter(username='existinguser').count() == 1

# 2. Тесты для ВХОДА (логин)

@pytest.mark.django_db
def test_user_login_success():
    # Пользователь может войти с правильными учётными данными
    
    # Создаём пользователя
    User.objects.create_user(username='testuser', password='correctpass')
    
    client = Client()
    response = client.post(reverse('users:login'), {
        'username': 'testuser',
        'password': 'correctpass'
    })
    
    # После успешного входа должен быть редирект (обычно на главную)
    assert response.status_code == 302
    
    # Проверяем, что пользователь действительно залогинен (сессия содержит user_id)
    assert '_auth_user_id' in client.session


@pytest.mark.django_db
def test_user_login_wrong_password():
    # Вход с неправильным паролем не должен пропускать
    
    User.objects.create_user(username='testuser', password='correctpass')
    
    client = Client()
    response = client.post(reverse('users:login'), {
        'username': 'testuser',
        'password': 'wrongpass'
    })
    
    # Пользователь не должен быть залогинен
    assert '_auth_user_id' not in client.session


@pytest.mark.django_db
def test_user_login_nonexistent_user():
    # Вход с несуществующим пользователем не работает
    
    client = Client()
    response = client.post(reverse('users:login'), {
        'username': 'nonexistent',
        'password': 'anypass'
    })
    
    assert '_auth_user_id' not in client.session

# 3. Тесты для ВЫХОДА (логаут)

@pytest.mark.django_db
def test_user_logout():
    # После выхода пользователь разлогинивается
    
    # Создаём и логиним пользователя
    user = User.objects.create_user(username='testuser', password='pass123')
    client = Client()
    client.login(username='testuser', password='pass123')
    
    # Проверяем, что залогинен
    assert '_auth_user_id' in client.session
    
    # Выходим
    response = client.post(reverse('users:logout'))
    
    # После выхода — редирект
    assert response.status_code == 302
    
    # Пользователь разлогинен
    assert '_auth_user_id' not in client.session


# 4. Тесты для ПРОФИЛЯ

@pytest.mark.django_db
def test_profile_can_be_created_manually():
    # Профиль можно создать вручную (не автоматически)
    user = User.objects.create_user(username='testuser', password='pass123')
    profile = Profile.objects.create(user=user)
    
    assert Profile.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_profile_view_requires_login():
    # Страница профиля доступна только авторизованным
    client = Client()
    response = client.get(reverse('users:profile'))
    
    # Неавторизованный пользователь должен быть перенаправлен на страницу логина
    assert response.status_code == 302
    assert 'login' in response.url


@pytest.mark.django_db
def test_profile_view_accessible_when_logged_in():
    # Авторизованный пользователь может видеть свой профиль
    user = User.objects.create_user(username='testuser', password='pass123')
    Profile.objects.get_or_create(user=user)
    
    client = Client()
    client.login(username='testuser', password='pass123')
    
    response = client.get(reverse('users:profile'))
    
    assert response.status_code == 200


@pytest.mark.django_db
def test_profile_update():
    # Пользователь может обновить данные профиля (доход, стаж, телефон, адрес)
    user = User.objects.create_user(username='testuser', password='pass123')
    profile, _ = Profile.objects.get_or_create(user=user)
    
    client = Client()
    client.login(username='testuser', password='pass123')
    
    response = client.post(reverse('users:profile'), {
        'monthly_income': 75000,
        'employment_length': 4,
        'phone': '+79991234567',
        'address': 'Test Address'
    })
    
    # Обновляем профиль из БД
    profile.refresh_from_db()
    
    # Проверяем, что данные обновились
    assert profile.monthly_income == 75000
    assert profile.employment_length == 4
    assert profile.phone == '+79991234567'

# 5. Тест на структурную целостность (связь User и Profile)

@pytest.mark.django_db
def test_user_can_have_profile():
    # Пользователь может иметь профиль (создаётся вручную)
    user = User.objects.create_user(username='testuser', password='pass123')
    profile = Profile.objects.create(user=user)
    
    assert profile.user == user
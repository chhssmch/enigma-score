import pytest
from credit_score.ml_service import CreditScoringML

# Тесты для fallback, когда модель не грузит (fallback)
def test_fallback_when_no_model():
    service = CreditScoringML()
    
    # Принудительно отключаем модель
    service.model = None
    service.preprocessor = None
    
    # Минимальный набор данных для fallback
    test_data = {
        'loan_amnt': 100000,
        'person_income': 50000
    }
    
    result = service.predict(test_data)
    
    # Проверки
    assert result['method'] == 'FALLBACK'
    assert 'decision' in result
    assert 'probability' in result
    assert result['decision'] in ['APPROVE', 'REJECT']
    assert 0 <= result['probability'] <= 1
    assert result.get('fallback') == True


# Случай с одобрением, когда кредит маленький и низкий доход
def test_fallback_approve_case():
    service = CreditScoringML()
    service.model = None
    service.preprocessor = None
    
    # loan_to_income = 10000 / 100000 = 0.1 (<0.2) и loan_amnt=10000 (<20000)
    test_data = {
        'loan_amnt': 10000,
        'person_income': 100000
    }
    
    result = service.predict(test_data)
    
    assert result['decision'] == 'APPROVE'
    assert result['probability'] == 0.15


# Отказ из-за высокого отношения кредит/доход
def test_fallback_reject_by_loan_to_income():
    service = CreditScoringML()
    service.model = None
    service.preprocessor = None
    
    # loan_to_income = 60000 / 100000 = 0.6 (>0.5)
    test_data = {
        'loan_amnt': 60000,
        'person_income': 100000
    }
    
    result = service.predict(test_data)
    
    assert result['decision'] == 'REJECT'
    assert result['probability'] == 0.85


# Отказ из-за большой суммы кредита(>30000)
def test_fallback_reject_by_loan_amount():
    service = CreditScoringML()
    service.model = None
    service.preprocessor = None
    
    # loan_amnt=50000 (>30000), loan_to_income=0.25 (<0.5) но всё равно REJECT
    test_data = {
        'loan_amnt': 50000,
        'person_income': 200000
    }
    
    result = service.predict(test_data)
    
    assert result['decision'] == 'REJECT'
    assert result['probability'] == 0.85


# Средний случай, отказ с probability=0.50
def test_fallback_reject_middle_case():
    service = CreditScoringML()
    service.model = None
    service.preprocessor = None
    
    # loan_to_income = 25000 / 80000 = 0.3125 (не <0.2, не >0.5)
    # loan_amnt=25000 (<30000, не >30000)
    test_data = {
        'loan_amnt': 25000,
        'person_income': 80000
    }
    
    result = service.predict(test_data)
    
    assert result['decision'] == 'REJECT'
    assert result['probability'] == 0.50

# Если данных каких-то нет, должны использоваться значения по умолчанию
def test_fallback_with_missing_keys():
    service = CreditScoringML()
    service.model = None
    service.preprocessor = None
    
    # Пустой словарь
    result = service.predict({})
    
    assert result['decision'] in ['APPROVE', 'REJECT']
    assert isinstance(result['probability'], (int, float))
    # loan_amnt=0 по умолчанию, person_income=50000 по умолчанию
    # loan_to_income=0 -> попадает в случай APPROVE
    assert result['decision'] == 'APPROVE'


# Тесты для реальной модели

# Если модель загружена, выходные данные имеют правильный формат
def test_ml_model_output_format():
    service = CreditScoringML()
    
    # Если модель не загружена - пропускаем тест
    if service.model is None or service.preprocessor is None:
        pytest.skip("Модель или препроцессор не загружены, тест пропущен")
    
    # Полный набор данных (все поля, которые могут понадобиться препроцессору)
    test_data = {
        'loan_amnt': 100000,
        'person_income': 50000,
        'person_emp_length': 3,
        'loan_int_rate': 12.0,
        'loan_percent_income': 2.0,
        'person_home_ownership': 'RENT',
        'loan_intent': 'PERSONAL',
        'cb_person_default_on_file': 'N'
    }
    
    result = service.predict(test_data)
    
    # Проверки
    assert 'method' in result
    assert result['method'] in ['ML_MODEL', 'FALLBACK']
    assert 'decision' in result
    assert 'probability' in result
    assert isinstance(result['probability'], float)
    assert 0 <= result['probability'] <= 1


# Проверка, что threshold всегда 0.77
def test_ml_model_threshold_consistency():
    service = CreditScoringML()
    
    test_data = {
        'loan_amnt': 50000,
        'person_income': 60000,
        'person_emp_length': 2,
        'loan_int_rate': 10.0,
        'loan_percent_income': 0.83,
        'person_home_ownership': 'RENT',
        'loan_intent': 'PERSONAL',
        'cb_person_default_on_file': 'N'
    }
    
    result = service.predict(test_data)
    
    assert 'threshold' in result
    assert result['threshold'] == 0.77


# Тест на проверку корректности возвращаемых типов данных

def test_return_type_is_dict():
    service = CreditScoringML()
    service.model = None
    service.preprocessor = None
    
    result = service.predict({'loan_amnt': 10000, 'person_income': 50000})
    
    assert isinstance(result, dict)
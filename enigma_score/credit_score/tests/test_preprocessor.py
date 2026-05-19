import pytest
import pandas as pd
import numpy as np
from credit_score.preprocessor import CreditPreprocessor

# Тесты на заполнение пропусков
def test_fill_missing_numeric():
    """Пропуски в числовых полях заполняются медианой"""
    preprocessor = CreditPreprocessor()
    
    # Создаём данные с пропусками
    data = pd.DataFrame({
        'person_income': [50000, np.nan, 70000],
        'loan_amnt': [10000, 20000, np.nan],
        'person_emp_length': [2, 5, np.nan],
        'loan_int_rate': [10.0, 11.0, 12.0],
        'loan_percent_income': [0.2, 0.3, 0.4],
        'person_home_ownership': ['RENT', 'OWN', 'MORTGAGE'],
        'loan_intent': ['PERSONAL', 'EDUCATION', 'MEDICAL'],
        'loan_grade': ['A', 'B', 'C'],
        'cb_person_default_on_file': ['N', 'N', 'Y']
    })
    
    preprocessor.fit(data)
    result = preprocessor.transform(data)
    
    # Проверяем, что пропусков больше нет
    assert result.isnull().sum().sum() == 0

# Пропуски в категориальных полях заполняются модой
def test_fill_missing_categorical():
    preprocessor = CreditPreprocessor()
    
    data = pd.DataFrame({
        'person_income': [50000, 60000, 70000],
        'loan_amnt': [10000, 20000, 30000],
        'person_emp_length': [2, 5, 8],
        'loan_int_rate': [10.0, 11.0, 12.0],
        'loan_percent_income': [0.2, 0.3, 0.4],
        'person_home_ownership': ['RENT', np.nan, 'RENT'],
        'loan_intent': ['PERSONAL', 'PERSONAL', np.nan],
        'loan_grade': ['A', 'B', 'C'],
        'cb_person_default_on_file': ['N', 'N', 'Y']
    })
    
    preprocessor.fit(data)
    result = preprocessor.transform(data)
    
    # Проверяем, что пропусков больше нет
    assert result.isnull().sum().sum() == 0

# Тест на преобразование словаря в DataFrame
# transform() должен принимать словарь (как из API)
def test_transform_accepts_dict():
    preprocessor = CreditPreprocessor()
    
    # Обучаем на минимальных данных
    train_data = pd.DataFrame({
        'person_income': [50000],
        'loan_amnt': [10000],
        'person_emp_length': [2],
        'loan_int_rate': [10.0],
        'loan_percent_income': [0.2],
        'person_home_ownership': ['RENT'],
        'loan_intent': ['PERSONAL'],
        'loan_grade': ['A'],
        'cb_person_default_on_file': ['N']
    })
    preprocessor.fit(train_data)
    
    # Передаём словарь (как из ml_service.py)
    dict_data = {
        'person_income': 60000,
        'loan_amnt': 15000,
        'person_emp_length': 3,
        'loan_int_rate': 11.0,
        'loan_percent_income': 0.25,
        'person_home_ownership': 'OWN',
        'loan_intent': 'EDUCATION',
        'loan_grade': 'B',
        'cb_person_default_on_file': 'N'
    }
    
    result = preprocessor.transform(dict_data)
    
    # Должен вернуть DataFrame
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1  #одна строка

# Тест на наличие всех признаков на выходе

def test_output_has_all_features():
    preprocessor = CreditPreprocessor()
    
    train_data = pd.DataFrame({
        'person_income': [50000],
        'loan_amnt': [10000],
        'person_emp_length': [2],
        'loan_int_rate': [10.0],
        'loan_percent_income': [0.2],
        'person_home_ownership': ['RENT'],
        'loan_intent': ['PERSONAL'],
        'loan_grade': ['A'],
        'cb_person_default_on_file': ['N']
    })
    preprocessor.fit(train_data)
    
    result = preprocessor.transform(train_data)
    
    expected_features = [
        'person_income', 'person_emp_length', 'loan_amnt',
        'loan_int_rate', 'loan_percent_income',
        'person_home_ownership', 'loan_intent', 'loan_grade',
        'cb_person_default_on_file'
    ]
    
    for feature in expected_features:
        assert feature in result.columns

# Тест на логирование (log1p)
def test_log_transform_applied():
    preprocessor = CreditPreprocessor()
    
    train_data = pd.DataFrame({
        'person_income': [50000],
        'loan_amnt': [10000],
        'person_emp_length': [2],
        'loan_int_rate': [10.0],
        'loan_percent_income': [0.2],
        'person_home_ownership': ['RENT'],
        'loan_intent': ['PERSONAL'],
        'loan_grade': ['A'],
        'cb_person_default_on_file': ['N']
    })
    preprocessor.fit(train_data)
    
    test_data = pd.DataFrame({
        'person_income': [100000],
        'loan_amnt': [50000],
        'person_emp_length': [5],
        'loan_int_rate': [12.0],
        'loan_percent_income': [0.5],
        'person_home_ownership': ['OWN'],
        'loan_intent': ['EDUCATION'],
        'loan_grade': ['B'],
        'cb_person_default_on_file': ['N']
    })
    
    result = preprocessor.transform(test_data)
    
    # Проверяем, что значения изменились (стали меньше из-за log)
    # Логируемые поля: person_income, loan_amnt, person_emp_length
    assert result['person_income'].iloc[0] < 100000
    assert result['loan_amnt'].iloc[0] < 50000
    assert result['person_emp_length'].iloc[0] < 5
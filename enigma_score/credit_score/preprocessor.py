import pandas as pd
import numpy as np

class CreditPreprocessor:
    def __init__(self):
        self.numeric_features = [
            'person_income', 'person_emp_length', 'loan_amnt', 
            'loan_int_rate', 'loan_percent_income'
        ]
        self.categorical_features = [
            'person_home_ownership', 'loan_intent', 'loan_grade',
            'cb_person_default_on_file'
        ]
        self.log_features = ['person_income', 'loan_amnt', 'person_emp_length']
        
        self.fill_values = {}     
        self.fill_categories = {}  
        self.clip_bounds = {}
        self.fitted = False
        
    def fit(self, X):
        if X is None or len(X) == 0:
            raise ValueError("X не может быть None или пустым")
        
        X = X.copy()
        
        for col in self.numeric_features:
            if col in X.columns:
                self.fill_values[col] = X[col].median()
                
                Q1 = X[col].quantile(0.25)
                Q3 = X[col].quantile(0.75)
                IQR = Q3 - Q1
                self.clip_bounds[col] = (Q1 - 1.5 * IQR, Q3 + 1.5 * IQR)
            else:
                self.fill_values[col] = 0
                self.clip_bounds[col] = (-np.inf, np.inf)
        
        for col in self.categorical_features:
            if col in X.columns:
                mode_val = X[col].mode()
                self.fill_categories[col] = mode_val[0] if len(mode_val) > 0 else 'Unknown'
            else:
                self.fill_categories[col] = 'Unknown'
        
        self.fitted = True
        return self
    
    def transform(self, X):
        if X is None:
            raise ValueError("X не может быть None")
        
        if not self.fitted:
            raise ValueError("Сначала вызовите .fit()")
        
        if isinstance(X, dict):
            X = pd.DataFrame([X])
        elif isinstance(X, list):
            X = pd.DataFrame(X)
        
        X = X.copy()

        for col, val in self.fill_values.items():
            if col in X.columns:
                X[col] = pd.to_numeric(X[col], errors='coerce')  
                X[col] = X[col].fillna(val)
            else:
                X[col] = val
        
        for col in self.log_features:
            if col in X.columns:
                X[col] = np.log1p(X[col].clip(lower=0))
        
        for col, (lower, upper) in self.clip_bounds.items():
            if col in X.columns:
                X[col] = X[col].clip(lower=lower, upper=upper)
        
        for col, val in self.fill_categories.items():
            if col in X.columns:
                X[col] = X[col].astype(str).replace(['nan', 'None', 'null', ''], np.nan)
                X[col] = X[col].fillna(val)
            else:
                X[col] = val
        
        all_features = self.numeric_features + self.categorical_features
        missing = set(all_features) - set(X.columns)
        if missing:
            for col in missing:
                if col in self.numeric_features:
                    X[col] = self.fill_values.get(col, 0)
                else:
                    X[col] = self.fill_categories.get(col, 'Unknown')
        
        return X[all_features]
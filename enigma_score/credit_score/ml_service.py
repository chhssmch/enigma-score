import pandas as pd
import numpy as np
from pathlib import Path
import sys
import types

class CreditScoringML:
    def __init__(self):
        self.models_path = Path(__file__).parent / 'ml_models'
        self.model = None
        self.preprocessor = None
        self._register_preprocessor_module()
        self._load_models_if_exist()
    
    def _register_preprocessor_module(self):
        try:
            from .preprocessor import CreditPreprocessor
            
            preprocessor_module = types.ModuleType('preprocessor')
            preprocessor_module.CreditPreprocessor = CreditPreprocessor
            
            sys.modules['preprocessor'] = preprocessor_module
            print("✅ Registered preprocessor module for compatibility")
        except Exception as e:
            print(f"⚠️ Could not register preprocessor module: {e}")
    
    def _load_models_if_exist(self):
        model_path = self.models_path / 'credit_scoring_model.cbm'
        if model_path.exists():
            try:
                from catboost import CatBoostClassifier
                self.model = CatBoostClassifier()
                self.model.load_model(str(model_path))
                print("✅ CatBoost model loaded")
            except Exception as e:
                print(f"⚠️ Could not load model: {e}")
        else:
            print(f"⚠️ Model not found at {model_path}")
        
        preprocessor_path = self.models_path / 'preprocessor.pkl'
        if preprocessor_path.exists():
            try:
                import joblib
                self.preprocessor = joblib.load(preprocessor_path)
                print("✅ Preprocessor loaded successfully")
                print(f"Preprocessor type: {type(self.preprocessor)}")
            except Exception as e:
                print(f"⚠️ Could not load preprocessor: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"⚠️ Preprocessor not found at {preprocessor_path}")
    
    def predict(self, data):
        print(f"🔍 Predict called with data: {data}")
        print(f"🤖 Model available: {self.model is not None}")
        print(f"⚙️ Preprocessor available: {self.preprocessor is not None}")
        
        if self.model is not None and self.preprocessor is not None:
            try:
                print("🚀 Using ML model prediction...")
                df = pd.DataFrame([data])
                X_processed = self.preprocessor.transform(df)
                probability_default = float(self.model.predict_proba(X_processed)[0, 1])
                decision = 'REJECT' if probability_default >= 0.77 else 'APPROVE'
                
                result = {
                    'probability': probability_default,
                    'decision': decision,
                    'threshold': 0.77,
                    'method': 'ML_MODEL'
                }
                print(f"✅ ML Prediction result: {result}")
                return result
            except Exception as e:
                print(f"❌ ML prediction failed: {e}")
        
        print("🔄 Using fallback prediction...")
        result = self._fallback_prediction(data)
        result['method'] = 'FALLBACK'
        print(f"📊 Fallback result: {result}")
        return result
    
    def _fallback_prediction(self, data):
        loan_amount = data.get('loan_amnt', 0)
        income = data.get('person_income', 50000)
        
        loan_to_income = loan_amount / income if income > 0 else 1
        
        if loan_to_income < 0.2 and loan_amount < 20000:
            probability = 0.15
            decision = 'APPROVE'
        elif loan_to_income > 0.5 or loan_amount > 30000:
            probability = 0.85
            decision = 'REJECT'
        else:
            probability = 0.50
            decision = 'REJECT'
        
        return {
            'probability': probability,
            'decision': decision,
            'threshold': 0.77,
            'fallback': True
        }

ml_service = CreditScoringML()
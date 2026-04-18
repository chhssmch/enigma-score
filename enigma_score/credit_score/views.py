from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from .models import CreditApplication
from .ml_service import ml_service  

def home_page(request):
    if request.user.is_authenticated:
        result = request.session.pop('credit_result', None)
        return render(request, 'credit_score/home_auth.html', {
            'user': request.user,
            'result': result,
        })
    else:
        return render(request, 'credit_score/home.html')
    
@login_required
def check_credit(request):
    if request.method == 'POST':
        loan_amount = request.POST.get('loan_amount')
        loan_intent = request.POST.get('loan_intent', 'PERSONAL')
        loan_int_rate = request.POST.get('loan_int_rate', '11.0')
        cb_person_default_on_file = request.POST.get('cb_person_default_on_file', 'N')
        
        try:
            amount = float(loan_amount)
            interest_rate = float(loan_int_rate)
            
            if amount <= 0:
                messages.error(request, 'Сумма кредита должна быть положительной.')
                return redirect('credit_score:home')
            
            if interest_rate <= 0:
                messages.error(request, 'Процентная ставка должна быть положительной.')
                return redirect('credit_score:home')
            
            profile = request.user.profile
            
            annual_income = float(profile.monthly_income * 12) if profile.monthly_income else 50000.0
            employment_length = float(profile.employment_length) if profile.employment_length else 5.0
            
            loan_percent_income = amount / annual_income if annual_income > 0 else 0.2
            
            ml_data = {
                'person_income': annual_income,
                'person_emp_length': employment_length,
                'loan_amnt': amount,
                'loan_int_rate': interest_rate,
                'loan_percent_income': min(loan_percent_income, 0.83),
                'person_home_ownership': getattr(profile, 'home_ownership', 'RENT'),
                'loan_intent': loan_intent,
                'cb_person_default_on_file': cb_person_default_on_file
            }
            
            try:
                ml_result = ml_service.predict(ml_data)
                is_approved = ml_result['decision'] == 'APPROVE'
                probability_default = ml_result['probability']
                probability_approval = 1 - probability_default
                
                credit_application = CreditApplication.objects.create(
                    user=request.user,
                    loan_amnt=amount,
                    person_income=annual_income,
                    person_emp_length=employment_length,
                    loan_int_rate=ml_data['loan_int_rate'],
                    loan_percent_income=ml_data['loan_percent_income'],
                    person_home_ownership=ml_data['person_home_ownership'],
                    loan_intent=ml_data['loan_intent'],
                    cb_person_default_on_file=ml_data['cb_person_default_on_file'],
                    probability_default=probability_default,
                    decision=ml_result['decision']
                )
                
                method = ml_result.get('method', 'UNKNOWN')
                if is_approved:
                    messages.success(
                        request, 
                        f"Одобрено! Вероятность одобрения: {probability_approval*100:.1f}% (Метод: {method})"
                    )
                else:
                    messages.warning(
                        request, 
                        f"Отказано. Вероятность одобрения: {probability_approval*100:.1f}% (Метод: {method})"
                    )
                
            except Exception as ml_error:
                print(f"ML model error: {ml_error}, using fallback logic")
                is_approved = (amount < 1000000)
                probability_approval = 0.7 if is_approved else 0.3
                
                credit_application = CreditApplication.objects.create(
                    user=request.user,
                    loan_amnt=amount,
                    person_income=annual_income,
                    person_emp_length=employment_length,
                    loan_percent_income=loan_percent_income,
                    person_home_ownership=getattr(profile, 'home_ownership', 'RENT'),
                    loan_intent='PERSONAL',
                    cb_person_default_on_file='N'
                )
                
                messages.info(request, "Предсказание на основе упрощенной модели")
            
            result = {
                'is_approved': is_approved,
                'loan_amount': loan_amount,
                'probability': probability_approval if 'probability_approval' in locals() else None,
                'application_id': credit_application.id
            }
            
            request.session['credit_result'] = result
            
        except Exception as e:
            messages.error(request, f"Ошибка при обработке заявки: {str(e)}")
            print(f"Error in check_credit: {e}")
        
        return redirect('credit_score:home')
    
    return redirect('credit_score:home')

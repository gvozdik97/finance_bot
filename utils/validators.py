# finance_bot/utils/validators.py

def validate_amount(amount_text):
    """Проверяет валидность суммы"""
    try:
        amount = float(amount_text)
        if amount <= 0:
            return False, "❌ Сумма должна быть положительной!"
        return True, amount
    except ValueError:
        return False, "❌ Пожалуйста, введите число!"

def validate_budget_amount(amount_text):
    """Проверяет валидность суммы для бюджета"""
    return validate_amount(amount_text)  # Можно расширить специфичной логикой
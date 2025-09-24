# finance_bot/utils/formatters.py

def format_currency(amount):
    """Форматирует сумму в денежный формат"""
    return f"{amount:,.0f} руб."

def format_percentage(value, total):
    """Форматирует процентное значение"""
    if total > 0:
        return f"{(value / total * 100):.1f}%"
    return "0%"

def format_transaction_message(transaction_type, amount, category, description):
    """Форматирует сообщение о транзакции"""
    emoji = "💸" if transaction_type == 'expense' else "💳"
    type_text = "Расход" if transaction_type == 'expense' else "Доход"
    
    return (
        f"{emoji} *{type_text} добавлен!*\n\n"
        f"• Сумма: {format_currency(amount)}\n"
        f"• Категория: {category}\n"
        f"• Описание: {description}"
    )
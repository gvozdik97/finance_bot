# bot/debt_menu_handlers.py - С ЛОГИРОВАНИЕМ

import logging
from telegram import Update
from telegram.ext import ContextTypes

from keyboards.main_menu import get_main_menu_keyboard
from keyboards.debt_menu import get_debt_management_keyboard
from .common import show_main_menu
from .debt_handlers import (
    show_debts_menu, 
    show_snowball_plan, 
    show_debt_freedom_progress, 
    show_debt_milestones,
    show_debt_statistics,
    show_debts_main_menu
)

logger = logging.getLogger(__name__)

async def handle_debt_menu_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команды меню управления долгами"""
    text = update.message.text
    logger.info(f"Обрабатываем команду долгов: {text}")
    
    try:
        if text == '📜 Мои долги':
            logger.info("Показываем список долгов")
            await show_debts_menu(update, context)
        elif text == '➕ Добавить долг':
            logger.info("Начинаем добавление долга")
            from .debt_conversations import start_add_debt_flow
            await start_add_debt_flow(update, context)
        elif text == '💳 Погасить долг':
            logger.info("Начинаем погашение долга")
            await update.message.reply_text(
                "💳 *Начинаем процесс погашения долга...*",
                parse_mode='Markdown',
                reply_markup=get_debt_management_keyboard()
            )
        elif text == '📋 План погашения':
            logger.info("Показываем план погашения")
            await show_snowball_plan(update, context)
        elif text == '📈 Прогресс свободы':
            logger.info("Показываем прогресс свободы")
            await show_debt_freedom_progress(update, context)
        elif text == '🎯 Вехи освобождения':
            logger.info("Показываем вехи освобождения")
            await show_debt_milestones(update, context)
        elif text == '📊 Статистика долгов':
            logger.info("Показываем статистику долгов")
            await show_debt_statistics(update, context)
        elif text == '🏠 Главное меню':
            logger.info("Возвращаем в главное меню")
            await show_main_menu(update, context)
        elif text.lower().startswith('долг'):
            logger.info("Быстрый ввод долга")
            from .debt_conversations import quick_debt_input
            await quick_debt_input(update, context)
        else:
            logger.warning(f"Неизвестная команда долгов: {text}")
            await show_debts_main_menu(update, context)
            
    except Exception as e:
        logger.error(f"Ошибка в обработчике долгов: {e}")
        await update.message.reply_text(
            "❌ Ошибка при обработке команды. Попробуйте еще раз.",
            reply_markup=get_debt_management_keyboard()
        )
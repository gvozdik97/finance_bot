# finance_bot/bot/reports_handlers.py

from telegram import Update
from telegram.ext import ContextTypes
from keyboards.reports_menu import get_reports_keyboard
from services.report_service import report_service

async def show_reports(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает меню отчетов"""
    await update.message.reply_text(
        "📈 *Выберите период для отчета:*", 
        parse_mode='Markdown', 
        reply_markup=get_reports_keyboard()
    )

async def report_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор периода отчета"""
    query = update.callback_query
    await query.answer()
    
    data = query.data.replace('report_', '')
    
    try:
        result = report_service.generate_report(query.from_user.id, data)
        
        if not result['success']:
            await query.message.reply_text(result['error'])
            return
        
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=result['image_buffer'],
            caption=result['report_text'],
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Report handler error: {e}")
        await query.message.reply_text("❌ Ошибка при создании отчета.")
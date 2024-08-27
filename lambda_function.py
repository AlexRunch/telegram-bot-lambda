import json
import boto3
import nest_asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import logging
import asyncio

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация переменных
bot_token = '7512734081:AAGVNe3SGMdY1AnaJwu6_mN4bKTxp3Z7hJs'
s3_bucket_name = 'telegram-bot-subscribers'

s3_client = boto3.client('s3')

# Основная функция для инициализации и запуска бота
async def main():
    logger.debug("Инициализация бота начинается")
    
    # Инициализация бота
    application = Application.builder().token(bot_token).build()

    # Регистрация обработчика команды /start
    logger.debug("Регистрация команды /start")
    application.add_handler(CommandHandler("start", start))
    logger.debug("Команда /start зарегистрирована")

    logger.debug("Бот готов к запуску polling")

    # Запуск и проверка подписчиков один раз
    await application.initialize()
    await application.start()
    
    # Проверка подписчиков один раз
    await check_subscribers(application)
    
    # Ожидание 1 минуты
    await asyncio.sleep(60)
    
    # Повторная проверка подписчиков
    await check_subscribers(application)
    
    # Остановка бота
    await application.stop()

# Функция-обработчик для AWS Lambda
def lambda_handler(event, context):
    try:
        # Инициализация и запуск бота
        nest_asyncio.apply()
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Алексей, привет!")

async def check_subscribers(application):
    # Логика проверки подписчиков
    logger.info("Проверка подписчиков выполнена")

# Функция загрузки данных о подписчиках из S3
def load_subscribers():
    try:
        obj = s3_client.get_object(Bucket=s3_bucket_name, Key='subscribers.json')
        return json.loads(obj['Body'].read())
    except Exception as e:
        logger.error(f"Ошибка при загрузке данных из S3: {e}")
        return {"subscribers": []}

# Функция сохранения данных о подписчиках в S3
def save_subscribers(data):
    try:
        s3_client.put_object(Bucket=s3_bucket_name, Key='subscribers.json', Body=json.dumps(data))
    except Exception as e:
        logger.error(f"Ошибка при сохранении данных в S3: {e}")

# Функция для генерации отчета
def generate_report(added, removed, total):
    date_str = (datetime.now() + timedelta(hours=3)).strftime('%d %B %Y')
    report = f"📊 Отчет по подпискам и отпискам\n\nДата: {date_str}\n\n"

    if added:
        report += f"🔔 Новые подписчики ({len(added)}):\n"
        for user in added:
            report += f"1. @{user} (подписан)\n"
    else:
        report += "🔔 Новые подписчики: Нет\n"

    if removed:
        report += f"\n🚫 Отписавшиеся ({len(removed)}):\n"
        for user in removed:
            report += f"1. @{user} (отписался)\n"
    else:
        report += "\n🚫 Отписавшиеся: Нет\n"

    report += f"\n📈 Итог: \nОбщее количество подписчиков: {total}\nРазница за период: {len(added) - len(removed)}"

    return report

# Получаем текущих подписчиков канала (заглушка, требуется реализация)
async def get_current_subscribers():
    # Здесь должна быть реализация получения списка подписчиков канала
    return []

if __name__ == '__main__':
    lambda_handler(None, None)

import os
import psutil
import subprocess
import json
import tkinter as tk
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters
import threading
import mss
import pyautogui
import time
import sys
import winreg as reg
import GPUtil

# Перенаправление вывода в null, чтобы избежать вывода в консоль
sys.stdout = open(os.devnull, 'w')
sys.stderr = open(os.devnull, 'w')

# Ваш user_id для проверки доступа
ALLOWED_USER_ID = 00000

def load_apps():
    apps_path = "your/patch/to/apps.json" #<----------------- your/patch/to/apps.json
    with open(apps_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# Функция для проверки пользователя
async def check_user(update: Update):
    user_id = update.message.from_user.id
    if user_id != ALLOWED_USER_ID:
        await update.message.reply_text("У вас нет доступа к этому боту.")
        return False
    return True

# Статусы для ConversationHandler
SELECT_APP = 1

# Добавление в автозагрузку
def add_to_autostart():
    script_path = sys.argv[0]
    reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
    try:
        reg_key = reg.OpenKey(reg.HKEY_CURRENT_USER, reg_path, 0, reg.KEY_WRITE)
        reg.SetValueEx(reg_key, "PCAdmin", 0, reg.REG_SZ, script_path)
        reg.CloseKey(reg_key)
    except Exception as e:
        pass

# Функция для обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user(update):
        return
    await update.message.reply_text(
        "Привет! Я готов управлять твоим компьютером.\n"
        "Доступные команды:\n"
        "/run - Запустить приложение\n"
        "/sysinfo - Получить системную информацию\n"
        "/shutdown - Выключить компьютер\n"
        "/restart - Перезагрузить компьютер\n"
        "/screen - Сделать скриншот рабочего стола\n"
    )

# Функция для начала выбора приложения
async def run(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user(update):
        return
    apps = load_apps()
    context.user_data['apps'] = apps
    await update.message.reply_text(
        "Выберите приложение из списка:\n" + "\n".join([f"- {app}" for app in apps.keys()])
    )
    return SELECT_APP

# Функция для переключения на второй рабочий стол
def switch_to_second_desktop():
    pyautogui.hotkey('win', 'ctrl', 'right')
    time.sleep(1)

# Функция для переключения на первый рабочий стол
def switch_to_first_desktop():
    pyautogui.hotkey('win', 'ctrl', 'left')
    time.sleep(1)

# Функция для обработки выбора приложения
async def choose_app(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user(update):
        return
    user_choice = update.message.text.lower()
    if user_choice in context.user_data['apps']:
        app_path = context.user_data['apps'][user_choice]
        try:
            if user_choice == "запрет":
                switch_to_second_desktop()
            os.startfile(app_path)
            await update.message.reply_text(f"Приложение {user_choice.capitalize()} успешно запущено.")
            if user_choice == "запрет":
                time.sleep(3)
                switch_to_first_desktop()
        except Exception as e:
            await update.message.reply_text(f"Произошла ошибка при запуске приложения: {str(e)}")
    else:
        await update.message.reply_text(
            "Приложение не найдено в списке. Пожалуйста, выберите одно из предложенных приложений."
        )
        return SELECT_APP
    del context.user_data['apps']
    return ConversationHandler.END

# Функции для выключения и перезагрузки компьютера
async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user(update):
        return
    try:
        subprocess.run(["shutdown", "/s", "/f", "/t", "0"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        await update.message.reply_text("Компьютер будет выключен.")
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка при выключении: {str(e)}")

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user(update):
        return
    try:
        subprocess.run(["shutdown", "/r", "/f", "/t", "0"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        await update.message.reply_text("Компьютер будет перезагружен.")
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка при перезагрузке: {str(e)}")

async def system_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user(update):
        return
    cpu = psutil.cpu_percent()
    active_processes = len(list(psutil.process_iter()))
    memory = psutil.virtual_memory().percent
    gpus = GPUtil.getGPUs()
    gpu_info = "Нет видеокарт"
    if gpus:
        gpu_info = "\n".join([f"<b>{gpu.memoryUsed / gpu.memoryTotal * 100:.2f}%</b>" for gpu in gpus])
    await update.message.reply_text(
        f"Загрузка Процессора: <b>{cpu}%</b>\n"
        f"Загрузка Оперативки: <b>{memory}%</b>\n"
        f"Загрузка видеокарты: {gpu_info}\n"
        f"Активных процессов: <b>{active_processes}</b>\n",
        parse_mode='HTML'
    )

# Функция для создания и отправки скриншота
async def screen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user(update):
        return
    try:
        screenshot_path = os.path.join(os.path.dirname(__file__), "screenshot.png")
        with mss.mss() as sct:
            sct.shot(output=screenshot_path)
        if os.path.exists(screenshot_path):
            file_size = os.path.getsize(screenshot_path)
            if file_size > 20 * 1024 * 1024:
                await update.message.reply_text("Скриншот слишком большой для отправки.")
                return
            with open(screenshot_path, 'rb') as photo_file:
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_file)
            os.remove(screenshot_path)
        else:
            await update.message.reply_text("Не удалось создать скриншот. Попробуйте еще раз.")
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка при создании или отправке скриншота: {str(e)}")

# Функция для создания GUI и скрытия окна
def create_gui():
    window = tk.Tk()
    window.withdraw()  # Скрытие окна
    window.after(1000, lambda: window.quit())  # Закрытие окна через 1 секунду
    window.mainloop()

# Функция для отправки сообщения "Ваш компьютер запущен."
async def notify_computer_started(context):
    try:
        bot = context.bot
        await bot.send_message(ALLOWED_USER_ID, "Ваш компьютер запущен.")
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {str(e)}")

# Основная функция для запуска бота и GUI
def main():
    add_to_autostart()
    threading.Thread(target=create_gui, daemon=True).start()
    application = ApplicationBuilder().token("Your bot token").build() #<----------------- Your bot token
    application.add_handler(CommandHandler("start", start))
    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler("run", run)],
        states={SELECT_APP: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_app)]},
        fallbacks=[],
    ))
    application.add_handler(CommandHandler("sysinfo", system_info))
    application.add_handler(CommandHandler("shutdown", shutdown))
    application.add_handler(CommandHandler("restart", restart))
    application.add_handler(CommandHandler("screen", screen))

    application.job_queue.run_once(notify_computer_started, 1)

    application.run_polling()

if __name__ == "__main__":
    main()
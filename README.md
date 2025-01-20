# RU
Данное приложение позволяет управлять вашим компьютером с помощью телеграмм бота. Для этого потребуется создать телеграмм бота в BotFather, указать его токен а так же указать путь до apps.json. После создания exe файла через команду
`pyinstaller --onefile --icon=PCAdminLogo.ico --name=PCAdmin main.pyw`

После вы просто запускаете `.exe` файл и всё! бот автоматически добавляется в реестр, по пути: 
`HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`.

Для установки всех библиотек, выполните эту команду в консоли:
`pip install psutil python-telegram-bot mss pyautogui GPUtil`


# EN
This application allows you to control your computer using a Telegram bot. To do this, you need to create a Telegram bot via BotFather, provide its token, and specify the path to the `apps.json` file. After creating the executable file using the command:

`pyinstaller --onefile --icon=PCAdminLogo.ico --name=PCAdmin main.pyw`

you simply run the `.exe` file, and that's it! The bot is automatically added to the registry at the path:  
`HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`.

To install all the required libraries, run this command in the console:  
`pip install psutil python-telegram-bot mss pyautogui GPUtil`

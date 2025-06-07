import datetime

LOG_TO_FILE = False  # Якщо хочеш логувати в файл, зміни на True
LOG_FILE_PATH = "game_log.txt"

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] {message}"

    if LOG_TO_FILE:
        with open(LOG_FILE_PATH, "a") as file:
            file.write(full_message + "\n")
    else:
        print(full_message)

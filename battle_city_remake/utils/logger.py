#me
import datetime
import traceback
import sys

from config import LOG_TO_FILE, LOG_FILE_PATH, PLAYER_NAME


def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] {message}"

    if LOG_TO_FILE:
        try:
            with open(LOG_FILE_PATH, "a", encoding='utf-8') as file:
                file.write(full_message + "\n")

        except Exception as e:
            print(f'''Failed Logging to File. Error: {e} \n{full_message} 
                \n{PLAYER_NAME} has left the game.\n=====================================\n''')
    else:
        print(full_message)

def any_error_logger(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    error = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    error_message = f"""[{timestamp}] An Error in Game has been Occurred! Exception Traceback: \n{error} 
    \n{PLAYER_NAME} has left the game.\n=====================================\n"""

    if LOG_TO_FILE:
        try:
            with open(LOG_FILE_PATH, "a", encoding='utf-8') as file:
                file.write(error_message + "\n")
        except Exception as e:
            print(f''''Failed Logging an Error to File. Error: {e} \n{error_message} 
                \n{PLAYER_NAME} has left the game.\n=====================================\n''')
    else:
        print(error_message)
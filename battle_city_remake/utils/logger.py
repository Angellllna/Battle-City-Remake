#me
import datetime
import traceback
import logging
import sys

from config import LOG_TO_FILE, LOG_FILE_PATH, PLAYER_NAME


def log(message):
    global timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] {message}"

    if LOG_TO_FILE:
        with open(LOG_FILE_PATH, "a") as file:
            file.write(full_message + "\n")
    else:
        print(full_message)

def any_error_logger(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    error = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    error_message = log(f"""[{timestamp}] An Error in Game has been Occurred! Exception Traceback: \n{error} 
    \n{PLAYER_NAME} has left the game.""")

    if LOG_TO_FILE:
        with open(LOG_FILE_PATH, "a") as file:
            file.write(error_message + "\n")
    else:
        print(error_message)
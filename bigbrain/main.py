# bigbrain/main.py

import logging

logging.basicConfig(level=logging.WARNING)
logging.getLogger("browser_use").setLevel(logging.ERROR)
logging.getLogger("browser_use.agent").setLevel(logging.ERROR)
logging.getLogger("browser_use.browser").setLevel(logging.ERROR)
logging.getLogger("browser_use.service").setLevel(logging.ERROR)

from jarvis_core import handle_user_input


while True:

    user_input = input("You: ")

    if user_input.lower() in ["exit", "quit", "bye"]:
        print("Jarvis shutting down.")
        break

    result = handle_user_input(user_input)

    print(result)
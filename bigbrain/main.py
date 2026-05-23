# orchestrator/main.py

from router import route_request

while True:

    user_input = input("You: ")

    route = route_request(user_input)

    print(f"\n[ROUTER] → {route}\n")

    # Placeholder behavior
    if route == "browser":
        print("Would use browser tools here.")

    elif route == "coding":
        print("Would use coding model here.")

    elif route == "interpreter":
        print("Would use Open Interpreter here.")

    else:
        print("Would use DeepSeek reasoning here.")
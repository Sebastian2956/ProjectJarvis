# bigbrain/main.py

from router import route_request

from tools import TOOLS

while True:

    user_input = input("You: ")

    route = route_request(user_input)

    print(f"\n[ROUTER] → {route}\n")

    tool = TOOLS[route]

    result = tool(user_input)

    print(result)
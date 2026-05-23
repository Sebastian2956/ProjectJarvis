# orchestrator/router.py

def route_request(user_input: str):

    text = user_input.lower()

    # Browser tasks
    if any(word in text for word in [
        "google",
        "search",
        "look up",
        "browse",
        "website"
    ]):
        return "browser"

    # Coding tasks
    elif any(word in text for word in [
        "code",
        "python",
        "react",
        "javascript",
        "fix bug",
        "program"
    ]):
        return "coding"

    # System/terminal tasks
    elif any(word in text for word in [
        "open",
        "launch",
        "terminal",
        "file",
        "folder",
        "run command"
    ]):
        return "interpreter"

    # Default reasoning/chat
    else:
        return "reasoning"
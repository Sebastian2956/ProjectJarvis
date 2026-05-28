# bigbrain/safety.py

DANGEROUS_COMMANDS = [
    # File/folder deletion
    "rm",
    "del",
    "erase",
    "rmdir",
    "rd",
    "remove-item",
    "ri",

    # Formatting / disk / partition tools
    "format",
    "diskpart",
    "clean",
    "convert",
    "bcdedit",
    "bootrec",
    "bootsect",
    "chkdsk",

    # Shutdown / restart / power state
    "shutdown",
    "restart-computer",
    "stop-computer",
    "logoff",

    # Process killing
    "taskkill",
    "kill",
    "stop-process",
    "spps",

    # User/account/security changes
    "net user",
    "net localgroup",
    "add-localuser",
    "remove-localuser",
    "disable-localuser",
    "enable-localuser",
    "set-localuser",
    "new-localuser",
    "add-localgroupmember",
    "remove-localgroupmember",

    # Permissions / ownership
    "takeown",
    "icacls",
    "cacls",
    "attrib",

    # Registry modification
    "reg delete",
    "reg add",
    "reg import",
    "regedit",

    # Firewall / networking changes
    "netsh",
    "set-netfirewallprofile",
    "new-netfirewallrule",
    "remove-netfirewallrule",
    "disable-netadapter",
    "enable-netadapter",
    "ipconfig /release",

    # Services / startup changes
    "sc delete",
    "sc stop",
    "stop-service",
    "set-service",
    "new-service",
    "delete-service",

    # Package uninstall / system modification
    "winget uninstall",
    "choco uninstall",
    "scoop uninstall",
    "npm uninstall -g",
    "pip uninstall",

    # Remote/script execution risks
    "invoke-expression",
    "iex",
    "invoke-webrequest",
    "iwr",
    "curl",
    "wget",
    "start-bitstransfer",

    # PowerShell execution policy / scripts
    "set-executionpolicy",
    "powershell -encodedcommand",
    "pwsh -encodedcommand",

    # Environment/path changes
    "setx path",
    "[environment]::setenvironmentvariable",

    # Drives / mounts
    "mountvol",
    "subst",
]


DANGEROUS_PATTERNS = [
    # Recursive/force patterns
    "-recurse",
    "-force",
    "/s",
    "/q",
    "-r ",
    "-rf",
    "/f",

    # Wildcards
    "*",
    "/*",
    "\\*",

    # System locations
    "c:\\windows",
    "c:\\program files",
    "c:\\program files (x86)",
    "c:\\users",
    "$env:userprofile",
    "$home",
    "system32",

    # Redirection/chaining/piping
    ">",
    ">>",
    "&&",
    "||",
    ";",
    "|",

    # Download/run obfuscation
    "downloadstring",
    "frombase64string",
    "encodedcommand",
]


def is_safe_command(command: str) -> bool:
    command_lower = command.strip().lower()

    if not command_lower:
        return False

    if command_lower == "needs_confirmation":
        return False

    for dangerous in DANGEROUS_COMMANDS:
        if command_lower == dangerous:
            return False

        if command_lower.startswith(dangerous + " "):
            return False

    for pattern in DANGEROUS_PATTERNS:
        if pattern in command_lower:
            return False

    return True
import re

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|above|prior)\s+(instructions?|prompts?|rules?)",
    r"you\s+are\s+now\s+(a|an|the)",
    r"new\s+(role|instructions?|system)\s*:",
    r"act\s+as\s+if\s+you\s+have\s+no\s+(rules?|restrictions?)",
    r"pretend\s+you\s+are",
    r"disable\s+(your\s+)?(safety|filters?|guardrails?)",
    r"\bDAN\b|\bjailbreak\b|\bdeveloper\s+mode\b",
    r"system\s*:\s*",
    r"\[INST\]|<<SYS>>",
    r"how\s+do\s+I\s+(hack|exploit|bypass)",
    r"what\s+(are|is)\s+your\s+(system\s+)?(prompt|instructions?)",
    r"reveal\s+(your|the)\s+(system|original)\s+prompt",
    r"repeat\s+(everything|all|the)\s+(above|before)",
    r"print\s+(your|the)\s+(prompt|instructions?)",
    r"output\s+(your|the|above)\s+(prompt|instructions?|text)",
    r"summarize\s+(your|the)\s+(prompt|instructions?|rules?)",
]

MAX_MESSAGE_LENGTH = 2000

SPAM_REPEATED_CHAR = re.compile(r"(.)\1{10,}")


async def check_input(message: str) -> dict:
    if len(message) > MAX_MESSAGE_LENGTH:
        return {"clean": False, "reason": "message_too_long"}

    if SPAM_REPEATED_CHAR.search(message):
        return {"clean": False, "reason": "spam_detected"}

    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, message, re.IGNORECASE):
            return {"clean": False, "reason": "injection_detected", "pattern": pattern}

    return {"clean": True, "reason": None}

import re

SENSITIVE_PATTERNS = [
    (r"sk-[a-zA-Z0-9]{20,}", "api_key"),
    (r"(?:api[_-]?key|apikey)\s*[:=]\s*\S+", "api_key_leak"),
    (r"(?:password|passwd|pwd)\s*[:=]\s*\S+", "password_leak"),
    (r"(?:secret|token)\s*[:=]\s*['\"]?\S+['\"]?", "secret_leak"),
    (r"localhost:\d+", "internal_host"),
    (r"192\.168\.\d{1,3}\.\d{1,3}", "internal_ip"),
    (r"10\.\d{1,3}\.\d{1,3}\.\d{1,3}", "internal_ip"),
    (r"172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}", "internal_ip"),
    (r"postgresql://\S+", "database_url"),
    (r"mongodb://\S+", "database_url"),
    (r"redis://\S+", "database_url"),
]

PROMPT_LEAK_PATTERNS = [
    r"my\s+(system\s+)?(prompt|instructions?)\s+(is|are|says)",
    r"I\s+(was|am)\s+(told|instructed|programmed)\s+to",
    r"according\s+to\s+my\s+(rules?|instructions?)",
    r"as\s+(an\s+)?AI\s+(assistant|model|chatbot)",
]

INFRASTRUCTURE_PATTERNS = [
    (r"\bn8n\b", "infra_reference"),
    (r"\bgroq\b", "infra_reference"),
    (r"\bopenai\b", "infra_reference"),
    (r"\bllama\b", "infra_reference"),
]


async def check_output(response: str) -> dict:
    sanitized = response

    for pattern, reason in SENSITIVE_PATTERNS + INFRASTRUCTURE_PATTERNS:
        match = re.search(pattern, sanitized, re.IGNORECASE)
        if match:
            sanitized = re.sub(pattern, "[REDACTED]", sanitized, flags=re.IGNORECASE)

    for pattern in PROMPT_LEAK_PATTERNS:
        if re.search(pattern, response, re.IGNORECASE):
            return {
                "safe": False,
                "reason": "prompt_leak",
                "sanitized": "I can only answer portfolio-related questions about Abdullah's skills, projects, services, or meeting booking.",
            }

    if sanitized != response:
        return {"safe": True, "reason": "sanitized", "sanitized": sanitized}

    return {"safe": True, "reason": None, "sanitized": response}

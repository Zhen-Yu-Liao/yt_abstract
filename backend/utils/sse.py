import json
from typing import Any

def format_sse(event: str, data: Any) -> str:
    """Format data as a Server-Sent Event string."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"

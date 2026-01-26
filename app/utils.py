def format_size(size: int | None) -> str:
    if not size:
        return "Unknown size"
    return f"{size // 1048576}MB"

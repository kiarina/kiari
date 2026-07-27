def parse_duration(duration: str) -> float:
    duration = duration.strip()

    if duration.endswith("s"):
        return float(duration[:-1])
    if duration.endswith("m"):
        return float(duration[:-1]) * 60
    if duration.endswith("h"):
        return float(duration[:-1]) * 3600
    if duration.endswith("d"):
        return float(duration[:-1]) * 86400

    return float(duration)

import ffmpeg


def get_media_duration(file_path: str) -> float:
    """
    Returns duration in seconds
    """
    probe = ffmpeg.probe(file_path)
    return float(probe["format"]["duration"])

import subprocess

import ffmpeg


def get_media_duration(file_path: str) -> float:
    """
    Returns duration in seconds
    """
    probe = ffmpeg.probe(file_path)
    return float(probe["format"]["duration"])


def extract_audio(video_path: str) -> str:
    audio_path = video_path + ".wav"

    subprocess.run(
        ["ffmpeg", "-i", video_path, "-ar", "16000", "-ac", "1", audio_path], check=True
    )

    return audio_path

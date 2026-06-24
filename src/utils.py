import os
import subprocess
import logging

logger = logging.getLogger(__name__)

def extract_audio(video_path: str, audio_output_path: str):
    """
    Extracts audio from a video file using FFmpeg.
    """
    logger.info(f"Extracting audio from {video_path}")
    command = [
        'ffmpeg', '-y',
        '-i', video_path,
        '-vn', '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2',
        audio_output_path
    ]
    try:
        subprocess.run(command, check=True, capture_output=True)
        return audio_output_path
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg error: {e.stderr.decode()}")
        raise

def merge_audio_video(video_path: str, audio_path: str, output_path: str):
    """
    Merges an audio file with a video file, replacing the original audio.
    """
    logger.info(f"Merging audio {audio_path} with video {video_path}")
    command = [
        'ffmpeg', '-y',
        '-i', video_path,
        '-i', audio_path,
        '-c:v', 'copy',
        '-map', '0:v:0', '-map', '1:a:0',
        '-shortest',
        output_path
    ]
    try:
        subprocess.run(command, check=True, capture_output=True)
        return output_path
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg error: {e.stderr.decode()}")
        raise

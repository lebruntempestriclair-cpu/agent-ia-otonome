import asyncio
import logging
import ffmpeg
import os

logger = logging.getLogger(__name__)

class AIServices:
    """
    AI services in the dubbing pipeline.
    Currently using stubs, but designed to integrate with:
    - STT: OpenAI Whisper / Google Speech-to-Text
    - MT: DeepL / Google Translate
    - TTS: Amazon Polly / ElevenLabs
    - LipSync: Wav2Lip
    """

    @staticmethod
    async def transcribe(file_path: str) -> str:
        """STT: Speech-to-Text stub."""
        logger.info(f"Transcribing {file_path}...")
        # Integration point: openai.Audio.transcribe("whisper-1", file)
        await asyncio.sleep(1)
        return "This is a transcribed text from the source audio."

    @staticmethod
    async def translate(text: str, target_lang: str) -> str:
        """MT: Machine Translation stub."""
        logger.info(f"Translating text to {target_lang}...")
        # Integration point: deepl.Translator.translate_text(text, target_lang)
        await asyncio.sleep(0.5)
        return f"[Translated to {target_lang}] {text}"

    @staticmethod
    async def synthesize(text: str, voice_id: str) -> str:
        """TTS: Text-to-Speech stub."""
        logger.info(f"Synthesizing voice with {voice_id}...")
        # Integration point: polly.synthesize_speech(Text=text, VoiceId=voice_id)
        await asyncio.sleep(1)
        output_path = "temp_synthesized_audio.wav"
        # In a real scenario, we'd write the actual audio data here
        return output_path

    @staticmethod
    async def lip_sync(video_path: str, audio_path: str) -> str:
        """LipSync stub (e.g., Wav2Lip)."""
        logger.info("Performing lip synchronization...")
        await asyncio.sleep(2)
        # Mock final output
        final_video = video_path.replace(".mp4", "_final.mp4")
        if not os.path.exists(final_video):
            with open(final_video, 'wb') as f:
                f.write(b"fake dubbed video content")
        return final_video

class TranscodingService:
    """Utilities for media transcoding using FFmpeg."""

    @staticmethod
    async def extract_audio(video_path: str) -> str:
        """Extracts audio from video file using ffmpeg-python."""
        output_path = video_path.rsplit(".", 1)[0] + ".wav"
        logger.info(f"Extracting audio from {video_path} to {output_path}")

        try:
            # check if ffmpeg is available
            stream = ffmpeg.input(video_path)
            stream = ffmpeg.output(stream, output_path, acodec='pcm_s16le', ac=1, ar='16k')
            # Run in a thread pool since ffmpeg.run is blocking
            await asyncio.to_thread(ffmpeg.run, stream, overwrite_output=True, quiet=True)
        except Exception as e:
            logger.warning(f"FFmpeg extraction failed (binary likely missing): {e}. Using stub.")
            # Fallback for environment without FFmpeg binary
            if not os.path.exists(output_path):
                with open(output_path, 'wb') as f:
                    f.write(b"fake audio content")

        return output_path

    @staticmethod
    async def merge_audio_video(video_path: str, audio_path: str) -> str:
        """Merges dubbed audio back into video using ffmpeg-python."""
        output_path = video_path.rsplit(".", 1)[0] + "_dubbed.mp4"
        logger.info(f"Merging {audio_path} into {video_path} to {output_path}")

        try:
            input_video = ffmpeg.input(video_path)
            input_audio = ffmpeg.input(audio_path)
            # Use original video and new audio, copy video codec, re-encode audio to aac
            joined = ffmpeg.concat(input_video.video, input_audio.audio, v=1, a=1).node
            out = ffmpeg.output(joined[0], joined[1], output_path, vcodec='copy', acodec='aac')
            await asyncio.to_thread(ffmpeg.run, out, overwrite_output=True, quiet=True)
        except Exception as e:
            logger.warning(f"FFmpeg merge failed (binary likely missing): {e}. Using stub.")
            if not os.path.exists(output_path):
                with open(output_path, 'wb') as f:
                    f.write(b"fake merged video content")

        return output_path

import pytest
import os
import shutil
import asyncio
from pathlib import Path
from src.storage import StorageManager
from src.services import TranscodingService, STTService, MTService, TTSService
from src.orchestrator import DubbingOrchestrator
from src.models import DubbingJob

@pytest.fixture
def storage():
    sm = StorageManager(base_dir="test_uploads")
    yield sm
    if Path("test_uploads").exists():
        shutil.rmtree("test_uploads")

@pytest.mark.asyncio
async def test_storage_chunk_assembly(storage):
    user_id = "test_user"
    upload_id = "test_upload"
    filename = "test.txt"
    chunks = [b"Hello ", b"World", b"!"]

    for i, chunk in enumerate(chunks):
        await storage.save_chunk(upload_id, i, chunk)

    final_path = await storage.assemble_file(user_id, upload_id, filename, len(chunks))

    assert Path(final_path).exists()
    with open(final_path, "rb") as f:
        assert f.read() == b"Hello World!"

@pytest.mark.asyncio
async def test_transcoding_simulation():
    service = TranscodingService()
    # If ffmpeg is not installed, it should still return True (simulation)
    success = await service.extract_audio("input.mp4", "output.mp3")
    assert success is True

@pytest.mark.asyncio
async def test_ai_services_stubs():
    stt = STTService()
    mt = MTService()
    tts = TTSService()

    res = await stt.transcribe("path")
    assert "text" in res

    trans = await mt.translate(res["text"], "fr")
    assert "Bonjour" in trans

    voice = await tts.synthesize(trans, "default", "out.mp3")
    assert voice["audio_path"] == "out.mp3"

@pytest.mark.asyncio
async def test_orchestrator_pipeline():
    orchestrator = DubbingOrchestrator()
    # Create a dummy file for the "video"
    os.makedirs("test_data", exist_ok=True)
    video_path = "test_data/input.mp4"
    with open(video_path, "w") as f:
        f.write("dummy video data")

    job = DubbingJob(
        user_id="user1",
        input_file=video_path,
        target_language="fr",
        voice_model="model_x"
    )

    await orchestrator.run_pipeline(job)

    assert job.status == "completed"
    assert job.progress == 1.0
    assert "wer" in job.metrics
    assert "mos" in job.metrics

    # Cleanup
    shutil.rmtree("test_data")

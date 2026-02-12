from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
import requests
import base64
from io import BytesIO

app = FastAPI()

# TikTok TTS Configuration
WEILBYTE_ENDPOINT = "https://tiktok-tts.weilnet.workers.dev"

# TikTok Voices List
VOICES = [
    {"id": "en_us_001", "name": "English US Female 1", "language": "English", "gender": "Female"},
    {"id": "en_us_002", "name": "English US Female 2 (Siri-like)", "language": "English", "gender": "Female"},
    {"id": "en_us_006", "name": "English US Male 1", "language": "English", "gender": "Male"},
    {"id": "en_us_007", "name": "English US Male 2", "language": "English", "gender": "Male"},
    {"id": "en_us_009", "name": "English US Male 3", "language": "English", "gender": "Male"},
    {"id": "en_us_010", "name": "English US Male 4", "language": "English", "gender": "Male"},
    {"id": "en_uk_001", "name": "English UK Male 1", "language": "English", "gender": "Male"},
    {"id": "en_uk_003", "name": "English UK Male 2", "language": "English", "gender": "Male"},
    {"id": "en_au_001", "name": "English AU Female", "language": "English", "gender": "Female"},
    {"id": "en_au_002", "name": "English AU Male", "language": "English", "gender": "Male"},
    {"id": "en_us_ghostface", "name": "Ghost Face", "language": "English", "gender": "Character"},
    {"id": "en_us_chewbacca", "name": "Chewbacca", "language": "English", "gender": "Character"},
    {"id": "en_us_c3po", "name": "C3PO", "language": "English", "gender": "Character"},
    {"id": "en_us_stitch", "name": "Stitch", "language": "English", "gender": "Character"},
    {"id": "en_us_stormtrooper", "name": "Stormtrooper", "language": "English", "gender": "Character"},
    {"id": "en_us_rocket", "name": "Rocket", "language": "English", "gender": "Character"},
    {"id": "es_002", "name": "Spanish Male", "language": "Spanish", "gender": "Male"},
    {"id": "es_mx_002", "name": "Spanish MX Male", "language": "Spanish", "gender": "Male"},
    {"id": "fr_001", "name": "French Male 1", "language": "French", "gender": "Male"},
    {"id": "fr_002", "name": "French Male 2", "language": "French", "gender": "Male"},
    {"id": "de_001", "name": "German Female", "language": "German", "gender": "Female"},
    {"id": "de_002", "name": "German Male", "language": "German", "gender": "Male"},
    {"id": "br_001", "name": "Portuguese BR Female 1", "language": "Portuguese", "gender": "Female"},
    {"id": "br_003", "name": "Portuguese BR Female 2", "language": "Portuguese", "gender": "Female"},
    {"id": "br_004", "name": "Portuguese BR Female 3", "language": "Portuguese", "gender": "Female"},
    {"id": "br_005", "name": "Portuguese BR Male", "language": "Portuguese", "gender": "Male"},
    {"id": "id_001", "name": "Indonesian Female", "language": "Indonesian", "gender": "Female"},
    {"id": "jp_001", "name": "Japanese Female 1", "language": "Japanese", "gender": "Female"},
    {"id": "jp_003", "name": "Japanese Female 2", "language": "Japanese", "gender": "Female"},
    {"id": "jp_005", "name": "Japanese Female 3", "language": "Japanese", "gender": "Female"},
    {"id": "jp_006", "name": "Japanese Male", "language": "Japanese", "gender": "Male"},
    {"id": "kr_002", "name": "Korean Male 1", "language": "Korean", "gender": "Male"},
    {"id": "kr_003", "name": "Korean Female", "language": "Korean", "gender": "Female"},
    {"id": "kr_004", "name": "Korean Male 2", "language": "Korean", "gender": "Male"},
    {"id": "en_male_narration", "name": "Narrator", "language": "English", "gender": "Male"},
    {"id": "en_male_funny", "name": "Funny", "language": "English", "gender": "Male"},
    {"id": "en_female_emotional", "name": "Emotional", "language": "English", "gender": "Female"}
]

@app.get("/tts")
async def text_to_speech(voice: str = "", text: str = ""):
    if not voice or not text or voice.strip() == "" or text.strip() == "":
        return JSONResponse(
            content={
                "message": "The parameters 'voice' and 'text' are required"
            },
            status_code=400
        )

    # Verify that the voice exists
    voice_exists = any(v['id'] == voice for v in VOICES)
    if not voice_exists:
        return JSONResponse(
            content={
                "message": f"Voice '{voice}' not found. Use /voices to see available voices"
            },
            status_code=404
        )

    try:
        # Call TikTok TTS API
        response = requests.post(
            f"{WEILBYTE_ENDPOINT}/api/generation",
            json={"text": text, "voice": voice},
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        result = response.json()

        if not result.get('success') or result.get('data') is None:
            return JSONResponse(
                content={
                    "message": "Error generating audio"
                },
                status_code=500
            )

        # Decode Base64 audio
        audio_bytes = base64.b64decode(result['data'])
        audio_buffer = BytesIO(audio_bytes)

        return StreamingResponse(
            audio_buffer,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=audio.mp3"
            }
        )

    except requests.exceptions.Timeout:
        return JSONResponse(
            content={
                "message": "Timeout: The TTS service took too long to respond"
            },
            status_code=504
        )
    except Exception as e:
        return JSONResponse(
            content={
                "message": "Error processing the request"
            },
            status_code=500
        )

@app.get("/api/tts")
async def text_to_speech_api(voice: str = "", text: str = ""):
    return await text_to_speech(voice, text)

@app.get("/voices")
async def list_voices():
    return JSONResponse(
        content={
            "total": len(VOICES),
            "voices": VOICES
        },
        status_code=200
    )

@app.get("/api/voices")
async def list_voices_api():
    return await list_voices()
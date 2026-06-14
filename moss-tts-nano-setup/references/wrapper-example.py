#!/usr/bin/env python3
"""
MOSS-TTS-Nano wrapper for Hermes TTS command provider.

使用方式:
  python3 moss_tts_wrapper.py <text_input_path> <output_audio_path> [format] [mode]

mode: voice_clone (預設) | demo
format: ogg (預設)

voice_clone: infer.py direct call → WAV → ffmpeg OGG Opus → Telegram voice message
demo:       FastAPI /api/generate → Vorbis → direct output
"""
import subprocess, sys, os, tempfile, urllib.request, json, base64

VOICE_PROFILE = os.path.expanduser("~/MOSS-TTS-Nano/voice_profiles/yinyu_voice.wav")
INFER_SCRIPT  = os.path.expanduser("~/MOSS-TTS-Nano/infer.py")
VENV_PYTHON   = os.path.expanduser("~/.venvs/moss-tts/bin/python")


def voice_clone(text: str, output_path: str) -> None:
    """infer.py voice_clone → WAV → OGG Opus"""
    tmp_wav = output_path + ".wav"
    cmd = [VENV_PYTHON, INFER_SCRIPT,
           "--text", text,
           "--output-audio-path", tmp_wav,
           "--mode", "voice_clone",
           "--prompt-audio-path", VOICE_PROFILE]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise RuntimeError(f"infer.py failed: {r.stderr}")

    # WAV → OGG Opus（Telegram 語音格式）
    subprocess.run(["ffmpeg", "-y", "-i", tmp_wav,
                    "-c:a", "libopus", "-b:a", "32k", output_path],
                   capture_output=True, timeout=60)
    os.unlink(tmp_wav)


def demo_mode(text: str, output_path: str, demo_id: str = "demo-2") -> None:
    """走 FastAPI /api/generate，回傳 Vorbis"""
    req = urllib.request.Request(
        "http://localhost:8001/api/generate",
        data=json.dumps({"text": text, "demo_id": demo_id}).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read())
    audio = base64.b64decode(data["audio_base64"])
    with open(output_path, "wb") as f:
        f.write(audio)


def main():
    if len(sys.argv) < 3:
        print("Usage: moss_tts_wrapper.py <text_input_path> <output_audio_path> [format] [mode]",
              file=sys.stderr)
        sys.exit(1)

    text_path = sys.argv[1]
    output_path = sys.argv[2]
    target_format = sys.argv[3] if len(sys.argv) > 3 else "ogg"
    mode = sys.argv[4] if len(sys.argv) > 4 else "voice_clone"

    with open(text_path, "r", encoding="utf-8") as f:
        text = f.read().strip()

    if not text:
        print("Error: empty input text", file=sys.stderr)
        sys.exit(1)

    if mode == "demo":
        demo_mode(text, output_path)
    else:
        voice_clone(text, output_path)

    print(f"Generated: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
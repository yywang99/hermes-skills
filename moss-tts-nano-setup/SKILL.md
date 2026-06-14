---
name: moss-tts-nano-setup
description: MOSS-TTS-Nano 本地安裝、FastAPI service、voice clone 音色訓練、Telegram 語音整合。基於 OpenMOSS/MOSS-TTS-Nano (Apache 2.0)。
triggers:
  - "moss tts 安裝"
  - "moss tts nano setup"
  - "moss tts voice clone"
  - "MOSS TTS 本地"
  - "moss-tts-nano"
---

# MOSS-TTS-Nano Setup & Voice Clone Guide

> **版權宣告**：本 skill 參考 [OpenMOSS/MOSS-TTS-Nano](https://github.com/OpenMOSS/MOSS-TTS-Nano)（Apache License 2.0）。使用請保留版權聲明。

## 系統架構

```
使用者文字 → FastAPI (localhost:8001) → MOSS-TTS-Nano infer.py
                                        ├── demo 模式（預設音色，透過 /api/generate）
                                        └── voice_clone 模式（自訂音色，繞過 API 直接 call infer.py）
                                      → WAV → ffmpeg 轉 OGG Opus → Telegram 語音訊息
```

## 1. 安裝 MOSS-TTS-Nano

```bash
# 建議用 venv 隔離，避免污染系統
python3 -m venv ~/.venvs/moss-tts
source ~/.venvs/moss-tts/bin/activate

# Clone 並安裝
git clone https://github.com/OpenMOSS/MOSS-TTS-Nano.git ~/MOSS-TTS-Nano
cd ~/MOSS-TTS-Nano
pip install -e .
```

**相依檢查**（`apt` / `brew`）:
```bash
ffmpeg -version   # 音訊轉換用，必須有 libopus 支援
```

驗證安裝：
```bash
python infer.py --text "測試語音" --output-audio-path /tmp/test.wav --mode demo --demo-id demo-2
```

---

## 2. FastAPI Service（Demo 音色）

適用場景：直接用預設音色（`demo-2/zh_6` 等），不走 voice clone。

### 啟動服務

```bash
cd ~/MOSS-TTS-Nano
source ~/.venvs/moss-tts/bin/activate
python app.py --device cpu  # 或 cuda
```

預設 port `8001`。服務支援 `/api/generate`（POST），接受 `text` + `demo_id`。

### 驗證
```bash
curl -X POST http://localhost:8001/api/generate \
  -F "text=你好" \
  -F "demo_id=demo-2" \
  --output /tmp/test_api.ogg
```

> **注意**：FastAPI 輸出為 Vorbis/Ogg，傳 Telegram 語音訊息需在 Hermes `config.yaml` 中設定 wrapper 指令碼處理轉檔（見第四節）。

---

## 3. Voice Clone 音色訓練與使用

### 3.1 準備音色音檔

需求：
- **格式**：WAV，16-bit PCM
- **時長**：30 秒 ~ 5 分鐘（建議 1-3 分鐘）
- **品質**：清晰、無音樂、無背景噪音、無 Echo
- **內容**：語音朗讀（用於對齊文字）或純語音（口語模式）

**檔案位置**：`~/MOSS-TTS-Nano/voice_profiles/your_voice.wav`

```bash
# 轉換格式（若需）
ffmpeg -i source.mp3 -ar 16000 -ac 1 -ab 128k -f wav voice.wav
```

### 3.2 使用 Voice Clone 模式

直接呼叫 `infer.py`（推薦用 venv python）：
```bash
source ~/.venvs/moss-tts/bin/activate

python infer.py \
  --text "要說的內容" \
  --output-audio-path output.wav \
  --mode voice_clone \
  --prompt-audio-path ~/MOSS-TTS-Nano/voice_profiles/your_voice.wav
```

**可用音色模式**：
| mode | 說明 |
|------|------|
| `demo` | 預設音色（`--demo-id demo-2` 等）|
| `voice_clone` | 自訂音色（`--prompt-audio-path`）|

**常用 demo IDs**：`demo-1`（男聲）, `demo-2`（女聲預設）, `demo-3`, `zh_1` ~ `zh_9`（中文音色）

### 3.3 訓練新音色（Fine-tuning）

```bash
cd ~/MOSS-TTS-Nano/finetuning
# 見 finetuning/README.md 完整說明
```

---

## 4. Hermes TTS 整合（Wrapper Script）

Hermes 的 `text_to_speech` 工具需要一個 wrapper 將 MOSS-TTS 輸出轉為 Telegram 可接受格式。建議放在 `~/MOSS-TTS-Nano/moss_tts_wrapper.py`。

### wrapper.py 核心邏輯

```python
#!/usr/bin/env python3
"""
MOSS-TTS-Nano wrapper for Hermes TTS command provider.
voice_clone 模式：直接 call infer.py → WAV → ffmpeg OGG Opus
demo 模式：走 FastAPI → 回傳 Vorbis
"""
import subprocess, sys, os, tempfile, urllib.request, json, base64

VOICE_PROFILE = os.path.expanduser("~/MOSS-TTS-Nano/voice_profiles/yinyu_voice.wav")
INFER_SCRIPT  = os.path.expanduser("~/MOSS-TTS-Nano/infer.py")
VENV_PYTHON   = os.path.expanduser("~/.venvs/moss-tts/bin/python")

def voice_clone(text: str, output_path: str):
    """infer.py voice_clone → WAV → OGG Opus"""
    cmd = [VENV_PYTHON, INFER_SCRIPT,
           "--text", text, "--output-audio-path", output_path + ".wav",
           "--mode", "voice_clone", "--prompt-audio-path", VOICE_PROFILE]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise RuntimeError(f"infer.py failed: {r.stderr}")
    # WAV → OGG Opus（Telegram 語音格式）
    subprocess.run(["ffmpeg", "-y", "-i", output_path + ".wav",
                    "-c:a", "libopus", "-b:a", "32k", output_path],
                   capture_output=True, timeout=60)
    os.unlink(output_path + ".wav")

def demo_mode(text: str, output_path: str, demo_id: str = "demo-2"):
    """走 FastAPI，回傳 Vorbis"""
    req = urllib.request.Request(
        "http://localhost:8001/api/generate",
        data=json.dumps({"text": text, "demo_id": demo_id}).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read())
    audio = base64.b64decode(data["audio_base64"])
    with open(output_path, "wb") as f:
        f.write(audio)

if __name__ == "__main__":
    text  = open(sys.argv[1]).read().strip()
    out   = sys.argv[2]
    mode  = sys.argv[3] if len(sys.argv) > 3 else "voice_clone"
    voice_clone(text, out) if mode == "voice_clone" else demo_mode(text, out)
```

### Hermes config.yaml TTS 設定

```yaml
tts:
  default_provider: command
  providers:
    command:
      command: "python3 /home/yywang/MOSS-TTS-Nano/moss_tts_wrapper.py {text_path} {output_path} ogg voice_clone"
      voice_compatible: false    # 輸出為 OGG，text_to_speech 工具會當附件發送
      timeout: 300
```

重啟 Hermes：`hermes restart`

---

## 5. 常見問題

### Q: `voice_clone` 出現對齊錯誤
檢查音色音檔是否有乾淨的語音、沒有背景音。必要時重新錄製或剪輯。

### Q: ffmpeg 轉 OGG 失敗（無 libopus）
```bash
# Ubuntu/Debian
sudo apt install ffmpeg
ffmpeg -version | grep libopus   # 確認有 --enable-libopus

# macOS
brew install ffmpeg --with-libopus
```

### Q: FastAPI 服務停止
重啟服務：
```bash
cd ~/MOSS-TTS-Nano
source ~/.venvs/moss-tts/bin/activate
nohup python app.py --device cpu > ~/MOSS-TTS-Nano/app.log 2>&1 &
echo $! > ~/MOSS-TTS-Nano/app.pid
```

### Q: 輸出延遲太長
- 減少 `max_new_frames` 參數（預設 500）
- 改用 CPU 即時模式（`--device cpu --realtime`）

---

## 6. 參考資源

- **MOSS-TTS-Nano Repo**: https://github.com/OpenMOSS/MOSS-TTS-Nano
- **License**: Apache 2.0
- **Fine-tuning 文件**: `~/MOSS-TTS-Nano/finetuning/README.md`
- **預設音色 IDs**: `demo-1`, `demo-2`, `demo-3`, `zh_1` ~ `zh_9`
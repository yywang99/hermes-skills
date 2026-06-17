# hermes-skills

Hermes Agent 專用技能集合（Skills），用於日常任務、架構設定與工具整合。

## 目錄結構

```
hermes-skills/
  moss-tts-nano-setup/    # MOSS-TTS-Nano 安裝、voice clone、Telegram 語音整合
  ziwei-dou-shu/           # 紫微斗數命盤計算、排盤腳本
  iching/                  # 易經卜卦諮詢（硬幣法64卦）
```

## Skill 說明

### moss-tts-nano-setup
MOSS-TTS-Nano 本地安裝、FastAPI service、voice clone 音色訓練、Telegram 語音整合。基於 [OpenMOSS/MOSS-TTS-Nano](https://github.com/OpenMOSS/MOSS-TTS-Nano)（Apache 2.0）。

### ziwei-dou-shu
紫微斗數命盤計算機：支援農曆/國曆輸入、排星、布四大限、查詢星曜性質等。

### iching
易經卜卦諮詢：使用硬幣法（電腦模擬6次擲硬幣）自動產生本卦 + 互卦（過渡卦），提供卦辭、動爻詮釋與生活建議。適用於旅行卜事、人生抉择等命理諮詢。

## 關於

本 repo 為個人使用，請參考各 skill 內的版權宣告。

## 新增 Skill

在對應目錄下新增 `SKILL.md`，格式請參考各 skill 內的 frontmatter 範例。
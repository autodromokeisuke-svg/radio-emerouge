"""台本を1行ずつ音声合成し、1本の放送音源(MP3)に組み立てる。

- セリフ間に短い「間」を入れる
- assets/jingle.mp3 があれば冒頭と末尾に流す（任意）
- 音量をざっくり揃えてから書き出す
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from pydub import AudioSegment

from .tts import get_engine

ASSETS = Path(__file__).resolve().parent.parent / "assets"
TARGET_DBFS = -16.0


def _normalize(seg: AudioSegment) -> AudioSegment:
    if seg.dBFS == float("-inf"):
        return seg
    return seg.apply_gain(TARGET_DBFS - seg.dBFS)


def build(lines: list[dict[str, str]], tts_cfg: dict[str, Any]) -> AudioSegment:
    engine = get_engine(tts_cfg)
    engine.prepare()

    pause = AudioSegment.silent(duration=int(tts_cfg.get("pause_ms", 350)))
    show = AudioSegment.silent(duration=300)

    jingle_path = ASSETS / "jingle.mp3"
    jingle = None
    if jingle_path.exists():
        jingle = _normalize(AudioSegment.from_file(jingle_path))
        show += jingle + pause

    total = len(lines)
    failed = 0
    for i, ln in enumerate(lines, 1):
        try:
            seg = engine.synth(ln["speaker"], ln["text"])
            show += _normalize(seg) + pause
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"[warn] セリフ{i}の合成をスキップ: {e}")
        if i % 10 == 0 or i == total:
            print(f"[..] 収録中 {i}/{total}")

    if failed > total // 4:
        raise RuntimeError(f"合成失敗が多すぎる ({failed}/{total})。エンジン状態を確認して。")

    if jingle is not None:
        show += jingle

    minutes = len(show) / 1000 / 60
    print(f"[ok] 収録完了: 約{minutes:.1f}分")
    return show


def export_mp3(show: AudioSegment, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    show.export(out_path, format="mp3", bitrate="96k",
                tags={"artist": "えめるーじぇ"})
    size_mb = out_path.stat().st_size / 1024 / 1024
    print(f"[ok] 書き出し: {out_path} ({size_mb:.1f} MB)")

"""_strip_alpha_reading_gloss() の単体テスト（標準ライブラリ unittest のみ使用）。"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.build_audio import _strip_alpha_reading_gloss


class TestStripAlphaReadingGloss(unittest.TestCase):
    def test_alpha_abbreviation_with_katakana_gloss(self) -> None:
        self.assertEqual(
            _strip_alpha_reading_gloss("TSMC（ティーエスエムシー）"),
            "ティーエスエムシー",
        )

    def test_alnum_with_hyphen_and_katakana_gloss(self) -> None:
        self.assertEqual(
            _strip_alpha_reading_gloss("GPT-4（ジーピーティーフォー）"),
            "ジーピーティーフォー",
        )

    def test_kanji_gloss_is_not_replaced(self) -> None:
        self.assertEqual(
            _strip_alpha_reading_gloss("AI（人工知能）"),
            "AI（人工知能）",
        )

    def test_plain_sentence_without_parentheses_is_unchanged(self) -> None:
        text = "今日はいい天気だね、ルジェ。"
        self.assertEqual(_strip_alpha_reading_gloss(text), text)


if __name__ == "__main__":
    unittest.main()

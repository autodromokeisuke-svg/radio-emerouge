"""glossary_history.json 周りの単体テスト（標準ライブラリ unittest のみ使用）。"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.make_feed import load_recent_glossary_terms, record_glossary_term

JST = timezone(timedelta(hours=9))


class TestGlossaryHistory(unittest.TestCase):
    def test_record_then_load_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp)
            record_glossary_term(site, "20260707", "フィジカルAI")
            terms = load_recent_glossary_terms(site, days=30)
            self.assertEqual(terms, [{"date": "20260707", "term": "フィジカルAI"}])

    def test_old_entries_excluded_by_days_window(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp)
            old_date = (datetime.now(JST) - timedelta(days=40)).strftime("%Y%m%d")
            recent_date = (datetime.now(JST) - timedelta(days=5)).strftime("%Y%m%d")
            (site / "glossary_history.json").write_text(
                json.dumps([
                    {"date": old_date, "term": "古い用語"},
                    {"date": recent_date, "term": "新しい用語"},
                ], ensure_ascii=False),
                encoding="utf-8",
            )
            terms = load_recent_glossary_terms(site, days=30)
            self.assertEqual(terms, [{"date": recent_date, "term": "新しい用語"}])

    def test_record_same_date_key_overwrites_not_duplicates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp)
            record_glossary_term(site, "20260707", "フィジカルAI")
            record_glossary_term(site, "20260707", "OCR")
            terms = load_recent_glossary_terms(site, days=30)
            self.assertEqual(terms, [{"date": "20260707", "term": "OCR"}])

    def test_load_returns_empty_list_when_file_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp)
            terms = load_recent_glossary_terms(site, days=30)
            self.assertEqual(terms, [])

    def test_load_returns_empty_list_when_file_corrupt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp)
            (site / "glossary_history.json").write_text("{not valid json", encoding="utf-8")
            terms = load_recent_glossary_terms(site, days=30)
            self.assertEqual(terms, [])

    def test_record_with_empty_term_does_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp)
            record_glossary_term(site, "20260707", "")
            self.assertFalse((site / "glossary_history.json").exists())


if __name__ == "__main__":
    unittest.main()

import os
import shutil
import tempfile
import pytest
from scripts.generate_digest import parse_issue_body, generate_digest


def test_parse_issue_body_daily():
    sample_issue = """### 種類 / Type
日刊

### 日付 / Date
2026-10-05

### 概要 / Summary
テスト概要です。

### 注目トピック / Topics
- テストトピック1

### ツール & リリース / Tools
- テストツール1

### 考察・まとめ / Analysis
- テスト考察
"""
    parsed = parse_issue_body(sample_issue)
    assert parsed.get("type") == "日刊"
    assert parsed.get("date") == "2026-10-05"
    assert parsed.get("summary") == "テスト概要です。"
    assert parsed.get("topics") == "- テストトピック1"
    assert parsed.get("tools") == "- テストツール1"
    assert parsed.get("analysis") == "- テスト考察"


def test_parse_issue_body_weekly():
    sample_issue = """### 種類 / Type
週刊

### 日付 / Date
2026-10-05

### 概要 / Summary
今週のサマリーです。
"""
    parsed = parse_issue_body(sample_issue)
    assert parsed.get("type") == "週刊"
    assert parsed.get("date") == "2026-10-05"
    assert parsed.get("summary") == "今週のサマリーです。"


def test_generate_digest_daily_file_creation():
    temp_dir = tempfile.mkdtemp()
    try:
        path = generate_digest(
            digest_type="daily",
            date_str="2026-10-05",
            summary="Daily summary test",
            output_dir=temp_dir,
        )
        assert os.path.exists(path)
        assert path.endswith("articles/daily/2026-10-05-daily-digest.md") or path.endswith("daily/2026-10-05-daily-digest.md")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "# AI開発ダイジェスト (日刊) - 2026-10-05" in content
        assert "Daily summary test" in content
    finally:
        shutil.rmtree(temp_dir)


def test_generate_digest_weekly_file_creation():
    temp_dir = tempfile.mkdtemp()
    try:
        path = generate_digest(
            digest_type="weekly",
            date_str="2026-10-05",
            summary="Weekly summary test",
            output_dir=temp_dir,
        )
        assert os.path.exists(path)
        assert "weekly/2026-10-05-weekly-digest.md" in path
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "# AI開発ダイジェスト (週刊) - 2026-10-05" in content
        assert "Weekly summary test" in content
    finally:
        shutil.rmtree(temp_dir)


def test_generate_digest_from_issue_body():
    temp_dir = tempfile.mkdtemp()
    sample_body = """### 種類 / Type
週刊

### 日付 / Date
2026-10-05

### 概要 / Summary
Issueから生成された週刊ダイジェスト。
"""
    try:
        path = generate_digest(
            digest_type=None,
            issue_body=sample_body,
            output_dir=temp_dir,
        )
        assert os.path.exists(path)
        assert "weekly/2026-10-05-weekly-digest.md" in path
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "# AI開発ダイジェスト (週刊) - 2026-10-05" in content
        assert "Issueから生成された週刊ダイジェスト。" in content
    finally:
        shutil.rmtree(temp_dir)

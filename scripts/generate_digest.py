#!/usr/bin/env python3
"""
AI Development Digest Article Generator

This script parses template issues/PRs or CLI options to generate
Daily (日刊) and Weekly (週刊) AI Development Digest Markdown articles.
"""

import argparse
import os
import re
import sys
from datetime import datetime, timezone

DEFAULT_ARTICLES_DIR = "articles"

DAILY_TEMPLATE = """# AI開発ダイジェスト (日刊) - {date}

## 概要
{summary}

## 本日の注目ニュース & トピック
{topics}

## AI開発ツールの更新 & リリース
{tools}

## 技術考察・まとめ
{analysis}

---
*Generated automatically by AI Development Digest Workflow on {timestamp}*
"""

WEEKLY_TEMPLATE = """# AI開発ダイジェスト (週刊) - {date}

## 今週のハイライト
{summary}

## 主なトレンド & ニュース
{topics}

## 今週のモデル & OSSリリース
{tools}

## 来週の展望 & まとめ
{analysis}

---
*Generated automatically by AI Development Digest Workflow on {timestamp}*
"""


def parse_issue_body(body: str) -> dict:
    """
    Parses issue/PR markdown body with sections like:
    ### 種類 / Type
    日刊 (or 週刊)

    ### 日付 / Date
    2026-10-05

    ### 概要 / Summary
    ...
    """
    data = {}
    current_key = None
    buffer = []

    for line in body.splitlines():
        header_match = re.match(r"^###\s+(.+)$", line.strip())
        if header_match:
            if current_key:
                data[current_key] = "\n".join(buffer).strip()
                buffer = []
            current_key = header_match.group(1).strip()
        else:
            if current_key:
                buffer.append(line)

    if current_key:
        data[current_key] = "\n".join(buffer).strip()

    # Normalize key names
    normalized = {}
    for key, val in data.items():
        k_lower = key.lower()
        if "種類" in key or "type" in k_lower:
            normalized["type"] = val
        elif "日付" in key or "date" in k_lower:
            normalized["date"] = val
        elif "概要" in key or "summary" in k_lower:
            normalized["summary"] = val
        elif "トピック" in key or "topic" in k_lower or "ニュース" in key:
            normalized["topics"] = val
        elif "ツール" in key or "tool" in k_lower or "リリース" in key:
            normalized["tools"] = val
        elif "考察" in key or "まとめ" in k_lower or "analysis" in k_lower:
            normalized["analysis"] = val

    return normalized


def generate_digest(
    digest_type: str,
    date_str: str = None,
    summary: str = None,
    topics: str = None,
    tools: str = None,
    analysis: str = None,
    issue_body: str = None,
    output_dir: str = DEFAULT_ARTICLES_DIR,
) -> str:
    """
    Generates a digest article file and returns its path.
    """
    if issue_body:
        parsed = parse_issue_body(issue_body)
        digest_type = digest_type or parsed.get("type", "daily")
        date_str = date_str or parsed.get("date")
        summary = summary or parsed.get("summary")
        topics = topics or parsed.get("topics")
        tools = tools or parsed.get("tools")
        analysis = analysis or parsed.get("analysis")

    # Normalize type
    digest_type = (digest_type or "daily").strip().lower()
    if "週" in digest_type or "weekly" in digest_type:
        digest_type = "weekly"
    else:
        digest_type = "daily"

    # Default date to today UTC
    if not date_str:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    else:
        date_str = date_str.strip()

    # Fill defaults for content fields if missing
    summary = summary or "本日・今週のAI開発における主要なアップデートと注目トピックの概要です。"
    topics = topics or "- LLMおよびAIツールの最新動向\n-オープンソースモデルの進化と活用事例"
    tools = tools or "- 新機能および性能改善リリースのアップデート情報"
    analysis = analysis or "AI開発技術の継続的な進化により、開発効率化と適用範囲の拡大が期待されます。"

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    if digest_type == "weekly":
        content = WEEKLY_TEMPLATE.format(
            date=date_str,
            summary=summary,
            topics=topics,
            tools=tools,
            analysis=analysis,
            timestamp=timestamp,
        )
        sub_folder = os.path.join(output_dir, "weekly")
        file_name = f"{date_str}-weekly-digest.md"
    else:
        content = DAILY_TEMPLATE.format(
            date=date_str,
            summary=summary,
            topics=topics,
            tools=tools,
            analysis=analysis,
            timestamp=timestamp,
        )
        sub_folder = os.path.join(output_dir, "daily")
        file_name = f"{date_str}-daily-digest.md"

    os.makedirs(sub_folder, exist_ok=True)
    file_path = os.path.join(sub_folder, file_name)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Digest generated successfully: {file_path}")
    return file_path


def main():
    parser = argparse.ArgumentParser(description="Generate AI Development Digest Article")
    parser.add_argument("--type", choices=["daily", "weekly", "日刊", "週刊"], help="Digest type")
    parser.add_argument("--date", help="Date string (YYYY-MM-DD)")
    parser.add_argument("--summary", help="Summary text")
    parser.add_argument("--topics", help="Topics text")
    parser.add_argument("--tools", help="Tools & releases text")
    parser.add_argument("--analysis", help="Analysis / Conclusion text")
    parser.add_argument("--issue-body", help="Issue or PR body markdown string")
    parser.add_argument("--issue-file", help="Path to file containing Issue/PR body")
    parser.add_argument("--outdir", default=DEFAULT_ARTICLES_DIR, help="Output directory")

    args = parser.parse_args()

    issue_body = args.issue_body
    if args.issue_file and os.path.exists(args.issue_file):
        with open(args.issue_file, "r", encoding="utf-8") as f:
            issue_body = f.read()

    try:
        file_path = generate_digest(
            digest_type=args.type,
            date_str=args.date,
            summary=args.summary,
            topics=args.topics,
            tools=args.tools,
            analysis=args.analysis,
            issue_body=issue_body,
            output_dir=args.outdir,
        )
        sys.exit(0)
    except Exception as e:
        print(f"Error generating digest: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
check_memory.py — 扫描 MEMORY.md，报告 stale（28天未验证）记忆

支持两种格式：
1. 新格式：YAML frontmatter 块（<!-- ... -->），每个记忆独立 block
2. 老格式：§ 分隔的纯文本段落，根据内容中的日期判断

用法：
  python3 check_memory.py [--cleanup]
  --cleanup: 删除 status=dead 的记忆块
"""

import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

MEMORY_PATH = Path.home() / ".hermes" / "memories" / "MEMORY.md"
STALE_THRESHOLD_DAYS = 28
FRESH_THRESHOLD_DAYS = 7

def parse_frontmatter(block: str) -> dict:
    """从新格式记忆块中解析 YAML frontmatter"""
    fm = {}
    match = re.search(r'<!--\s*(.*?)\s*-->', block, re.DOTALL)
    if not match:
        return fm
    for line in match.group(1).strip().splitlines():
        if ':' in line:
            key, val = line.split(':', 1)
            fm[key.strip()] = val.strip()
    return fm

def extract_date_from_old_format(line: str) -> str:
    """从老格式行中提取日期（如 '2026-04-09 >'）"""
    match = re.search(r'(\d{4}-\d{2}-\d{2})', line)
    return match.group(1) if match else None

def get_status_from_fm(fm: dict) -> str:
    """根据 frontmatter 元数据判断状态"""
    status = fm.get('status', '')
    if status in ('dead',):
        return status
    created_str = fm.get('created_at', '')
    if not created_str:
        return 'unknown'
    try:
        last_verified_str = fm.get('last_verified', created_str)
        now = datetime.now()
        days_since_verified = (now - datetime.strptime(last_verified_str, '%Y-%m-%d')).days
        if days_since_verified > STALE_THRESHOLD_DAYS:
            return 'stale'
        elif days_since_verified <= FRESH_THRESHOLD_DAYS:
            return 'fresh'
        return 'valid'
    except (ValueError, TypeError):
        return 'unknown'

def get_status_from_date(date_str: str) -> str:
    """根据嵌入日期判断老格式记忆的状态"""
    if not date_str:
        return 'unknown'
    try:
        created = datetime.strptime(date_str, '%Y-%m-%d')
        now = datetime.now()
        days = (now - created).days
        if days > STALE_THRESHOLD_DAYS:
            return 'stale'
        elif days <= FRESH_THRESHOLD_DAYS:
            return 'fresh'
        return 'valid'
    except ValueError:
        return 'unknown'

def check_memory() -> dict:
    """扫描 MEMORY.md，返回各类记忆的统计"""
    if not MEMORY_PATH.exists():
        return {'error': f'MEMORY.md not found at {MEMORY_PATH}'}

    content = MEMORY_PATH.read_text()

    # 1. 先尝试匹配新格式（frontmatter block）
    new_format_blocks = []
    pattern = re.compile(
        r'(<!--\s*\n.*?\n-->)\s*\n?(.*?)(?=\n<!--|\Z)',
        re.DOTALL
    )
    for match in pattern.finditer(content):
        fm_block = match.group(1)
        body = match.group(2).strip()
        fm = parse_frontmatter(fm_block)
        new_format_blocks.append({
            'format': 'new',
            'id': fm.get('id', '(no id)'),
            'fm': fm,
            'body': body,
            'status': get_status_from_fm(fm),
        })

    # 2. 老格式：用 § 分隔，每个段落按日期判断
    old_format_entries = []
    sections = content.split('§')
    for section in sections:
        section = section.strip()
        if not section or section.startswith('<!--'):
            continue
        # 跳过已经是 new format 的
        if re.match(r'^\d{4}-\d{2}-\d{2}', section):
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', section)
            date_str = date_match.group(1) if date_match else None
            status = get_status_from_date(date_str)
            old_format_entries.append({
                'format': 'old',
                'id': date_str or '(undated)',
                'date': date_str,
                'body': section[:100],
                'status': status,
            })

    # 合并
    all_entries = new_format_blocks + old_format_entries

    stats = {'fresh': 0, 'valid': 0, 'stale': 0, 'dead': 0, 'unknown': 0}
    stale_entries = []
    for e in all_entries:
        stats[e['status']] += 1
        if e['status'] == 'stale':
            stale_entries.append(e)

    return {
        'new_format': new_format_blocks,
        'old_format': old_format_entries,
        'stats': stats,
        'stale': stale_entries,
    }

def main():
    cleanup = '--cleanup' in sys.argv

    result = check_memory()

    if 'error' in result:
        print(result['error'])
        sys.exit(1)

    print("=" * 55)
    print("MEMORY HYGIENE REPORT")
    print(f"Scanned: {MEMORY_PATH}")
    print(f"Checked: {datetime.now():%Y-%m-%d %H:%M}")
    print(f"Stale threshold: {STALE_THRESHOLD_DAYS} days")
    print(f"Fresh threshold: {FRESH_THRESHOLD_DAYS} days")
    print("=" * 55)

    stats = result['stats']
    total = sum(stats.values())
    print(f"\nTotal entries: {total}")
    print(f"  fresh:  {stats['fresh']}  (≤{FRESH_THRESHOLD_DAYS}d old)")
    print(f"  valid:  {stats['valid']}  ({FRESH_THRESHOLD_DAYS}-{STALE_THRESHOLD_DAYS}d old)")
    print(f"  stale:  {stats['stale']}  (>{STALE_THRESHOLD_DAYS}d old)")
    print(f"  dead:   {stats['dead']}")
    print(f"  unknown:{stats['unknown']}")

    if result['stale']:
        print(f"\n⚠️  STALE MEMORIES ({len(result['stale'])}):")
        print("-" * 55)
        for e in result['stale']:
            fmt_label = "[NEW]" if e['format'] == 'new' else "[OLD]"
            if e['format'] == 'new':
                days = (datetime.now() - datetime.strptime(
                    e['fm'].get('last_verified', e['fm'].get('created_at', '2020-01-01')),
                    '%Y-%m-%d')).days
                preview = e['body'][:80]
            else:
                days = (datetime.now() - datetime.strptime(e['date'], '%Y-%m-%d')).days
                preview = e['body'][:80]
            print(f"\n  {fmt_label} {e['id']}")
            print(f"      stale for: {days} days")
            print(f"      preview: {preview}...")

    if not result['stale']:
        print("\n✅ No stale memories found.")

    return 0

if __name__ == '__main__':
    sys.exit(main())

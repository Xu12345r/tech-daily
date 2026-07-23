#!/usr/bin/env python3
"""Daily cover image rotation for tech-daily."""
import re
from datetime import date

COVERS = [
    'images/doubao_aidigi_sm.jpg',      # AI&数字化
    'images/doubao_hardtech_sm.jpg',    # 硬科技&半导体
    'images/doubao_aerospace_sm.jpg',   # 航天&物理
    'images/doubao_biotech_sm.jpg',     # 生物&能源
]
INDEX = '/Users/jalleen/Desktop/tech-daily/index.html'
BASE = 'https://tech-daily-tau.vercel.app'

today = date.today()
idx = today.toordinal() % 4
cover_url = f'{BASE}/{COVERS[idx]}'
month_day = f'{today.month}月{today.day}日'

with open(INDEX, 'r') as f:
    html = f.read()

new_html = re.sub(
    r'<meta property="og:url" content="[^"]*"',
    f'<meta property="og:url" content="{BASE}/"',
    html
)

new_html = re.sub(
    r'<meta property="og:image" content="[^"]*"',
    f'<meta property="og:image" content="{cover_url}"',
    new_html
)

new_html = re.sub(
    r'<meta property="og:title" content="\d+月\d+日 科技前沿日报',
    f'<meta property="og:title" content="{month_day} 科技前沿日报',
    new_html
)

with open(INDEX, 'w') as f:
    f.write(new_html)

print(f'Cover rotated: {cover_url} | Date: {month_day}')

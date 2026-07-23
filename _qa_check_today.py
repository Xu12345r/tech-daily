#!/usr/bin/env python3
"""QA check for tech-daily — runtime adapted"""
import json, os, sys
from datetime import date

BASE = "/Users/jalleen/Desktop/tech-daily"
today = date.today()
DATE = today.strftime("%Y-%m-%d")
DATE_NUM = today.strftime("%Y%m%d")
DATE_SHORT = today.strftime("%m%d")
DATE_CN = today.strftime("%m月%d日").lstrip("0").replace("月0", "月")

errors = []
warnings = []
fixes_applied = []

# === 1. FILE EXISTENCE ===
required = [
    f"data/{DATE_NUM}.json",
    f"tts_{DATE_NUM}.txt",
    f"audio/{DATE_NUM}.mp3",
    f"audio/{DATE_NUM}_sm.mp3",
    f"cover_{DATE_SHORT}.jpg",
    "index.html",
]
for f in required:
    path = os.path.join(BASE, f)
    if not os.path.exists(path):
        errors.append(f"Missing file: {f}")
    else:
        print(f"✅ Found: {f}")

# === 2. JSON VALIDATION ===
json_path = os.path.join(BASE, f"data/{DATE_NUM}.json")
try:
    with open(json_path) as f:
        data = json.load(f)

    for field in ['date', 'weekday', 'lunar', 'cover_quote', 'categories']:
        if field not in data:
            errors.append(f"JSON missing field: {field}")

    if data.get('date') != DATE:
        errors.append(f"Wrong date in JSON: {data.get('date')}")
    else:
        print(f"✅ JSON date: {data['date']}")
        print(f"✅ JSON weekday: {data.get('weekday')}")
        print(f"✅ JSON lunar: {data.get('lunar')}")
        print(f"✅ JSON cover_quote: {str(data.get('cover_quote'))[:50]}...")

    cats = data.get('categories', [])
    if len(cats) != 4:
        errors.append(f"Expected 4 categories, got {len(cats)}")

    total_items = 0
    expected_ids = set()
    for i, cat in enumerate(cats):
        for key in ['name', 'icon']:
            if key not in cat:
                errors.append(f"Category {i} missing {key}")
        items = cat.get('items', [])
        for j, item in enumerate(items):
            total_items += 1
            for key in ['id', 'title', 'body', 'source']:
                if key not in item:
                    errors.append(f"Cat {i} item {j} missing {key}")
                elif item[key] is None or (isinstance(item[key], str) and not item[key].strip()):
                    errors.append(f"Cat {i} item {j} has empty {key}")
            if item.get('id'):
                expected_ids.add(item['id'])

    if total_items != 12:
        errors.append(f"Expected 12 items, got {total_items}")
    else:
        print(f"✅ Total items: {total_items}")

    expected = set(f'{n:02d}' for n in range(1, 13))
    if expected_ids != expected:
        errors.append(f"Item IDs mismatch: expected {expected}, got {expected_ids}")
    else:
        print(f"✅ Item IDs: {sorted(expected_ids)}")

except Exception as e:
    errors.append(f"JSON parse error: {e}")

# === 3. TTS vs JSON consistency ===
tts_path = os.path.join(BASE, f"tts_{DATE_NUM}.txt")
try:
    with open(tts_path) as f:
        tts_text = f.read()

    missing_titles = []
    for cat in data.get('categories', []):
        for item in cat.get('items', []):
            title = item['title']
            if title not in tts_text:
                missing_titles.append(title)
    if missing_titles:
        for t in missing_titles:
            errors.append(f"TTS missing title: {t}")
    else:
        print(f"✅ TTS: {len(tts_text)} chars, all titles present")

except Exception as e:
    errors.append(f"TTS check error: {e}")

# === 4. FILE PERMISSIONS ===
perm_checks = {
    f"audio/{DATE_NUM}.mp3": 0o644,
    f"audio/{DATE_NUM}_sm.mp3": 0o644,
    f"data/{DATE_NUM}.json": 0o644,
    f"tts_{DATE_NUM}.txt": 0o644,
}
for fpath, expected_perm in perm_checks.items():
    full = os.path.join(BASE, fpath)
    if os.path.exists(full):
        mode = os.stat(full).st_mode
        perms = mode & 0o777
        if perms != expected_perm:
            warnings.append(f"Permissions {oct(perms)} on {fpath} (expected {oct(expected_perm)})")
            try:
                os.chmod(full, expected_perm)
                fixes_applied.append(f"Fixed permissions on {fpath}: {oct(perms)} → {oct(expected_perm)}")
            except Exception as e:
                errors.append(f"Failed to fix permissions on {fpath}: {e}")
        else:
            print(f"✅ Permissions OK: {fpath}")

# === 5. AUDIO FILE SIZE SANITY ===
audio_main = os.path.join(BASE, f"audio/{DATE_NUM}.mp3")
audio_sm = os.path.join(BASE, f"audio/{DATE_NUM}_sm.mp3")
if os.path.exists(audio_main):
    size = os.path.getsize(audio_main)
    if size < 100000:
        warnings.append(f"Main audio file too small: {size} bytes")
    else:
        print(f"✅ Audio (main): {size} bytes ({size/1024:.0f} KB)")
if os.path.exists(audio_sm):
    size = os.path.getsize(audio_sm)
    if size < 50000:
        warnings.append(f"Small audio file too small: {size} bytes")
    else:
        print(f"✅ Audio (sm): {size} bytes ({size/1024:.0f} KB)")

# === 6. INDEX.HTML DATE CHECK ===
index_path = os.path.join(BASE, "index.html")
if os.path.exists(index_path):
    with open(index_path) as f:
        html = f.read()
    if DATE_CN not in html and DATE_SHORT not in html:
        warnings.append(f"index.html may not be updated to {DATE_CN}")
    else:
        print(f"✅ index.html: date matches {DATE_CN}")

# === 7. COVER IMAGE ===
cover_path = os.path.join(BASE, f"cover_{DATE_SHORT}.jpg")
if os.path.exists(cover_path):
    size = os.path.getsize(cover_path)
    if size < 10000:
        warnings.append(f"Cover image too small: {size} bytes")
    else:
        print(f"✅ Cover: {size} bytes ({size/1024:.0f} KB)")

# === SUMMARY ===
print()
print("="*60)
if errors:
    print(f"❌ {len(errors)} FAILURE(S):")
    for e in errors:
        print(f"   ❌ {e}")
else:
    print("✅ No failures found")

if warnings:
    print(f"⚠️  {len(warnings)} WARNING(S):")
    for w in warnings:
        print(f"   ⚠️  {w}")
else:
    print("✅ No warnings")

if fixes_applied:
    print(f"🔧 {len(fixes_applied)} FIX(ES) applied:")
    for f in fixes_applied:
        print(f"   🔧 {f}")
else:
    print("✅ Nothing to fix")

sys.exit(0 if not errors else 1)

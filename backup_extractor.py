"""
Phone Backup Extractor - ClearDrive
=====================================
Extracts everything from Phone_Backups folder
Organises by Person → Category

Usage:
    python phone_backup_extractor.py --dry-run
    python phone_backup_extractor.py

Output:
    D:\Phone_Backups_Organized\
    ├── Person1\
    │   ├── Photos\
    │   ├── Videos\
    │   ├── Documents\
    │   ├── Audio\
    │   ├── Other\
    │   └── Skipped\
    ├── Person2\
    │   └── ...
    └── Person3\
        └── ...
"""

import os
import shutil
import hashlib
import argparse
from pathlib import Path
from datetime import datetime

# ─── File type buckets ────────────────────────────────────────────────────────
PHOTOS    = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif',
             '.heic', '.heif', '.webp', '.raw', '.cr2', '.nef', '.arw'}
VIDEOS    = {'.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.3gp',
             '.m4v', '.webm', '.mpg', '.mpeg'}
AUDIO     = {'.mp3', '.wav', '.aac', '.m4a', '.ogg', '.flac', '.amr',
             '.opus', '.wma'}
DOCUMENTS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
             '.txt', '.csv', '.odt', '.ods', '.rtf'}

# ─── Skip these completely — pure junk ───────────────────────────────────────
SKIP_EXTENSIONS = {
    '.tmp', '.log', '.db', '.db-wal', '.db-shm',
    '.nomedia', '.meta1', '.json', '.xml',
    '.ini', '.cfg', '.bak', '.dat'
}

SKIP_FILENAMES = {
    '.nomedia', 'thumbdata', '.clear_sdcard',
    '.sdcard_version', '.meta1', 'thumbdata3',
    'thumbdata4', 'thumbdata5'
}

# ─── Person mapping ──────────────────────────────────────────────────────────
# Edit this to match YOUR folder names → person names
# Key: part of folder name (lowercase) → Person label
PERSON_MAP = {
    'samsung_backup':    'Person1',
    'photo backup':      'Person1',
    'jan_2026':          'Person1',
    'full phone backup': 'Person2',
    'august 2025_p2':    'Person2',
    'august 2025_p3':    'Person3',
}

def get_person(src_path, source_root):
    """Figure out which person a file belongs to based on its top-level folder."""
    try:
        rel = src_path.relative_to(source_root)
        top_folder = rel.parts[0].lower()
        for key, person in PERSON_MAP.items():
            if key in top_folder or top_folder in key:
                return person
    except Exception:
        pass
    return "Unknown"

# ─── Helpers ─────────────────────────────────────────────────────────────────

def get_category(path):
    ext = Path(path).suffix.lower()
    if ext in PHOTOS:     return "Photos"
    if ext in VIDEOS:     return "Videos"
    if ext in AUDIO:      return "Audio"
    if ext in DOCUMENTS:  return "Documents"
    return "Other"

def get_file_hash(path):
    """MD5 of first 64KB for fast duplicate detection."""
    h = hashlib.md5()
    try:
        with open(path, 'rb') as f:
            for _ in range(8):
                data = f.read(8192)
                if not data:
                    break
                h.update(data)
    except Exception:
        return None
    return h.hexdigest()

def safe_copy_path(dest_dir, filename):
    """Returns a safe destination path, adds _1 _2 if name conflict."""
    dest = dest_dir / filename
    if not dest.exists():
        return dest
    stem = Path(filename).stem
    suffix = Path(filename).suffix
    counter = 1
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        dest = dest_dir / new_name
        if not dest.exists():
            return dest
        counter += 1

def should_skip(path):
    """Returns True if file should be skipped."""
    name = path.name.lower()
    ext = path.suffix.lower()
    # skip junk extensions
    if ext in SKIP_EXTENSIONS:
        return True
    # skip junk filenames
    if name in SKIP_FILENAMES:
        return True
    # skip hidden files
    if name.startswith('.'):
        return True
    # skip very small files under 5KB (thumbnails, cache)
    try:
        if path.stat().st_size < 5 * 1024:
            return True
    except Exception:
        return True
    return False

# ─── Core ─────────────────────────────────────────────────────────────────────

def extract(source, output, dry_run=False):
    source = Path(source)
    output = Path(output).resolve()

    print(f"\n{'='*60}")
    print(f"  Phone Backup Extractor")
    print(f"{'='*60}")
    print(f"  Mode   : {'DRY RUN' if dry_run else 'COPY'}")
    print(f"  Source : {source}")
    print(f"  Output : {output}")
    print(f"{'='*60}\n")

    # collect all files
    all_files = []
    for root, dirs, files in os.walk(source):
        # skip output folder if inside source
        dirs[:] = [d for d in dirs
                   if Path(root, d).resolve() != output
                   and not d.startswith('.')]
        for f in files:
            all_files.append(Path(root) / f)

    print(f"[→] Found {len(all_files)} total files\n")

    seen_hashes = {}
    # Build stats dict dynamically from PERSON_MAP values + Unknown
    people = sorted(set(PERSON_MAP.values())) + ["Unknown"]
    stats = {p: 0 for p in people}
    stats["duplicates"] = 0
    stats["skipped"] = 0
    stats["errors"] = 0

    for i, src in enumerate(all_files, 1):
        try:
            person   = get_person(src, source)
            category = get_category(src)

            # skip junk → goes to Person\Skipped\
            if should_skip(src):
                stats["skipped"] += 1
                skip_dir = output / person / "Skipped"
                print(f"  [SKP]  {src.name:45s} → {person}/Skipped/")
                if not dry_run:
                    skip_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(str(src), safe_copy_path(skip_dir, src.name))
                continue

            dest_dir = output / person / category

            # duplicate check (per person)
            file_hash = get_file_hash(src)
            dup_key = f"{person}:{file_hash}"
            if file_hash and dup_key in seen_hashes:
                stats["duplicates"] += 1
                print(f"  [DUP]  {src.name:45s} ({person})")
                continue
            if file_hash:
                seen_hashes[dup_key] = src

            dest_path = safe_copy_path(dest_dir, src.name)
            rel = dest_path.relative_to(output)
            print(f"  [{'DRY' if dry_run else 'CPY'}]  {src.name:45s} → {rel}")

            if not dry_run:
                dest_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(src), dest_path)

            stats[person] += 1

        except Exception as e:
            stats["errors"] += 1
            print(f"  [ERR]  {src.name} — {e}")

        if i % 200 == 0:
            print(f"\n  ... {i}/{len(all_files)} files processed ...\n")

    # summary
    total = sum(stats[p] for p in people)
    print(f"\n{'='*60}")
    print(f"  {'Would copy' if dry_run else 'Copied'} {total} files")
    for p in people:
        print(f"  {p:<12}: {stats[p]}")
    print(f"  Duplicates: {stats['duplicates']} skipped")
    print(f"  Junk skip : {stats['skipped']} → Person/Skipped/")
    print(f"  Errors    : {stats['errors']}")
    print(f"{'='*60}")
    if dry_run:
        print("\n  ✅ Dry run done. Run without --dry-run to actually copy.")
    else:
        print(f"\n  ✅ Done! Check: {output}")
    print()

# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Phone Backup Extractor — categorises all files into Photos/Videos/Docs/Audio/Other"
    )
    parser.add_argument(
        '--source', default=r"D:\Phone_Backups",
        help='Phone backups folder (default: D:\\Phone_Backups)'
    )
    parser.add_argument(
        '--output', default=r"D:\Phone_Backups_Organized",
        help='Output folder (default: D:\\Phone_Backups_Organized)'
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Preview without copying anything'
    )
    args = parser.parse_args()
    extract(args.source, args.output, dry_run=args.dry_run)

if __name__ == '__main__':
    main()

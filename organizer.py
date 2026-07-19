"""
ClearDrive — Family Drive Organizer
=====================================
Level 1: Extract everything from scattered folders
Level 2: Group by Year > Month
Level 3: Inside each month -> Pictures / Videos / Documents / Audio / Other

Usage:
    python organizer.py --source "D:\Photos" --output "D:\Organized" --dry-run
    python organizer.py --source "D:\Photos" --output "D:\Organized"

Multiple source folders:
    python organizer.py --source "D:\Camera" "D:\Downloads" "D:\TRIPS" --output "D:\Organized"

Always dry run first to preview before actually copying anything.
"""

import os
import sys
import shutil
import hashlib
import argparse
from pathlib import Path
from datetime import datetime

# ─── PIL for EXIF (install if missing) ───────────────────────────────────────
try:
    from PIL import Image
    from PIL.ExifTags import TAGS
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("[!] Pillow not installed. EXIF reading disabled.")
    print("    Run: pip install Pillow")
    print("    Falling back to file modified date.\n")

# ─── File type buckets ────────────────────────────────────────────────────────
PICTURES   = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif',
              '.heic', '.heif', '.webp', '.raw', '.cr2', '.nef', '.arw'}
VIDEOS     = {'.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.3gp',
              '.m4v', '.webm', '.mpg', '.mpeg'}
AUDIO      = {'.mp3', '.wav', '.aac', '.m4a', '.ogg', '.flac', '.amr',
              '.opus', '.wma'}
DOCUMENTS  = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
              '.txt', '.csv', '.odt', '.ods', '.rtf'}

MONTH_NAMES = {
    1: "01 - January",   2: "02 - February",  3: "03 - March",
    4: "04 - April",     5: "05 - May",        6: "06 - June",
    7: "07 - July",      8: "08 - August",     9: "09 - September",
    10: "10 - October",  11: "11 - November",  12: "12 - December"
}

# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_file_hash(path, chunk=8192):
    """MD5 of first 64KB — fast duplicate check."""
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for _ in range(8):
            data = f.read(chunk)
            if not data:
                break
            h.update(data)
    return h.hexdigest()

def get_exif_date(path):
    """Try to read DateTimeOriginal from EXIF."""
    if not PIL_AVAILABLE:
        return None
    try:
        # skip files over 200MB — no point loading huge videos into PIL
        if os.path.getsize(path) > 200 * 1024 * 1024:
            return None
        img = Image.open(path)
        exif_data = img._getexif()
        if not exif_data:
            return None
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == 'DateTimeOriginal':
                return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
    except Exception:
        return None
    return None

def get_file_date(path):
    """Best date we can get: EXIF → file modified date."""
    ext = Path(path).suffix.lower()
    if ext in PICTURES:
        exif = get_exif_date(path)
        if exif:
            return exif
    stat = os.stat(path)
    # st_ctime on Windows = creation time (not reliable), use st_mtime only
    return datetime.fromtimestamp(stat.st_mtime)

def get_category(path):
    ext = Path(path).suffix.lower()
    if ext in PICTURES:  return "Pictures"
    if ext in VIDEOS:    return "Videos"
    if ext in AUDIO:     return "Audio"
    if ext in DOCUMENTS: return "Documents"
    return "Other"

def is_whatsapp(path):
    parts = str(path).lower()
    return 'whatsapp' in parts

def safe_filename(dest_dir, filename):
    """If file exists at dest, add _1, _2 etc."""
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

# ─── Core logic ───────────────────────────────────────────────────────────────

def collect_files(source_dirs, output_dir):
    """Recursively collect all files from source dirs, skipping output dir."""
    output_dir = Path(output_dir).resolve()
    all_files = []
    for src in source_dirs:
        src = Path(src).resolve()
        if not src.exists():
            print(f"[!] Source not found, skipping: {src}")
            continue
        for root, dirs, files in os.walk(src):
            # skip hidden folders AND the output folder (avoids infinite loop)
            dirs[:] = [d for d in dirs if not d.startswith('.')
                       and Path(root, d).resolve() != output_dir]
            for f in files:
                if f.startswith('.'):
                    continue
                all_files.append(Path(root) / f)
    return all_files

def organize(source_dirs, output_dir, dry_run=False, move=False):
    output_dir = Path(output_dir)
    
    print(f"\n{'='*60}")
    print(f"  Family Drive Organizer")
    print(f"{'='*60}")
    print(f"  Mode     : {'DRY RUN (nothing will move)' if dry_run else ('MOVE' if move else 'COPY')}")
    print(f"  Output   : {output_dir}")
    print(f"  Sources  : {', '.join(str(s) for s in source_dirs)}")
    print(f"{'='*60}\n")

    files = collect_files(source_dirs, output_dir)
    print(f"[→] Found {len(files)} files\n")

    seen_hashes = {}   # hash → dest path (duplicate tracking)
    stats = {"copied": 0, "skipped_dup": 0, "skipped_same": 0, "errors": 0, "whatsapp": 0}

    for i, src_path in enumerate(files, 1):
        try:
            # ── get date ──────────────────────────────────────────────────
            date = get_file_date(src_path)
            year = str(date.year)
            month = MONTH_NAMES.get(date.month, f"{date.month:02d}")
            category = get_category(src_path)

            # ── WhatsApp goes to its own folder ───────────────────────────
            if is_whatsapp(src_path):
                dest_dir = output_dir / "WhatsApp" / category
                stats["whatsapp"] += 1
            else:
                dest_dir = output_dir / year / month / category

            # ── duplicate check ───────────────────────────────────────────
            file_hash = get_file_hash(src_path)
            if file_hash in seen_hashes:
                dup_dest = output_dir / "_Duplicates" / src_path.name
                stats["skipped_dup"] += 1
                print(f"  [DUP]  {src_path.name} → _Duplicates/")
                if not dry_run:
                    dup_dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(str(src_path), safe_filename(dup_dest.parent, src_path.name))
                continue
            seen_hashes[file_hash] = dest_dir

            # ── destination path ──────────────────────────────────────────
            dest_path = safe_filename(dest_dir, src_path.name)
            rel_dest = dest_path.relative_to(output_dir)
            print(f"  [{'DRY' if dry_run else ('MOV' if move else 'CPY')}]  {src_path.name:40s} → {rel_dest}")

            if not dry_run:
                dest_dir.mkdir(parents=True, exist_ok=True)
                if move:
                    shutil.move(str(src_path), dest_path)
                else:
                    shutil.copy2(str(src_path), dest_path)

            stats["copied"] += 1

        except Exception as e:
            stats["errors"] += 1
            print(f"  [ERR]  {src_path.name} — {e}")

        # progress every 100 files
        if i % 100 == 0:
            print(f"\n  ... processed {i}/{len(files)} files ...\n")

    # ── summary ───────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  Done!")
    print(f"  {'Would process' if dry_run else 'Processed'} : {stats['copied']} files")
    print(f"  Duplicates   : {stats['skipped_dup']} files → _Duplicates/")
    print(f"  WhatsApp     : {stats['whatsapp']} files → WhatsApp/")
    print(f"  Errors       : {stats['errors']} files")
    print(f"{'='*60}")
    if dry_run:
        print("\n  ✅ Dry run complete. Run without --dry-run to actually copy files.")
    else:
        print(f"\n  ✅ All done! Check: {output_dir}")
    print()

# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Family Drive Organizer — sorts files by Year/Month/Category"
    )
    parser.add_argument(
        '--source', nargs='+', required=True,
        help='Source folder(s) to scan. Example: --source "D:\\Photos" or multiple: --source "D:\\Camera" "D:\\Downloads" "D:\\TRIPS"'
    )
    parser.add_argument(
        '--output', required=True,
        help='Output folder. Example: --output "E:\\Organized"'
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Preview what will happen without moving/copying anything'
    )
    parser.add_argument(
        '--move', action='store_true',
        help='Move files instead of copying (default is copy)'
    )
    args = parser.parse_args()
    organize(args.source, args.output, dry_run=args.dry_run, move=args.move)

if __name__ == '__main__':
    # ── Quick test: uncomment and edit paths, then just run the script ─────
    # organize(
    #     source_dirs=["D:\\Camera", "D:\\Downloads", "D:\\TRIPS"],  # edit these paths
    #     output_dir="D:\\Organized",                                 # edit output path
    #     dry_run=True,   # change to False when ready
    #     move=False      # change to True if you want to move instead of copy
    # )
    main()

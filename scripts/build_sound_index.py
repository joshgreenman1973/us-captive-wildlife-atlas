"""
Resolve sounds.json URLs to their direct Wikimedia upload paths and add an
MP3 transcode URL alongside the original. Browsers that don't play OGG
natively (most importantly Safari) get the MP3 fallback.

The Wikimedia hash path for File:Foo.ogg is derived from md5(Foo.ogg)[0]
and md5(Foo.ogg)[0:2]. Special characters in filenames are first replaced
with underscores (which is the Wikimedia rule).
"""
import hashlib
import json
import re
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SOUNDS = DATA / "sounds.json"


def commons_filename(url: str):
    """Given a Wikimedia URL, extract the filename used to compute hash path."""
    m = re.search(r"/Special:FilePath/(.+)$", url)
    if m:
        return urllib.parse.unquote(m.group(1)).replace(" ", "_")
    m = re.search(r"upload\.wikimedia\.org/wikipedia/commons/(?:thumb/)?[a-f0-9]/[a-f0-9]{2}/(.+?)(?:/[^/]+)?$", url)
    if m:
        return urllib.parse.unquote(m.group(1)).replace(" ", "_")
    return None


def hash_dirs(filename: str):
    """Return the (a, ab) directory parts for a Wikimedia commons file."""
    h = hashlib.md5(filename.encode("utf-8")).hexdigest()
    return h[0], h[:2]


def upload_urls(url: str):
    """Compute (canonical_upload, mp3_transcode) URLs for a sounds entry.
    Returns (canonical, mp3_or_None)."""
    fn = commons_filename(url)
    if not fn:
        return url, None
    a, ab = hash_dirs(fn)
    canonical = f"https://upload.wikimedia.org/wikipedia/commons/{a}/{ab}/{urllib.parse.quote(fn)}"
    # Transcode is supplied by Wikimedia for ogg/oga audio. Standard pattern:
    # /commons/transcoded/<a>/<ab>/<filename.ogg>/<filename.ogg.mp3>
    if fn.lower().endswith((".ogg", ".oga", ".webm")):
        mp3 = f"https://upload.wikimedia.org/wikipedia/commons/transcoded/{a}/{ab}/{urllib.parse.quote(fn)}/{urllib.parse.quote(fn)}.mp3"
        return canonical, mp3
    if fn.lower().endswith(".flac"):
        # Wikimedia transcodes flac to mp3 too
        mp3 = f"https://upload.wikimedia.org/wikipedia/commons/transcoded/{a}/{ab}/{urllib.parse.quote(fn)}/{urllib.parse.quote(fn)}.mp3"
        return canonical, mp3
    if fn.lower().endswith(".wav"):
        # WAV usually plays everywhere; no transcode needed
        return canonical, None
    return canonical, None


def main():
    data = json.loads(SOUNDS.read_text())
    updated = 0
    for k, v in data.items():
        if k.startswith("_") or not isinstance(v, dict) or not v.get("url"):
            continue
        canonical, mp3 = upload_urls(v["url"])
        v["url"] = canonical
        if mp3:
            v["url_mp3"] = mp3
            updated += 1
    SOUNDS.write_text(json.dumps(data, indent=1))
    print(f"Resolved {updated} entries with MP3 transcode fallback URLs.")


if __name__ == "__main__":
    main()

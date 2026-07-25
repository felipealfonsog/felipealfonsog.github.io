#!/usr/bin/env python3

import json
import os
import re
from pathlib import Path
from urllib.parse import urlsplit


CALLBACK_FILE = Path("spotify-callback.html")
CLIENT_ID = os.environ.get("SPOTIFY_PUBLIC_CLIENT_ID", "").strip()
REDIRECT_URI = os.environ.get("SPOTIFY_PUBLIC_REDIRECT_URI", "").strip()

CLIENT_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{16,128}$")
ASSIGNMENT_PATTERN = re.compile(
    r'const SPOTIFY_CLIENT_ID = ".*?"; '
    r"// managed-by-update-spotify-callback"
)
REDIRECT_ASSIGNMENT_PATTERN = re.compile(
    r'const SPOTIFY_REDIRECT_URI = ".*?"; '
    r"// managed-by-update-spotify-callback"
)


def main():
    if not CLIENT_ID:
        raise RuntimeError("The workflow input spotify_client_id is required.")
    if not REDIRECT_URI:
        raise RuntimeError(
            "The workflow input spotify_redirect_uri is required."
        )
    if not CLIENT_ID_PATTERN.fullmatch(CLIENT_ID):
        raise RuntimeError(
            "Invalid Spotify Client ID format. "
            "Expected 16-128 letters, numbers, underscores, or hyphens."
        )
    if not CALLBACK_FILE.is_file():
        raise RuntimeError(f"File not found: {CALLBACK_FILE}")

    parsed = urlsplit(REDIRECT_URI)
    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or parsed.query
        or parsed.fragment
    ):
        raise RuntimeError(
            "spotify_redirect_uri must be the exact HTTPS GitHub Pages URL "
            "without query parameters or fragments."
        )

    html = CALLBACK_FILE.read_text(encoding="utf-8")
    client_replacement = (
        f"const SPOTIFY_CLIENT_ID = {json.dumps(CLIENT_ID)}; "
        "// managed-by-update-spotify-callback"
    )
    updated, replacements = ASSIGNMENT_PATTERN.subn(
        client_replacement,
        html,
        count=1,
    )
    if replacements != 1:
        raise RuntimeError(
            "Managed SPOTIFY_CLIENT_ID assignment was not found exactly once."
        )

    redirect_replacement = (
        f"const SPOTIFY_REDIRECT_URI = {json.dumps(REDIRECT_URI)}; "
        "// managed-by-update-spotify-callback"
    )
    updated, redirect_replacements = REDIRECT_ASSIGNMENT_PATTERN.subn(
        redirect_replacement,
        updated,
        count=1,
    )
    if redirect_replacements != 1:
        raise RuntimeError(
            "Managed SPOTIFY_REDIRECT_URI assignment was not found exactly "
            "once."
        )

    if updated == html:
        print("Spotify callback Client ID and Redirect URI already configured.")
        return

    CALLBACK_FILE.write_text(updated, encoding="utf-8")
    print("Spotify callback Client ID and Redirect URI updated.")


if __name__ == "__main__":
    main()

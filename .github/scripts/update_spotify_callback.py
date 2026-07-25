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

CLIENT_ID_ASSIGNMENT = re.compile(
    r'const SPOTIFY_CLIENT_ID = ".*?"; '
    r"// managed-by-update-spotify-callback"
)

REDIRECT_URI_ASSIGNMENT = re.compile(
    r'const SPOTIFY_REDIRECT_URI = ".*?"; '
    r"// managed-by-update-spotify-callback"
)


def main():
    if not CLIENT_ID:
        raise RuntimeError("spotify_client_id is required.")

    if not CLIENT_ID_PATTERN.fullmatch(CLIENT_ID):
        raise RuntimeError("Invalid Spotify Client ID format.")

    if not REDIRECT_URI:
        raise RuntimeError("SPOTIFY_PUBLIC_REDIRECT_URI is required.")

    parsed = urlsplit(REDIRECT_URI)

    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or parsed.query
        or parsed.fragment
    ):
        raise RuntimeError("Invalid Spotify Redirect URI.")

    if not CALLBACK_FILE.is_file():
        raise RuntimeError(f"File not found: {CALLBACK_FILE}")

    html = CALLBACK_FILE.read_text(encoding="utf-8")

    client_assignment = (
        f"const SPOTIFY_CLIENT_ID = {json.dumps(CLIENT_ID)}; "
        "// managed-by-update-spotify-callback"
    )

    updated, client_count = CLIENT_ID_ASSIGNMENT.subn(
        client_assignment,
        html,
        count=1,
    )

    if client_count != 1:
        raise RuntimeError(
            "SPOTIFY_CLIENT_ID assignment was not found in spotify-callback.html."
        )

    redirect_assignment = (
        f"const SPOTIFY_REDIRECT_URI = {json.dumps(REDIRECT_URI)}; "
        "// managed-by-update-spotify-callback"
    )

    updated, redirect_count = REDIRECT_URI_ASSIGNMENT.subn(
        redirect_assignment,
        updated,
        count=1,
    )

    if redirect_count != 1:
        raise RuntimeError(
            "SPOTIFY_REDIRECT_URI assignment was not found in spotify-callback.html."
        )

    if updated == html:
        print("Spotify callback configuration already up to date.")
        return

    CALLBACK_FILE.write_text(updated, encoding="utf-8")
    print("Spotify Client ID and Redirect URI updated successfully.")


if __name__ == "__main__":
    main()

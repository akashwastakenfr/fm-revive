import urllib.request
import json

BASE = "http://127.0.0.1:8080"
TESTS = [
    ("GET", "/health"),
    ("GET", "/project"),
    ("GET", "/config/Android/18.1.03/config.ini?12345"),
    ("GET", "/config/Android/default/config.ini?12345"),
    ("GET", "/system/getServerTime"),
    ("POST", "/system/settings"),
    ("POST", "/system/loc/get-client-overrides"),
    ("POST", "/system/session/create"),
    ("POST", "/content/init"),
    ("GET", "/versionupdate/version"),
    ("POST", "/user/login"),
    ("POST", "/user/load"),
    ("GET", "/director/api/android/getDirectionByPackage"),
    ("POST", "/user/api/android/getDeviceID"),
    ("POST", "/user/api/android/getAnonUid"),
    ("GET", "/user/isVeteran"),
    ("GET", "/user/lineup/?type=0"),
    ("GET", "/unlockkey/getallkeys"),
    ("GET", "/stats/get"),
    ("GET", "/loginvideo/getCurrentVideo"),
    ("GET", "/loginbonus/status"),
    ("GET", "/assets/manifest.db"),
]

SQLITE_HEADER = b"SQLite format 3\x00"

ok = 0
for method, path in TESTS:
    req = urllib.request.Request(BASE + path, method=method, data=(b"{}" if method == "POST" else None))
    with urllib.request.urlopen(req, timeout=5) as resp:
        raw = resp.read()
        assert resp.status == 200, f"{method} {path} -> {resp.status}"
        if resp.headers.get("Content-Type", "").startswith("application/x.binary"):
            assert raw.startswith(SQLITE_HEADER), f"{method} {path} -> not a SQLite database"
        else:
            raw.decode("utf-8")
        ok += 1
        print(f"[PASS] {method:4s} {path} ({resp.status})")
print(f"All {ok}/{len(TESTS)} local server tests passed.")

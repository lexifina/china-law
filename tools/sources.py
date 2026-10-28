"""Official sources for the China build: 中国人大网 (www.npc.gov.cn), section 宪法、基本法和相关法律 > 宪法.

flk.npc.gov.cn is not used: its robots.txt disallows every crawler and forbids automated collection.
"""
import gzip
import hashlib
import http.client
import json
import os
import time

HOST = "www.npc.gov.cn"
BASE = "/npc/c34354/xgjbfwyh/xgjbfwyh002/xgjbfwyh003/"
UA = "Mozilla/5.0 (compatible; lexifina-law-history/1.0; +https://lexifina.com)"
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")

# key -> path under BASE. Titles as the listing page gives them.
PAGES = {
    "index": "index.html",
    "1982": "202410/t20241028_440219.html",       # 中华人民共和国宪法（1982年）
    "a1988": "202410/t20241017_440090.html",      # 中华人民共和国宪法修正案（1988年）
    "a1993": "202410/t20241017_440089.html",      # 中华人民共和国宪法修正案（1993年）
    "a1999": "202410/t20241017_440088.html",      # 中华人民共和国宪法修正案（1999年）
    "a2004": "202410/t20241017_440087.html",      # 中华人民共和国宪法修正案（2004年）
    "a2018": "202410/t20241028_440233.html",      # 中华人民共和国宪法修正案（2018年）
    "2018": "202409/t20240905_439070.html",       # 中华人民共和国宪法（2018年3月11日修正）
}


def url(key):
    return "http://" + HOST + BASE + PAGES[key]


def _cache_path(path):
    return os.path.join(CACHE, hashlib.sha256(path.encode()).hexdigest()[:24] + ".gz")


_conn = None
REQUESTS = 0


def _get(path):
    global _conn, REQUESTS
    for attempt in range(4):
        try:
            if _conn is None:
                _conn = http.client.HTTPConnection(HOST, timeout=60)
            _conn.request("GET", path, headers={"User-Agent": UA, "Accept-Encoding": "gzip",
                                                "Connection": "keep-alive"})
            r = _conn.getresponse()
            body = r.read()
            REQUESTS += 1
            if r.getheader("Content-Encoding") == "gzip":
                body = gzip.decompress(body)
            return r.status, body
        except (OSError, http.client.HTTPException):
            _conn = None
            time.sleep(2 * (attempt + 1))
    raise RuntimeError("fetch failed: " + path)


def fetch(key, offline=False):
    """Return (status, bytes) for a page, from the cache when present (negative answers cached too)."""
    path = BASE + PAGES[key]
    cp = _cache_path(path)
    if os.path.exists(cp):
        with gzip.open(cp, "rb") as f:
            rec = json.loads(f.readline())
            return rec["status"], f.read()
    if offline:
        raise RuntimeError("not cached (offline): " + path)
    status, body = _get(path)
    os.makedirs(CACHE, exist_ok=True)
    with gzip.open(cp + ".tmp", "wb") as f:
        f.write((json.dumps({"status": status, "path": path,
                             "retrieved": time.strftime("%Y-%m-%d")}) + "\n").encode())
        f.write(body)
    os.replace(cp + ".tmp", cp)
    return status, body


def retrieved(key):
    with gzip.open(_cache_path(BASE + PAGES[key]), "rb") as f:
        return json.loads(f.readline())["retrieved"]


if __name__ == "__main__":
    for k in PAGES:
        s, b = fetch(k)
        print(k, s, len(b), hashlib.sha256(b).hexdigest()[:12])
    print("requests", REQUESTS)

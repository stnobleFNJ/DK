"""중8-3 「생활 뉴스: 참지 마세요」 — 온라인 프로토타입 HTML에 base64로 들어 있는 그림을 JPEG 파일로 꺼낸다.
사용: python tools/gen_m8_3.py   → src/games/m8-3/img/anchor.jpg, s1-pain.jpg, s2-collapse.jpg, s3-hospital.jpg

원본: data/_1102/중기 온라인 프로토타입/m-p79.html (calm-salmiakki-4d2a53.netlify.app, 교재 PDF 79쪽 QR '뉴스속보')
프로토타입 안의 data:image/jpeg 9개는 같은 그림이 겹쳐 있어 서로 다른 그림은 4장이다.
<img alt="…">로 어떤 그림인지 찾아 이름을 붙인다(배경 흐림용 background-image는 같은 그림이라 건너뛴다).
원본 그림이므로 「임시생성」 도장은 찍지 않는다. 다시 실행해도 같은 파일이 나온다.
"""
import base64
import io
import re
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'data' / '_1102' / '중기 온라인 프로토타입' / 'm-p79.html'
OUT = ROOT / 'src' / 'games' / 'm8-3' / 'img'
MAX = 1200

# <img alt> 앞부분 → 저장 이름
NAMES = [
    ('뉴스를 전하는 아나운서', 'anchor.jpg'),
    ('가슴을 잡고 아파하는 남자', 's1-pain.jpg'),
    ('산책길에서 무릎을 짚고', 's2-collapse.jpg'),
    ('병원 침대에 누워', 's3-hospital.jpg'),
]


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    html = SRC.read_text(encoding='utf-8')
    OUT.mkdir(parents=True, exist_ok=True)
    found = {}
    for m in re.finditer(r'<img src="data:image/(?:jpeg|png);base64,([A-Za-z0-9+/=]+)" alt="([^"]*)"', html):
        data, alt = m.group(1), m.group(2)
        for key, name in NAMES:
            if alt.startswith(key) and name not in found:
                found[name] = data
    missing = [n for _, n in NAMES if n not in found]
    if missing:
        raise SystemExit(f'프로토타입에서 그림을 찾지 못함: {missing}')
    for _, name in NAMES:
        im = Image.open(io.BytesIO(base64.b64decode(found[name]))).convert('RGB')
        if max(im.size) > MAX:
            im.thumbnail((MAX, MAX), Image.LANCZOS)
        out = OUT / name
        im.save(out, 'JPEG', quality=84, optimize=True)
        print(f'{out.relative_to(ROOT)}\t{im.size[0]}x{im.size[1]}\t{out.stat().st_size // 1024}KB')


if __name__ == '__main__':
    main()

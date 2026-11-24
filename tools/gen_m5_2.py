"""중5-2 「나의 권리 말판 게임」 — 11/14 새 그림(나관엽)을 게임용 JPEG로 만든다.
사용: python tools/gen_m5_2.py   → src/games/m5-2/img/q02-scene.jpg … q12-bad.jpg, qNN-thumb.jpg (44장)

원본: data/큐알활동/중기 - 게임 참고자료 나관엽 (11.14)/중기 - 게임 참고자료 나관엽 (11.14)/5-2/
  - 'N-<상황>.png'   → qNN-scene.jpg(1200×900), 말판 칸 그림 qNN-thumb.jpg(240×180)
  - 'N-O <말>.png'   → qNN-good.jpg  (○ 내 권리를 표현해요)
  - 'N-X <말>.png'   → qNN-bad.jpg   (△ 표현하지 못하고 참아요)
원본은 모두 1448×1086(4:3) PNG 그림이고 말풍선 글자가 그림 안에 있다. 도장은 찍지 않는다.
(이전 10/26 그림은 ⭕/❌ 두 장이 붙은 그림이라 gen_m5_1.build 로 잘랐다.)
"""
import re
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'data' / '큐알활동' / '중기 - 게임 참고자료 나관엽 (11.14)' / '중기 - 게임 참고자료 나관엽 (11.14)' / '5-2'
OUT = ROOT / 'src' / 'games' / 'm5-2' / 'img'


def save(im, out, size, q=82):
    im.convert('RGB').resize(size, Image.LANCZOS).save(out, 'JPEG', quality=q, optimize=True, progressive=True)


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    found = {}
    for p in SRC.glob('*.png'):
        m = re.match(r'^(\d+)-\s*([OX])?', p.stem)
        n, kind = int(m.group(1)), m.group(2) or 'S'
        assert (n, kind) not in found, p
        found[n, kind] = p
    for n in range(2, 13):
        N = f'{n:02d}'
        for kind, name in (('S', 'scene'), ('O', 'good'), ('X', 'bad')):
            im = Image.open(found[n, kind])
            save(im, OUT / f'q{N}-{name}.jpg', (1200, 900))
            if kind == 'S':
                save(im, OUT / f'q{N}-thumb.jpg', (240, 180), 80)
        print(N, found[n, 'S'].stem, '|', found[n, 'O'].stem, '|', found[n, 'X'].stem)


if __name__ == '__main__':
    main()

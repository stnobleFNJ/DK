"""중7-4 「이건 학대일까요?」 — 상황 그림 12장을 게임용 JPEG로 줄인다.
사용: python tools/gen_m7_4.py   → src/games/m7-4/img/q01.jpg … q12.jpg

원본: data/나관엽*/나관엽*/중7-4 활용 그림/<번호>. <제목>.png (1448×1086)
파일 앞 번호가 프로토타입 문항 id(1~12)와 같다. 이름 끝이 '(학대 아님)'인 그림(4·8·12번)은 X가 정답이다.
모두 진짜 그림이라 도장을 찍지 않는다. 다시 실행해도 결과가 같다.
"""
import re
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = next((ROOT / 'data').glob('나관엽*/나관엽*/중7-4 활용 그림'))
OUT = ROOT / 'src' / 'games' / 'm7-4' / 'img'


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True, exist_ok=True)
    files = {int(re.match(r'(\d+)\.', p.name).group(1)): p for p in SRC.glob('*.png')}
    assert sorted(files) == list(range(1, 13)), sorted(files)
    for n, p in sorted(files.items()):
        im = Image.open(p).convert('RGB')
        im.thumbnail((1200, 1200), Image.LANCZOS)
        out = OUT / f'q{n:02d}.jpg'
        im.save(out, 'JPEG', quality=83, optimize=True, progressive=True)
        x = 'X' if '학대 아님' in p.stem else 'O'
        print(f'{out.name}\t{x}\t{im.size}\t{out.stat().st_size // 1024}KB\t← {p.name}')


if __name__ == '__main__':
    main()

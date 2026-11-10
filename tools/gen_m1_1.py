"""중1-1 「나의 생활, 나의 선택」(내가 선택한 것 찾기) — 주제별 사진 8장 × 3을 줄여 저장한다.
사용: python tools/gen_m1_1.py   → src/games/m1-1/img/<주제>-<원본 영어 이름>.jpg (24장)

원본: data/_1102/중기QR활동사진_김익수/중기QR_김익수(수정)/중1_1내가 선택한 것 찾기/<주제 폴더>/NN-<영어>.png (1254×1254)
주제 폴더 → 저장 접두어: 새집 물건 → home, 건강활동 → health, 필요한 도움 → help
모두 실제 사진이므로 임시 그림·도장은 없다. 자르지 않고 긴 변 800px로만 줄인다(2열 격자용).
다시 실행해도 같은 결과가 나온다.
"""
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'data' / '_1102' / '중기QR활동사진_김익수' / '중기QR_김익수(수정)' / '중1_1내가 선택한 것 찾기'
OUT = ROOT / 'src' / 'games' / 'm1-1' / 'img'
LONG = 800
QUALITY = 83
TOPICS = {'새집 물건': 'home', '건강활동': 'health', '필요한 도움': 'help'}


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True, exist_ok=True)
    n = 0
    for folder, key in TOPICS.items():
        files = sorted((SRC / folder).glob('*.png'))
        if len(files) != 8:
            raise SystemExit(f'{folder}: 사진이 8장이 아님 → {len(files)}')
        for f in files:
            name = f.stem.split('-', 1)[1]          # 01-table → table
            im = Image.open(f).convert('RGB')
            s = LONG / max(im.size)
            if s < 1:
                im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
            out = OUT / f'{key}-{name}.jpg'
            im.save(out, 'JPEG', quality=QUALITY, optimize=True, progressive=True)
            n += 1
            print(f'{out.relative_to(ROOT)}\t{im.size[0]}×{im.size[1]}\t{out.stat().st_size // 1024}KB\t← {folder}/{f.name}')
    print(n, '장')


if __name__ == '__main__':
    main()

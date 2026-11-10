"""중3-3 「나의 스트레스 해소법 월드컵」 — 스트레스 해소 활동 사진 16장을 줄여 저장한다.
사용: python tools/gen_m3_3.py   → src/games/m3-3/img/<원본 영어 이름>.jpg (16장, 예: pet-care.jpg)

원본: data/_1102/중기QR활동사진_김익수/중기QR_김익수(수정)/중3_3스트레스 월드컵/NN-<영어>.png (1254×1254)
모두 실제 사진이므로 임시 그림·도장은 없다. 자르지 않고 긴 변 1200px로만 줄인다.
다시 실행해도 같은 결과가 나온다.
"""
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'data' / '_1102' / '중기QR활동사진_김익수' / '중기QR_김익수(수정)' / '중3_3스트레스 월드컵'
OUT = ROOT / 'src' / 'games' / 'm3-3' / 'img'
LONG = 1200
QUALITY = 83


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True, exist_ok=True)
    files = sorted(SRC.glob('*.png'))
    if len(files) != 16:
        raise SystemExit(f'사진이 16장이 아님 → {len(files)}')
    for f in files:
        name = f.stem.split('-', 1)[1]              # 01-pet-care → pet-care
        im = Image.open(f).convert('RGB')
        s = LONG / max(im.size)
        if s < 1:
            im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        out = OUT / f'{name}.jpg'
        im.save(out, 'JPEG', quality=QUALITY, optimize=True, progressive=True)
        print(f'{out.relative_to(ROOT)}\t{im.size[0]}×{im.size[1]}\t{out.stat().st_size // 1024}KB\t← {f.name}')
    print(len(files), '장')


if __name__ == '__main__':
    main()

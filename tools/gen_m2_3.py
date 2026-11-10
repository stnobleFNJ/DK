"""중2-3 「약을 먹었는데 몸이 이상해요」 — 이상 증상 사진 8장을 게임용 JPEG로 줄인다.
사용: python tools/gen_m2_3.py   → src/games/m2-3/img/s-*.jpg (8장)

원본: data/_1102/중기QR활동사진_김익수/중기QR_김익수(수정)/중2_3이상증상/<증상>.jpg (1254×1254)
모두 진짜 사진이라 도장을 찍지 않는다. 다시 실행해도 결과가 같다.
"""
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = next((ROOT / 'data' / '_1102').glob('중기QR활동사진*/중기QR*/중2_3*'))
OUT = ROOT / 'src' / 'games' / 'm2-3' / 'img'

# 원본 파일 이름(확장자 뺌) → 게임 파일 이름
NAMES = {
    '어지러움': 's-dizzy.jpg',
    '설사': 's-diarrhea.jpg',
    '식은땀': 's-sweat.jpg',
    '속 울렁거림': 's-nausea.jpg',
    '붉음점': 's-rash.jpg',
    '부종(다리붓기)': 's-swelling.jpg',
    '고열': 's-fever.jpg',
    '손발 떨림': 's-tremor.jpg',
}


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True, exist_ok=True)
    files = {p.stem: p for p in SRC.glob('*.jpg')}
    assert set(files) == set(NAMES), sorted(files)
    for stem, name in NAMES.items():
        im = Image.open(files[stem]).convert('RGB')
        im.thumbnail((900, 900), Image.LANCZOS)
        out = OUT / name
        im.save(out, 'JPEG', quality=83, optimize=True, progressive=True)
        print(f'{name}\t{im.size}\t{out.stat().st_size // 1024}KB\t← {files[stem].name}')


if __name__ == '__main__':
    main()

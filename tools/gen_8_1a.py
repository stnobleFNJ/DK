"""전8-1 「상황에 맞는 기관 선택하기」 — 시우 상황 그림 5장을 게임용 JPEG로 줄인다.
사용: python tools/gen_8_1a.py   → src/games/8-1a/img/<id>.jpg

원본: data/_1102/게임(전기2,8단원)/게임/8-1 기관 이용 준비하기/공공기관 알아보기/*.png (1920×1080)
원본 양옆은 흐리게 늘인 여백이라 가운데 4:3(1440×1080)만 잘라 1200×900으로 줄인다.
기관 건물 그림은 자료에 없어 게임에서 이모지 타일로 대신한다(임시 그림 없음).
모두 진짜 그림이라 도장을 찍지 않는다. 다시 실행해도 결과가 같다.
"""
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = next((ROOT / 'data' / '_1102').glob('게임(전기2*/게임/8-1*/공공기관*'))
OUT = ROOT / 'src' / 'games' / '8-1a' / 'img'

ITEMS = [('stomach', '갑자기 배가'), ('transfer', '계좌이체'), ('book', '과제용 책'),
         ('idcard', '영화관에서'), ('parcel', '택배를')]


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True, exist_ok=True)
    for key, prefix in ITEMS:
        src = next(SRC.glob(prefix + '*.png'))
        im = Image.open(src).convert('RGB')
        W, H = im.size
        w = H * 4 // 3
        im = im.crop(((W - w) // 2, 0, (W - w) // 2 + w, H)).resize((1200, 900), Image.LANCZOS)
        out = OUT / f'{key}.jpg'
        im.save(out, 'JPEG', quality=83, optimize=True, progressive=True)
        print(f'{out.name}\t{out.stat().st_size // 1024}KB\t← {src.name}')


if __name__ == '__main__':
    main()

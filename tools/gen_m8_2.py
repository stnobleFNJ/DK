"""중8-2 「나의 건강계산기」 — 체질량지수 4단계 그림 4장을 게임용 JPEG로 바꾼다.
사용: python tools/gen_m8_2.py   → src/games/m8-2/img/bmi-1.jpg … bmi-4.jpg

원본: data/_1102/중기QR활동사진_김익수/중기QR_김익수(수정)/중8_2체질량지수/0N-*.png (1254×1254, 투명 없음)
1 저체중 · 2 적정 체중 · 3 과체중 · 4 비만. 그림 아래에 단계 이름이 이미 적혀 있다.
모두 진짜 그림이라 도장을 찍지 않는다. 다시 실행해도 결과가 같다.
"""
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = next((ROOT / 'data' / '_1102').glob('중기QR활동사진*/중기QR*/중8_2*'))
OUT = ROOT / 'src' / 'games' / 'm8-2' / 'img'
NAMES = ['01-low-weight', '02-healthy-range', '03-overweight', '04-obesity']


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True, exist_ok=True)
    for n, stem in enumerate(NAMES, 1):
        src = SRC / f'{stem}.png'
        im = Image.open(src).convert('RGB')
        im.thumbnail((900, 900), Image.LANCZOS)
        out = OUT / f'bmi-{n}.jpg'
        im.save(out, 'JPEG', quality=83, optimize=True, progressive=True)
        print(f'{out.name}\t{im.size}\t{out.stat().st_size // 1024}KB\t← {src.name}')


if __name__ == '__main__':
    main()

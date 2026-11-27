"""중3-3 「나만의 건강검진 순서」 — 게임 그림을 만든다.
사용: python tools/gen_m_check.py   → src/games/m-check/img/*.jpg

원본: data/건강검진게임_삽입이미지/
  개별이미지/01~22_*.png  검사 단계 사진(웹앱 「나만의 건강검진 순서」에 들어간 그림) → 이름 그대로 번호.jpg
  원본/workbook-38.png     교재 38쪽 → 처음 화면의 질문 사진 3장(q1~q3)
개별 사진은 폭 75~300px로 작아서 화면에서 흐리지 않게 3배로 키운다(원본이 오면 다시 실행).
"""
import sys
from pathlib import Path
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'data' / '건강검진게임_삽입이미지'
OUT = ROOT / 'src' / 'games' / 'm-check' / 'img'
Q = {'q1': (66, 306, 305, 449), 'q2': (340, 306, 579, 449), 'q3': (615, 306, 854, 449)}   # 38쪽 질문 카드 사진 칸


def save(im, name, k):
    im = im.convert('RGB')
    if k > 1:
        im = im.resize((im.width * k, im.height * k), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 50, 2))
    im.save(OUT / f'{name}.jpg', 'JPEG', quality=88, optimize=True)
    print(name, im.size)


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True, exist_ok=True)
    for f in sorted((SRC / '개별이미지').glob('*.png')):
        save(Image.open(f), f.name[:2], 3)
    page = Image.open(SRC / '원본' / 'workbook-38.png')
    for name, box in Q.items():
        save(page.crop(box), name, 2)


if __name__ == '__main__':
    main()

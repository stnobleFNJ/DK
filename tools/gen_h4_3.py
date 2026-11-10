"""후4-3 「휴대전화로 119 신고하기」 — 증상 사진 3장을 줄여 저장한다.
사용: python tools/gen_h4_3.py   → src/games/h4-3/img/face.jpg, arm.jpg, chest.jpg

원본: data/_1102/후기 게임자료/게임개발/후 4-3/*.png (1254×1254). 진짜 사진이므로 도장을 찍지 않는다.
"""
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'data' / '_1102' / '후기 게임자료' / '게임개발' / '후 4-3'
OUT = ROOT / 'src' / 'games' / 'h4-3' / 'img'
FILES = [('face.jpg', '얼굴이 비뚤어짐.png'), ('arm.jpg', '한쪽 팔에 힘이 빠짐.png'), ('chest.jpg', '가슴 통증.png')]


def save(src, out, side=1000):
    im = Image.open(src).convert('RGB')
    im.thumbnail((side, side), Image.LANCZOS)
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, 'JPEG', quality=83, optimize=True, progressive=True)


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    for out, src in FILES:
        save(SRC / src, OUT / out)
        print(out, '<-', src)


if __name__ == '__main__':
    main()

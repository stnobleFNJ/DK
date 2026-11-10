"""후5-2 「나의 추억 카드 만들기」 — 어디·무엇·누구와 그림 15장을 줄여 저장한다.
사용: python tools/gen_h5_2.py   → src/games/h5-2/img/where-*.jpg, what-*.jpg, who-*.jpg

원본 폴더 이름은 「후 5-3」이지만 요청서는 후5-2이므로 게임 폴더는 h5-2로 한다.
원본: data/_1102/후기 게임자료/게임개발/후 5-3/{어디,무엇,누구와}/*.png (1254×1254). 진짜 그림이므로 도장을 찍지 않는다.
"""
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'data' / '_1102' / '후기 게임자료' / '게임개발' / '후 5-3'
OUT = ROOT / 'src' / 'games' / 'h5-2' / 'img'
FILES = [
    ('where-home.jpg', '어디/집에서.png'), ('where-mall.jpg', '어디/쇼핑몰에서.png'), ('where-park.jpg', '어디/공원에서.png'),
    ('where-cafe.jpg', '어디/식당,카페에서.png'), ('where-trip.jpg', '어디/여행지에서.png'),
    ('what-shop.jpg', '무엇/쇼핑했어요.png'), ('what-eat.jpg', '무엇/맛있는 것을 먹었어요.png'), ('what-walk.jpg', '무엇/산책했어요.png'),
    ('what-xmas.jpg', '무엇/크리스마스마켓을 구경했어요.png'), ('what-photo.jpg', '무엇/사진을 찍었어요.png'),
    ('who-alone.jpg', '누구와/혼자.png'), ('who-family.jpg', '누구와/가족과.png'), ('who-friend.jpg', '누구와/친구와.png'),
    ('who-teacher.jpg', '누구와/선생님과.png'), ('who-close.jpg', '누구와/친한 사람들과.png'),
]


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True, exist_ok=True)
    for out, src in FILES:
        im = Image.open(SRC / src).convert('RGB')
        im.thumbnail((900, 900), Image.LANCZOS)
        im.save(OUT / out, 'JPEG', quality=83, optimize=True, progressive=True)
        print(out, '<-', src)


if __name__ == '__main__':
    main()

"""전7-3 「혼자 이동하기」 보드판의 START·GOAL 글자를 '시작'·'도착'으로 바꾼다.
사용: python tools/gen_7_3.py   → optimize_images.py 7-3 실행 후 src/games/7-3/img/board.jpg 수정

11/09 수정의견(박신하): "Start, GOAL 모두 시작과 도착으로 수정해 주세요."
원본 로드맵 그림에 글자가 들어 있어서, 남색 이름표를 같은 모양으로 다시 칠하고 한글을 쓴다.
원본 그림 자체를 바꾼 것이 아니라 이름표만 덮었으므로 도장은 찍지 않는다.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import optimize_images  # noqa: E402

BOARD = ROOT / 'src' / 'games' / '7-3' / 'img' / 'board.jpg'
NAVY = (1, 38, 77)
FONT = 'C:/Windows/Fonts/malgunbd.ttf'
# 1600×900 보드판 기준 이름표 위치(남색 알약 모양)
TAGS = [((90, 55, 299, 109), '시작'), ((90, 472, 299, 526), '도착')]


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    optimize_images.main(['7-3'])
    im = Image.open(BOARD).convert('RGB')
    assert im.size == (1600, 900), im.size
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, 36)
    for (x0, y0, x1, y1), text in TAGS:
        d.rounded_rectangle((x0, y0, x1, y1), radius=(y1 - y0) // 2, fill=NAVY)
        l, t, r, b = d.textbbox((0, 0), text, font=f)
        d.text(((x0 + x1 - (r - l)) / 2 - l, (y0 + y1 - (b - t)) / 2 - t), text, font=f, fill='white')
    im.save(BOARD, 'JPEG', quality=82, optimize=True, progressive=True)
    print(f'{BOARD.relative_to(ROOT)}: START→시작, GOAL→도착')


if __name__ == '__main__':
    main()

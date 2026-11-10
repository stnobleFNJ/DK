"""전8-3 「회원가입 연습하기」 — 달마당 도서관 '달님 사서' 그림을 잘라 낸다.
사용: python tools/gen_8_3.py   → src/games/8-3/img/moon.jpg

원본: data/_1102/게임(전기2,8단원)/게임/8-3 신청서 작성하기/회원가입 작성화면.png (1920×1080 화면 캡처)
가입 폼과 완료 화면은 그림을 보고 HTML로 다시 만들었으므로, 그림에서는 달님 사서 캐릭터만 쓴다.
배경색은 말풍선 상자 색(237,253,243)이라 게임의 .lib-guide 배경(#edfdf3)과 맞춘다. 실제 그림이므로 도장 없음.
"""
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = next((ROOT / 'data' / '_1102' / '게임(전기2,8단원)' / '게임').glob('8-3*/회원가입 작성화면.png'))
OUT = ROOT / 'src' / 'games' / '8-3' / 'img'
BOX = (538, 106, 638, 214)   # 달님 사서 캐릭터(원본 좌표)


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True, exist_ok=True)
    im = Image.open(SRC).convert('RGB').crop(BOX)
    im = im.resize((im.width * 2, im.height * 2), Image.LANCZOS)
    out = OUT / 'moon.jpg'
    im.save(out, 'JPEG', quality=88, optimize=True)
    print(out.relative_to(ROOT), im.size)


if __name__ == '__main__':
    main()

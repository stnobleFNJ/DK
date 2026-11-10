"""전5-2 「우리집 한바퀴」 — 바른 행동 사진 5장과 칸 공간 사진 4장을 만든다.
사용: python tools/gen_5_2.py   → src/games/5-2/img/q*-good.jpg, sp-*.jpg

거실·주방·화장실 칸(1·3·4·6·8)의 '알맞은 행동' 사진은 11/09 추가 사진(data/_1109/5-2)을 쓴다.
(전에는 임시생성 그림이었다.) 나머지 보드판·상황 사진은 optimize_images.py 5-2 로 만든다.
sp-*.jpg(칸 공간 사진)는 실제 보드판에서 잘라 낸 것이다.
"""
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'src' / 'games' / '5-2' / 'img'
BOARD = ROOT / 'data' / '큐알활동사진_생애주기_전기_1,5,6,7단원' / '5-2 우리집공간사용법' / '1. 우리집 한바퀴 생활공간 보드.png'
NEW = ROOT / 'data' / '_1109' / '5-2'

# 칸 번호 → 저장 이름 (원본: 'N) …바른행동(추가).png')
GOOD = {'2-1': 'q1-good.jpg', '2-3': 'q3-good.jpg', '2-4': 'q4-good.jpg', '2-6': 'q6-good.jpg', '2-8': 'q8-good.jpg'}

# 보드판(1672×941)에서 칸 그림 부분을 잘라 문제 화면 머리 사진으로 쓴다(실제 사진, 도장 없음)
CROPS = [('sp-living.jpg', (362, 238, 646, 462)), ('sp-room.jpg', (702, 238, 980, 462)),
         ('sp-kitchen.jpg', (1033, 238, 1317, 462)), ('sp-bath.jpg', (363, 648, 647, 874))]


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True, exist_ok=True)
    board = Image.open(BOARD).convert('RGB')
    for name, box in CROPS:
        board.crop(box).save(OUT / name, 'JPEG', quality=84, optimize=True)
        print(f'{name}	(보드판 자르기)')
    for no, name in GOOD.items():
        src = next(p for p in NEW.glob(f'{no})*바른행동*.png'))
        im = Image.open(src).convert('RGB')
        if im.width > 1600:
            im = im.resize((1600, round(im.height * 1600 / im.width)), Image.LANCZOS)
        im.save(OUT / name, 'JPEG', quality=82, optimize=True, progressive=True)
        print(f'{name}	{im.width}x{im.height}	{(OUT / name).stat().st_size // 1024}KB	← {src.name}')
    mf = ROOT / 'tools' / 'placeholder_manifest' / '5-2.json'
    if mf.exists():
        mf.unlink()
        print(f'{mf.relative_to(ROOT)} 삭제(임시 그림 없음)')


if __name__ == '__main__':
    main()

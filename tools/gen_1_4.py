"""전1-4 내가 원하는 프로그램 고르기: 11/18 수정 의견(오승은)의 실사 사진 10장을 게임용으로 줄인다.

    python tools/gen_1_4.py

- img/p-<id>.jpg : 프로그램 카드에 마우스를 올리거나 누르면 보이는 활동 사진(1200×675)
- img/start.jpg  : 첫 화면 표지 — 사진 4장의 가운데(실제 사진 부분)를 나란히 붙인 그림(1200×675)

원본은 16:9 가운데에 세로 사진이 있고 양옆은 흐리게 채운 그림이다. 카드에서는 16:9 그대로 쓴다.
"""
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'data/큐알활동/게임(전기)1단원 수정의견261118/게임(전기)1단원 수정의견261118/전1-4 일주일 계획하기/실사이미지10종'
OUT = ROOT / 'src/games/1-4/img'

# 파일 번호 → 게임 속 프로그램 id
MAP = {'01': 'craft', '02': 'yoga', '03': 'pingpong', '04': 'cook', '05': 'drawing',
       '06': 'drone', '07': 'nanta', '08': 'movie', '09': 'camp', '10': 'computer'}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pics = {}
    for f in sorted(SRC.glob('*.png')):
        pid = MAP[f.name[:2]]
        im = ImageOps.fit(Image.open(f).convert('RGB'), (1200, 675), Image.LANCZOS)
        im.save(OUT / f'p-{pid}.jpg', quality=82, optimize=True, progressive=True)
        pics[pid] = im
        print('p-%s.jpg' % pid)
    sheet = Image.new('RGB', (1200, 675), (255, 255, 255))
    for i, pid in enumerate(['craft', 'cook', 'pingpong', 'camp']):
        src = pics[pid].crop((360, 0, 840, 675))          # 가운데 실제 사진 부분
        tile = ImageOps.fit(src, (296, 675), Image.LANCZOS)
        sheet.paste(tile, (i * 301, 0))
    sheet.save(OUT / 'start.jpg', quality=82, optimize=True, progressive=True)
    print('start.jpg')


if __name__ == '__main__':
    main()

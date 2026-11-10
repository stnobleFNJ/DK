"""전2-1 「소비기한 확인하기」 — 제품 그림 5장을 게임용 JPEG로 줄이고, 날짜 부분을 크게 잘라 둔다.
사용: python tools/gen_2_1.py   → src/games/2-1/img/<id>.jpg, <id>-date.jpg

원본: data/_1102/게임(전기2,8단원)/게임/2-1 똑똑하게 장보기/<제품> … 찾기.png (1672×941)
BOX는 원본 좌표로 잰 '날짜가 쓰인 곳'이다. 파이(가로로 긴 제품)를 빼고는 제품이 크게 보이도록
가운데 4:3(x 209~1464)만 잘라 1200×900으로 만든다. 파이는 16:9 그대로 1200×675. 게임의 누르는 영역(%)도 같은 값에서 나온다(실행하면 출력).
모두 진짜 그림이라 도장을 찍지 않는다. 다시 실행해도 결과가 같다.
"""
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = next((ROOT / 'data' / '_1102').glob('게임(전기2*/게임/2-1*'))
OUT = ROOT / 'src' / 'games' / '2-1' / 'img'

C43 = (209, 1464)
# (출력 id, 원본 파일 이름 앞부분, 날짜 영역 (x0, y0, x1, y1) 원본 픽셀, 가로 자르기 범위 또는 None)
ITEMS = [
    ('milk', '신선 우유', (607, 827, 980, 887), C43),
    ('sprout', '신선한 콩나물', (583, 687, 1091, 780), C43),
    ('pie', '아몬드 미니 파이', (1096, 316, 1503, 587), None),
    ('snack', '주황색 감자스낵', (567, 709, 1124, 773), C43),
    ('tofu', '찌개용 두부', (929, 540, 1407, 693), C43),
]


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True, exist_ok=True)
    for key, prefix, (x0, y0, x1, y1), cut in ITEMS:
        src = next(SRC.glob(prefix + '*.png'))
        im = Image.open(src).convert('RGB')
        W, H = im.size
        cx0, cx1 = cut or (0, W)
        main_im = im.crop((cx0, 0, cx1, H))
        main_im = main_im.resize((1200, round(1200 * H / (cx1 - cx0))), Image.LANCZOS)
        main_im.save(OUT / f'{key}.jpg', 'JPEG', quality=83, optimize=True, progressive=True)
        p = 10
        crop = im.crop((max(0, x0 - p), max(0, y0 - p), min(W, x1 + p), min(H, y1 + p)))
        crop.thumbnail((900, 900), Image.LANCZOS)
        crop.save(OUT / f'{key}-date.jpg', 'JPEG', quality=84, optimize=True)
        cw = cx1 - cx0
        pct = [round((x0 - cx0) / cw * 100, 1), round(y0 / H * 100, 1), round((x1 - x0) / cw * 100, 1), round((y1 - y0) / H * 100, 1)]
        print(f'{key}\tbox%={pct}\t{main_im.size}\t← {src.name}')


if __name__ == '__main__':
    main()

"""전8-1 「기관 이용 시 준비물 선택하기」 — 물건 그림 12장을 정사각 JPEG로 만든다.
사용: python tools/gen_8_1b.py   → src/games/8-1b/img/<id>.jpg (480×480)

원본: data/_1102/게임(전기2,8단원)/게임/8-1 기관 이용 준비하기/기관 방문 시 준비물 챙기기/<이름>.png (1920×1080, 일부 투명)
투명 배경은 흰색으로 채우고, 물건 둘레만 남겨 정사각으로 자른다(흰 타일 위에 놓이므로 PNG가 필요 없다).
모두 진짜 그림이라 도장을 찍지 않는다. 다시 실행해도 결과가 같다.
"""
import sys
from pathlib import Path
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent.parent
SRC = next((ROOT / 'data' / '_1102').glob('게임(전기2*/게임/8-1*/기관 방문*'))
OUT = ROOT / 'src' / 'games' / '8-1b' / 'img'

ITEMS = [('snack', '과자'), ('librarycard', '대출카드'), ('stamp', '도장'), ('money', '돈'),
         ('phone', '스마트폰'), ('slime', '슬라임'), ('idcard', '신분증'), ('dumbbell', '아령'),
         ('umbrella', '우산'), ('photo', '증명사진'), ('ball', '축구공'), ('toothbrush', '칫솔')]
S = 480


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True, exist_ok=True)
    for key, name in ITEMS:
        src = SRC / f'{name}.png'
        im = Image.open(src).convert('RGBA')
        bg = Image.new('RGBA', im.size, (255, 255, 255, 255))
        bg.alpha_composite(im)
        im = bg.convert('RGB')
        diff = ImageChops.difference(im, Image.new('RGB', im.size, 'white')).convert('L').point(lambda v: 255 if v > 18 else 0)
        x0, y0, x1, y1 = diff.getbbox()
        side = int(max(x1 - x0, y1 - y0) * 1.12)
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        # 원본 바깥으로 나가도 흰 바탕이 되도록 흰 캔버스에 붙인다
        box = (cx - side // 2, cy - side // 2)
        canvas = Image.new('RGB', (side, side), 'white')
        canvas.paste(im, (-box[0], -box[1]))
        canvas = canvas.resize((S, S), Image.LANCZOS)
        out = OUT / f'{key}.jpg'
        canvas.save(out, 'JPEG', quality=84, optimize=True)
        print(f'{out.name}\t{out.stat().st_size // 1024}KB\t← {src.name}')


if __name__ == '__main__':
    main()

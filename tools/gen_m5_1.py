"""중5-1 「예의 없는 행동 주사위 게임」 — 원본 그림을 잘라 게임용 JPEG로 만든다.
사용: python tools/gen_m5_1.py   → src/games/m5-1/img/q02-scene.jpg … q15-bad.jpg, qNN-thumb.jpg (56장)

원본: data/나관엽 - 게임 참고자료 (10.26)/…/중5-1 활용 그림/
  - 칸마다 상황 그림 1장(예: '4- 화가 나서 물건 던지기.png', 2번만 '2번 칸 …png')
    → qNN-scene.jpg (4:3, 1200×900), 말판 칸 그림 qNN-thumb.jpg (240×180)
  - 보기 그림 'N- ⭕ … ❌ ….png' 은 한 장에 두 그림이 붙어 있다.
    가운데 흰 줄을 찾아 자동으로 나눈다. 위·아래로 붙었으면 위가 ⭕, 왼쪽·오른쪽으로 붙었으면 왼쪽이 ⭕.
    → qNN-good.jpg(⭕), qNN-bad.jpg(❌)
  - 3번만 ⭕/❌ 가 따로 된 파일이라 그대로 줄여 쓴다.
모두 진짜 그림이므로 「임시생성」 도장을 찍지 않는다. 다시 실행해도 결과가 같다.
gen_m5_2.py 가 이 파일의 split_pair / save_jpg / build 를 함께 쓴다.
"""
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
REF = ROOT / 'data' / '나관엽 - 게임 참고자료 (10.26)' / '나관엽 - 게임 참고자료 (10.26)'
MAXSIDE = 1200
QUALITY = 83


def save_jpg(im, out):
    """긴 변을 MAXSIDE 이하로 줄여 JPEG로 저장한다."""
    im = im.convert('RGB')
    s = MAXSIDE / max(im.size)
    if s < 1:
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    im.save(out, 'JPEG', quality=QUALITY, optimize=True, progressive=True)
    return im.size


def _white_run(im, horizontal):
    """가운데 30~70% 구간에서 거의 흰 줄(행 또는 열)이 이어진 범위를 찾는다."""
    g = im.convert('L')
    w, h = g.size
    px = g.load()
    if horizontal:   # 흰 가로줄 → 위·아래로 나뉨
        cand = [y for y in range(int(h * .3), int(h * .7))
                if sum(px[x, y] > 230 for x in range(0, w, 6)) / len(range(0, w, 6)) > .95]
    else:            # 흰 세로줄 → 왼쪽·오른쪽으로 나뉨
        cand = [x for x in range(int(w * .3), int(w * .7))
                if sum(px[x, y] > 230 for y in range(0, h, 6)) / len(range(0, h, 6)) > .95]
    return (cand[0], cand[-1]) if cand else None


def split_pair(im):
    """붙은 그림을 (⭕, ❌, 방향) 으로 나눈다. 방향 'tb'=위아래, 'lr'=좌우."""
    w, h = im.size
    r = _white_run(im, True)
    if r:
        a, b = r
        return im.crop((0, 0, w, a - 2)), im.crop((0, b + 3, w, h)), 'tb'
    r = _white_run(im, False)
    if r:
        a, b = r
        return im.crop((0, 0, a - 2, h)), im.crop((b + 3, 0, w, h)), 'lr'
    raise ValueError('가운데 흰 줄을 찾지 못함')


def num(p):
    """'12- …png' / '2번 칸 …png' → 12 / 2"""
    s = p.name
    d = ''
    for c in s:
        if c.isdigit():
            d += c
        else:
            break
    return int(d)


def build(folder, out, nums):
    sys.stdout.reconfigure(encoding='utf-8')
    src = REF / folder
    out.mkdir(parents=True, exist_ok=True)
    files = sorted(src.glob('*.png'))
    layout = {}
    for n in nums:
        mine = [p for p in files if num(p) == n]
        pair = [p for p in mine if '⭕' in p.name and '❌' in p.name]
        good = [p for p in mine if '⭕' in p.name and '❌' not in p.name]
        bad = [p for p in mine if '❌' in p.name and '⭕' not in p.name]
        scene = [p for p in mine if '⭕' not in p.name and '❌' not in p.name]
        assert len(scene) == 1, (n, scene)
        sc = Image.open(scene[0])
        save_jpg(sc, out / f'q{n:02d}-scene.jpg')
        # 말판 칸에 넣을 작은 그림(240×180)
        sc.convert('RGB').resize((240, 180), Image.LANCZOS).save(
            out / f'q{n:02d}-thumb.jpg', 'JPEG', quality=80, optimize=True)
        if pair:
            g, b, d = split_pair(Image.open(pair[0]))
        else:
            assert len(good) == 1 and len(bad) == 1, (n, mine)
            g, b, d = Image.open(good[0]), Image.open(bad[0]), 'one'
        sg = save_jpg(g, out / f'q{n:02d}-good.jpg')
        sb = save_jpg(b, out / f'q{n:02d}-bad.jpg')
        layout[n] = d
        print(f'q{n:02d}\t{d}\tgood {sg[0]}×{sg[1]}\tbad {sb[0]}×{sb[1]}')
    total = sum(f.stat().st_size for f in out.glob('*.jpg')) // 1024
    print(f'{out.relative_to(ROOT)}  {len(list(out.glob("*.jpg")))}장  {total}KB')
    print('세로로 긴 보기(lr):', [n for n, d in layout.items() if d == 'lr'])
    return layout


if __name__ == '__main__':
    build('중5-1 활용 그림', ROOT / 'src' / 'games' / 'm5-1' / 'img', range(2, 16))

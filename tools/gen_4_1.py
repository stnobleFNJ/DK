"""전4-1 「나의 코디 꾸미기」 — 진짜 옷 사진 24장을 투명 PNG로 만든다.

원본: data/_1102/게임(전기3,4단원)/게임(전기3,4)/전4-1 깨끗한 하루 만들기/{남자|여자} 상의, 하의, 신발/
      {남자|여자} {상의|하의|신발}{1-4}[(얼룩)].png  (1672×941, 흰 배경 RGB와 투명 PNG가 섞여 있음)
결과: src/games/4-1/img/{m|f}-{top|bottom|shoes}-{1-4}.png

- 흰 배경 사진: 가장자리에서부터 flood-fill로 '거의 흰색'만 지운다(옷 안쪽의 흰색은 가장자리와
  이어져 있지 않으므로 남는다). 흰 셔츠·흰 운동화가 지워지지 않도록 기준을 높게(살짝 흐린 밝기 ≥250,
  채도 ≤8) 잡았다. 테두리는 1px 깎고 부드럽게 한다.
- 이미 투명한 PNG는 그대로 둔다.
- 여백을 잘라 낸다.
- 화면에서 보기 그림은 300px 안팎이라 긴 변 512px로 줄인다(최대 800px 안).
- 진짜 사진이므로 「임시생성」 도장은 찍지 않는다.

    python tools/gen_4_1.py

다시 실행해도 같은 결과가 나온다. 필요한 것: Pillow, numpy.
cutout()·trim()은 tools/gen_4_2.py도 가져다 쓴다.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'data' / '_1102' / '게임(전기3,4단원)' / '게임(전기3,4)' / '전4-1 깨끗한 하루 만들기'
OUT = ROOT / 'src' / 'games' / '4-1' / 'img'
MAX = 512
GEN = {'m': '남자', 'f': '여자'}
CAT = {'top': '상의', 'bottom': '하의', 'shoes': '신발'}


# ---------- 배경 지우기 (4-2도 사용) ----------
def _blur(x, r):
    return np.asarray(Image.fromarray(np.clip(x, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))).astype(np.float32)


def _grad(x):
    g = np.zeros_like(x)
    g[:, 1:-1] = np.abs(x[:, 2:] - x[:, :-2])
    g[1:-1, :] = np.maximum(g[1:-1, :], np.abs(x[2:, :] - x[:-2, :]))
    return g


def flood_from_border(passable):
    """passable(bool HxW) 중 그림 가장자리와 이어진 부분만 True로 돌려준다."""
    h, w = passable.shape
    m = Image.fromarray(np.where(passable, 255, 0).astype(np.uint8), 'L').copy()
    px = m.load()
    border = [(x, 0) for x in range(w)] + [(x, h - 1) for x in range(w)] + \
             [(0, y) for y in range(h)] + [(w - 1, y) for y in range(h)]
    for xy in border:
        if px[xy] == 255:
            ImageDraw.floodfill(m, xy, 128)
    return np.asarray(m) == 128


def cutout(im, hi=250, sat=8, shadow=False, lo=175, ssat=14, gthr=3.0, sgain=1.0, smax=.45, protect=False):
    """흰 배경을 가장자리부터 flood-fill로 지운 RGBA를 돌려준다. 이미 RGBA면 그대로.

    1단계: 살짝 흐린 밝기 ≥ hi, 채도 ≤ sat 인 픽셀을 가장자리부터 채워 배경으로 본다.
    shadow=True면 2단계: 밝기 ≥ lo, 채도 ≤ ssat, 밝기 변화가 작은(gthr 미만) 바닥 그림자/벽까지 넓혀서
      검은색 반투명 그림자(진하기 = 어두운 정도 × sgain, 최대 smax)로 바꾼다. sgain=0이면 완전히 지운다.
    protect=True면 진한 색 픽셀(나무 틀 등)의 볼록 껍질 안은 2단계에서 지우지 않는다(흰 이불 보호).
    """
    if im.mode == 'RGBA':
        return im.copy()
    rgb = np.asarray(im.convert('RGB')).astype(np.float32)
    lum = rgb.mean(2)
    s = rgb.max(2) - rgb.min(2)
    bl, bs = _blur(lum, 1.5), _blur(s, 1.5)
    p1 = (bl >= hi) & (bs <= sat)
    bg1 = flood_from_border(p1)
    alpha = np.where(bg1, 0.0, 255.0)
    out = rgb.copy()
    bg = bg1
    if shadow:
        p2 = p1 | ((bl >= lo) & (bs <= ssat) & (_grad(_blur(lum, 1.0)) < gthr))
        bg = flood_from_border(p2)
        if protect:
            bg &= ~_hull_mask((s > 40) | (lum < 150)) | bg1
        sh = bg & ~bg1
        alpha = np.where(sh, np.clip((252 - _blur(lum, 2.0)) / 252 * sgain, 0, smax) * 255, alpha)
        out[sh] = 0
    obj = ~bg
    edge = Image.fromarray(np.where(obj, 255, 0).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(.7))
    alpha = np.where(obj, np.asarray(edge).astype(np.float32), alpha)
    return Image.fromarray(np.dstack([out, alpha]).clip(0, 255).astype(np.uint8), 'RGBA')


def _hull_mask(m):
    """bool 마스크의 볼록 껍질을 채운 bool 마스크."""
    ys, xs = np.nonzero(m[::4, ::4])
    pts = sorted(set(zip((xs * 4).tolist(), (ys * 4).tolist())))
    if len(pts) < 3:
        return np.zeros_like(m)

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    img = Image.new('L', (m.shape[1], m.shape[0]), 0)
    ImageDraw.Draw(img).polygon(lower[:-1] + upper[:-1], fill=255)
    return np.asarray(img) > 0


def trim(im, maxside=MAX, pad=8, thr=24):
    """알파 > thr 인 부분만 남기고(여백 pad) 긴 변을 maxside 이하로 줄인다."""
    a = np.asarray(im)[..., 3]
    ys, xs = np.nonzero(a > thr)
    box = (max(int(xs.min()) - pad, 0), max(int(ys.min()) - pad, 0),
           min(int(xs.max()) + pad + 1, im.width), min(int(ys.max()) + pad + 1, im.height))
    im = im.crop(box)
    k = maxside / max(im.size)
    if k < 1:
        im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    return im


def save_png(im, dst):
    """RGBA PNG로 저장. 완전히 투명한 픽셀의 색은 0으로 지워서 용량을 줄인다.
    (256색 팔레트로 줄이면 그림자·검은 가구에 얼룩 무늬가 생겨서 쓰지 않는다.)"""
    a = np.asarray(im.convert('RGBA')).copy()
    a[a[..., 3] == 0] = 0
    Image.fromarray(a, 'RGBA').save(dst, optimize=True)


# ---------- 4-1 ----------
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True, exist_ok=True)
    n = 0
    for g, gk in GEN.items():
        folder = SRC / f'{gk} 상의, 하의, 신발'
        for c, ck in CAT.items():
            for i in range(1, 5):
                hits = sorted(folder.glob(f'{gk} {ck}{i}*.png'))
                if len(hits) != 1:
                    raise SystemExit(f'원본을 찾지 못함: {gk} {ck}{i} → {hits}')
                src = hits[0]
                im = trim(cutout(Image.open(src)))
                dst = OUT / f'{g}-{c}-{i}.png'
                save_png(im, dst)
                n += 1
                print(f'{dst.relative_to(ROOT)}\t{im.size[0]}×{im.size[1]}\t{dst.stat().st_size // 1024}KB\t← {src.name}')
    print(f'{n}장 완료')


if __name__ == '__main__':
    main()

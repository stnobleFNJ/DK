"""전4-1 「나의 코디 꾸미기」 임시 그림을 만든다 (종이 인형 방식).

모든 층(모델·상의·하의·신발)은 600×900 투명 PNG, 같은 기준점에 그려서
<img>를 겹치기만 하면 옷을 입은 모습이 된다. 쌓는 순서: 모델 → 하의 → 신발 → 상의.
2배 크기로 그린 뒤 줄여서 테두리를 부드럽게 했다.
도장은 모든 층의 같은 자리(오른쪽 위)에 같은 크기로 찍어서, 겹쳐도 도장 하나로 보인다.
작은 보기 그림(thumb-*.png, 320×320)도 따로 만든다.

    python tools/gen_4_1.py
"""
import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).parent))
from placeholder import stamp  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'src/games/4-1/img'
MAN = ROOT / 'tools/placeholder_manifest/4-1.json'
W, H, S = 600, 900, 2          # 최종 크기, 그리는 배율
CX = 300
STAMP = .75                    # 층 도장 크기(모든 층 같음)
TW = 320                       # 보기 그림 크기

SKIN = (243, 206, 178)
UNDER_T = (236, 230, 218)
UNDER_B = (168, 174, 182)
INK = (58, 46, 40)


def dark(c, k=.62):
    return tuple(round(v * k) for v in c[:3])


def light(c, k=.35):
    return tuple(round(v + (255 - v) * k) for v in c[:3])


# ---------- 2배 마스크 그리기 ----------
class Mask:
    def __init__(self):
        self.im = Image.new('L', (W * S, H * S), 0)
        self.d = ImageDraw.Draw(self.im)

    def _p(self, pts):
        return [(x * S, y * S) for x, y in pts]

    def poly(self, pts, v=255):
        self.d.polygon(self._p(pts), fill=v)
        return self

    def ell(self, cx, cy, rx, ry, v=255):
        self.d.ellipse((S * (cx - rx), S * (cy - ry), S * (cx + rx), S * (cy + ry)), fill=v)
        return self

    def rect(self, x0, y0, x1, y1, r=0, v=255):
        self.d.rounded_rectangle((S * x0, S * y0, S * x1, S * y1), r * S, fill=v)
        return self

    def limb(self, pts, ws, v=255):
        """굵기가 점점 바뀌는 팔다리 모양(관절마다 둥글게)."""
        for (a, wa), (b, wb) in zip(zip(pts, ws), zip(pts[1:], ws[1:])):
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy) or 1
            nx, ny = -dy / L, dx / L
            self.poly([(a[0] + nx * wa / 2, a[1] + ny * wa / 2), (b[0] + nx * wb / 2, b[1] + ny * wb / 2),
                       (b[0] - nx * wb / 2, b[1] - ny * wb / 2), (a[0] - nx * wa / 2, a[1] - ny * wa / 2)], v)
        for p, w in zip(pts, ws):
            self.ell(p[0], p[1], w / 2, w / 2, v)
        return self

    def cut(self, other):
        self.im = ImageChops.subtract(self.im, other.im)
        self.d = ImageDraw.Draw(self.im)
        return self


class Draw:
    """마스크 안에서만 그려지는 무늬용 그리기 (최종 좌표)."""
    def __init__(self, im):
        self.d = ImageDraw.Draw(im)

    def line(self, pts, fill, w=2):
        self.d.line([(x * S, y * S) for x, y in pts], fill=fill, width=round(w * S), joint='curve')

    def ell(self, cx, cy, rx, ry, fill=None, outline=None, w=2):
        self.d.ellipse((S * (cx - rx), S * (cy - ry), S * (cx + rx), S * (cy + ry)), fill=fill, outline=outline, width=round(w * S))

    def rect(self, x0, y0, x1, y1, fill=None, outline=None, r=0, w=2):
        self.d.rounded_rectangle((S * x0, S * y0, S * x1, S * y1), r * S, fill=fill, outline=outline, width=round(w * S))

    def poly(self, pts, fill):
        self.d.polygon([(x * S, y * S) for x, y in pts], fill=fill)

    def arc(self, cx, cy, rx, ry, a0, a1, fill, w=2):
        self.d.arc((S * (cx - rx), S * (cy - ry), S * (cx + rx), S * (cy + ry)), a0, a1, fill=fill, width=round(w * S))


def canvas():
    return Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0))


def paint(cv, m, fill, outline=None, ow=1.6, detail=None):
    """마스크 모양을 색으로 칠하고 둘레에 진한 선을 두른다. detail(Draw)는 마스크 안에만 남는다."""
    if outline is None:
        outline = dark(fill)
    if outline:
        k = 2 * round(ow * S) + 1
        dil = m.im.filter(ImageFilter.MaxFilter(k))
        ol = Image.new('RGBA', cv.size, outline + (255,))
        ol.putalpha(dil)
        cv.alpha_composite(ol)
    lay = Image.new('RGBA', cv.size, fill + (255,))
    if detail:
        detail(Draw(lay))
    lay.putalpha(m.im)
    cv.alpha_composite(lay)


def finish(cv):
    small = cv.convert('RGBa').resize((W, H), Image.LANCZOS).convert('RGBA')
    return small


# ---------- 몸 치수 ----------
def geo(g):
    if g == 'm':
        return dict(sh=86, waist=72, wy=420, hip=80, hy=485, neck=36,
                    arm=[(86 - 8, 256), (86 + 24, 385), (86 + 34, 498)], aw=[46, 38, 30], hand=(86 + 36, 522, 21),
                    leg=[(40, 490), (44, 665), (46, 828)], lw=[78, 52, 34], foot=24)
    return dict(sh=76, waist=58, wy=410, hip=84, hy=485, neck=30,
                arm=[(76 - 8, 254), (76 + 22, 380), (76 + 30, 492)], aw=[40, 33, 26], hand=(76 + 32, 514, 19),
                leg=[(40, 490), (42, 665), (42, 828)], lw=[80, 48, 30], foot=22)


def side(pts, s):
    return [(CX + s * x, y) for x, y in pts]


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def leg_at(G, t):
    """다리 위치 t: 0=엉덩이, 1=무릎, 2=발목 → (x, y, 굵기) (오른쪽 다리 기준 x 양수)."""
    i = min(int(t), 1)
    f = t - i
    p = lerp(G['leg'][i], G['leg'][i + 1], f)
    w = G['lw'][i] + (G['lw'][i + 1] - G['lw'][i]) * f
    return p[0], p[1], w


def leg_t(G, y):
    """y 높이에 해당하는 t."""
    (x0, y0), (x1, y1), (x2, y2) = G['leg']
    return (y - y0) / (y1 - y0) if y <= y1 else 1 + (y - y1) / (y2 - y1)


def arm_at(G, t):
    i = min(int(t), 1)
    f = t - i
    p = lerp(G['arm'][i], G['arm'][i + 1], f)
    w = G['aw'][i] + (G['aw'][i + 1] - G['aw'][i]) * f
    return p[0], p[1], w


def torso(G, m, grow=0, top=238, bottom=None):
    sh, wa, hp = G['sh'] + grow, G['waist'] + grow, G['hip'] + grow
    bottom = bottom or G['hy']
    m.poly([(CX - 20 - grow, top - 22), (CX + 20 + grow, top - 22), (CX + sh - 10, top), (CX + sh, top + 14),
            (CX + wa, G['wy']), (CX + hp, G['hy']), (CX + hp, bottom), (CX - hp, bottom), (CX - hp, G['hy']),
            (CX - wa, G['wy']), (CX - sh, top + 14), (CX - sh + 10, top)])
    for s in (-1, 1):
        m.ell(CX + s * (sh - 18), top + 16, 22 + grow / 2, 22 + grow / 2)
    return m


# ---------- 모델 ----------
def model(g):
    G = geo(g)
    cv = canvas()
    hair = (74, 52, 40) if g == 'm' else (96, 62, 44)
    if g == 'f':   # 뒷머리
        paint(cv, Mask().ell(CX, 112, 72, 74).rect(CX - 72, 110, CX + 72, 296, r=30), hair)
    body = Mask()
    body.limb([(CX, 160), (CX, 236)], [G['neck'], G['neck'] + 4])
    torso(G, body, top=238, bottom=530)
    for s in (-1, 1):
        body.limb(side(G['arm'], s), G['aw'])
        hx, hy, hr = G['hand']
        body.ell(CX + s * hx, hy, hr * .9, hr)
        body.limb(side(G['leg'], s), G['lw'])
        fx = CX + s * (G['leg'][2][0] + 4)
        body.ell(fx, 850, G['foot'], 18).ell(fx, 838, G['foot'] - 6, 16)

    def toes(dd):
        for s in (-1, 1):
            fx = CX + s * (G['leg'][2][0] + 4)
            for k in (-1, 0, 1):
                dd.line([(fx + k * 8, 860), (fx + k * 8, 866)], dark(SKIN, .8), 1.4)
    paint(cv, body, SKIN, detail=toes)
    # 속옷(민소매 + 반바지): 무늬 없는 기본 옷
    shirt = Mask().poly([(CX - 30, 236), (CX + 30, 236), (CX + G['sh'] - 22, 246), (CX + G['waist'] + 2, G['wy']),
                         (CX + G['hip'], 470), (CX - G['hip'], 470), (CX - G['waist'] - 2, G['wy']), (CX - G['sh'] + 22, 246)])
    shirt.cut(Mask().ell(CX, 236, 30, 26))
    paint(cv, shirt, UNDER_T)
    shorts = Mask().poly([(CX - G['waist'] - 2, 446), (CX + G['waist'] + 2, 446), (CX + G['hip'] + 2, G['hy']),
                          (CX + G['hip'] + 2, 530), (CX - G['hip'] - 2, 530), (CX - G['hip'] - 2, G['hy'])])
    for s in (-1, 1):
        x, y, w = leg_at(G, leg_t(G, 548 if g == 'm' else 540))
        shorts.limb([(CX + s * 40, 492), (CX + s * x, y)], [80 + 2, w + 4])
    paint(cv, shorts, UNDER_B)
    # 머리
    head = Mask().ell(CX, 112, 56, 64)
    for s in (-1, 1):
        head.ell(CX + s * 55, 122, 10, 15)
    paint(cv, head, SKIN)
    if g == 'm':
        hm = Mask().ell(CX, 96, 61, 54).cut(Mask().ell(CX + 4, 142, 56, 60))
        hm.ell(CX - 52, 104, 9, 22).ell(CX + 52, 104, 9, 22)
    else:
        hm = Mask().ell(CX, 98, 62, 58).cut(Mask().ell(CX + 14, 146, 56, 60))
        hm.ell(CX - 54, 128, 10, 40).ell(CX + 54, 128, 10, 40)
    paint(cv, hm, hair)
    # 얼굴
    d = Draw(cv)
    for s in (-1, 1):
        ex = CX + s * 22
        d.ell(ex, 120, 5.5, 7.5, fill=INK)
        d.ell(ex + 2, 117, 1.8, 1.8, fill=(255, 255, 255))
        d.arc(ex, 104 if g == 'm' else 106, 10, 5, 200, 340, dark(hair, .9), 2.6 if g == 'm' else 2)
        d.ell(CX + s * 34, 140, 9, 5.5, fill=(240, 168, 150))
    d.arc(CX, 129, 4, 3, 20, 160, dark(SKIN, .78), 1.6)
    d.arc(CX, 138, 14, 9, 25, 155, (170, 80, 70), 2.4)
    return finish(cv)


# ---------- 상의 ----------
def top(g, color, sleeve='short', hem=500, neck='crew', detail=None, hood=False, puff=False, cuff=None):
    G = geo(g)
    cv = canvas()
    if hood:
        ring = Mask().ell(CX, 222, 66, 30).cut(Mask().ell(CX, 212, 30, 20))
        paint(cv, ring, dark(color, .88))
    m = torso(G, Mask(), grow=6, top=234, bottom=hem)
    if neck == 'crew':
        m.cut(Mask().ell(CX, 214, 25, 20))
    elif neck == 'v':
        m.cut(Mask().ell(CX, 214, 25, 18).poly([(CX - 24, 214), (CX + 24, 214), (CX, 290)]))
    elif neck == 'collar':
        m.cut(Mask().ell(CX, 214, 22, 18).poly([(CX - 20, 214), (CX + 20, 214), (CX, 262)]))

    def body_detail(dd):
        if neck == 'crew':
            dd.ell(CX, 214, 29, 24, outline=dark(color, .8), w=4)
        if detail:
            detail(dd, G)
        dd.line([(CX - G['hip'] - 10, hem - 6), (CX + G['hip'] + 10, hem - 6)], dark(color, .85), 1.2)
    paint(cv, m, color, detail=body_detail)
    # 소매
    for s in (-1, 1):
        sm = Mask()
        if sleeve == 'short':
            x, y, w = arm_at(G, .45)
            sm.limb([(CX + s * G['arm'][0][0], G['arm'][0][1]), (CX + s * x, y)], [G['aw'][0] + 10, w + 12])
            if puff:
                sm.ell(CX + s * (G['arm'][0][0] + 4), G['arm'][0][1] + 6, 32, 30)
        else:
            t = 1.95 if sleeve == 'long' else 1.5
            pts = [(CX + s * G['arm'][0][0], G['arm'][0][1]), (CX + s * G['arm'][1][0], G['arm'][1][1])]
            x, y, w = arm_at(G, t)
            pts.append((CX + s * x, y))
            sm.limb(pts, [G['aw'][0] + 12, G['aw'][1] + 10, w + 8])

        def sd(dd, s=s):
            if sleeve == 'short':
                x, y, w = arm_at(G, .45)
                ax, ay = CX + s * x, y
                dd.line([(ax - (w + 12) / 2 - 4, ay - 3), (ax + (w + 12) / 2 + 4, ay + 3)] if s > 0 else
                        [(ax - (w + 12) / 2 - 4, ay + 3), (ax + (w + 12) / 2 + 4, ay - 3)], dark(color, .8), 3)
            else:
                t = 1.95 if sleeve == 'long' else 1.5
                x, y, w = arm_at(G, t)
                cc = cuff or dark(color, .82)
                dd.rect(CX + s * x - w / 2 - 6, y - 14, CX + s * x + w / 2 + 6, y + 12, fill=cc)
            if detail and getattr(detail, 'sleeve', None):
                detail.sleeve(dd, G, s)
        paint(cv, sm, color, detail=sd)
    return finish(cv)


def stripes(c):
    def f(dd, G):
        for y in range(240, 520, 22):
            dd.rect(0, y, W, y + 9, fill=c)
    f.sleeve = lambda dd, G, s: [dd.rect(0, y, W, y + 9, fill=c) for y in range(240, 520, 22)]
    return f


def shirt_detail(dd, G):
    c = (110, 146, 188)
    for y in range(240, 520, 18):        # 체크 무늬
        dd.line([(0, y), (W, y)], (168, 200, 232), 3)
    for x in range(0, W, 18):
        dd.line([(x, 230), (x, 520)], (168, 200, 232), 3)
    dd.line([(CX, 262), (CX, 505)], c, 2)
    for y in range(282, 500, 42):
        dd.ell(CX + 6, y, 4, 4, fill=(250, 250, 250), outline=c, w=1)
    dd.rect(CX + 24, 290, CX + 58, 330, outline=c, w=2, r=3)



def knit_detail(dd, G):
    c = dark((96, 132, 88), .82)
    for x in range(CX - 40, CX + 41, 40):        # 꽈배기 무늬
        pts = [(x + (6 if i % 2 else -6), y) for i, y in enumerate(range(250, 470, 14))]
        dd.line(pts, c, 2.4)
    for x in range(CX - 100, CX + 101, 6):         # 밑단 골
        dd.line([(x, 470), (x, 494)], c, 1.2)


def hood_detail(c):
    def f(dd, G):
        k = dark(c, .82)
        dd.poly([(CX - 52, 400), (CX + 52, 400), (CX + 66, 466), (CX - 66, 466)], k)
        dd.poly([(CX - 48, 404), (CX + 48, 404), (CX + 62, 462), (CX - 62, 462)], light(c, .08))
        dd.line([(CX - 14, 226), (CX - 16, 300)], (250, 250, 250), 3)
        dd.line([(CX + 14, 226), (CX + 16, 300)], (250, 250, 250), 3)
        dd.rect(CX - 120, 486, CX + 120, 512, fill=k)
    return f


def blouse_detail(dd, G):
    c = (250, 246, 240)
    for k in range(-3, 4):                         # 동그란 레이스 깃
        a = math.radians(90 + k * 25)
        dd.ell(CX + math.cos(a) * 34, 214 + math.sin(a) * 26, 11, 11, fill=c, outline=(214, 150, 160), w=1.4)
    for y in range(270, 480, 40):
        dd.ell(CX, y, 4.5, 4.5, fill=c, outline=(200, 130, 140), w=1)


def cardi_detail(dd, G):
    c = dark((214, 164, 64), .8)
    dd.line([(CX, 290), (CX, 500)], c, 2.4)
    for y in range(306, 490, 36):
        dd.ell(CX + 8, y, 5, 5, fill=(120, 80, 40))
    for x in range(CX - 110, CX + 111, 6):
        dd.line([(x, 474), (x, 498)], c, 1.2)
    dd.rect(CX + 22, 400, CX + 60, 440, outline=c, w=2, r=4)
    dd.rect(CX - 60, 400, CX - 22, 440, outline=c, w=2, r=4)


def shirt_collar(color):
    """셔츠 깃(목 둘레 두 장)."""
    m = Mask().poly([(CX - 26, 198), (CX - 2, 252), (CX - 34, 240)]).poly([(CX + 26, 198), (CX + 2, 252), (CX + 34, 240)])
    m2 = canvas()
    paint(m2, m, light(color, .4))
    return m2


# ---------- 하의 ----------
def pants(g, color, length='long', wide=0, detail=None, cuff=None, crease=None):
    G = geo(g)
    cv = canvas()
    m = Mask().poly([(CX - G['waist'] - 8, 420), (CX + G['waist'] + 8, 420), (CX + G['hip'] + 8, G['hy']),
                     (CX + G['hip'] + 6, 540), (CX - G['hip'] - 6, 540), (CX - G['hip'] - 8, G['hy'])])
    end_t = 1.95 if length == 'long' else .55
    for s in (-1, 1):
        pts, ws = [], []
        for t in ([0, 1, end_t] if length == 'long' else [0, end_t]):
            x, y, w = leg_at(G, t)
            pts.append((CX + s * x, y))
            ws.append(w + 12 + wide * t)
        if length == 'short':
            ws = [ws[0] + 4, ws[1] + 12]
        m.limb(pts, ws)
    y_end = leg_at(G, end_t)[1]
    m.cut(Mask().rect(0, y_end + (2 if length == 'short' else 8), W, H))
    gap = 6 if length == 'short' else 4
    m.cut(Mask().poly([(CX, 546), (CX - gap, y_end + 10), (CX + gap, y_end + 10)]))   # 두 다리 사이 틈

    def pd(dd):
        k = dark(color, .8)
        dd.rect(CX - G['waist'] - 10, 420, CX + G['waist'] + 10, 440, fill=dark(color, .9))
        dd.line([(CX, 440), (CX, 520)], k, 1.6)
        for s in (-1, 1):
            dd.arc(CX + s * (G['hip'] + 4), 444, 44, 34, 90 if s > 0 else 0, 180 if s > 0 else 90, k, 2)
            if crease:
                x0 = CX + s * 40
                dd.line([(x0, 540), (CX + s * leg_at(G, end_t)[0], leg_at(G, end_t)[1] - 6)], crease, 1.4)
            if cuff:
                x, y, w = leg_at(G, end_t)
                ww = w + 12 + wide * end_t + (12 if length == 'short' else 0)
                dd.rect(CX + s * x - ww / 2 - 10, y - 10, CX + s * x + ww / 2 + 10, y + 12, fill=cuff)
        if detail:
            detail(dd, G)
    paint(cv, m, color, detail=pd)
    return finish(cv)


def jeans_detail(dd, G):
    c = (214, 170, 96)
    for s in (-1, 1):
        x, y, w = leg_at(G, 1.95)
        dd.line([(CX + s * (G['hip'] + 4), 490), (CX + s * (x + w / 2 + 2), y)], c, 1.2)


def track_detail(dd, G):
    for s in (-1, 1):
        x, y, w = leg_at(G, 1.95)
        dd.line([(CX + s * (G['hip'] + 4), 436), (CX + s * (G['hip'] + 4), 500), (CX + s * (x + w / 2 + 3), y - 14)], (245, 245, 245), 4)


def skirt(g, color):
    G = geo(g)
    cv = canvas()
    m = Mask().poly([(CX - G['waist'] - 8, 412), (CX + G['waist'] + 8, 412), (CX + G['hip'] + 12, G['hy']),
                     (CX + G['hip'] + 52, 628), (CX - G['hip'] - 52, 628), (CX - G['hip'] - 12, G['hy'])])
    m.ell(CX, 622, G['hip'] + 52, 16)

    def sd(dd):
        k = dark(color, .8)
        dd.rect(CX - G['waist'] - 12, 412, CX + G['waist'] + 12, 432, fill=dark(color, .88))
        for i in range(-4, 5):
            dd.line([(CX + i * 15, 434), (CX + i * 29, 640)], k, 1.6)
        dd.ell(CX + G['waist'] - 4, 422, 6, 6, fill=(240, 220, 160))
    paint(cv, m, color, detail=sd)
    return finish(cv)


# ---------- 신발 ----------
def shoes(g, kind, color, accent=None):
    G = geo(g)
    cv = canvas()
    for s in (-1, 1):
        fx = CX + s * (G['leg'][2][0] + 4)
        fw = G['foot'] + 6
        if kind == 'sneaker':
            up = Mask().rect(fx - fw, 818, fx + fw, 868, r=18)
            paint(cv, up, color, detail=lambda dd, fx=fx: (
                dd.rect(fx - fw, 818, fx + fw, 828, fill=accent),
                [dd.line([(fx - 9, y), (fx + 9, y)], (120, 120, 130), 2) for y in (834, 842, 850)],
                dd.arc(fx, 856, fw - 2, 10, 200, 340, accent, 4)))
            paint(cv, Mask().rect(fx - fw - 3, 862, fx + fw + 3, 878, r=7), (236, 236, 232))
        elif kind == 'oxford':
            up = Mask().rect(fx - fw + 1, 828, fx + fw - 1, 870, r=18)
            paint(cv, up, color, detail=lambda dd, fx=fx: (
                dd.line([(fx - 8, 836), (fx + 8, 836)], light(color, .3), 2),
                dd.line([(fx - 8, 844), (fx + 8, 844)], light(color, .3), 2),
                dd.ell(fx - 8, 856, 6, 4, fill=light(color, .45))))
            paint(cv, Mask().rect(fx - fw - 2, 866, fx + fw + 2, 876, r=4), dark(color, .6))
        elif kind == 'mary':
            up = Mask().rect(fx - fw + 1, 842, fx + fw - 1, 870, r=14)
            up.rect(fx - fw + 2, 830, fx + fw - 2, 838, r=4)
            paint(cv, up, color, detail=lambda dd, fx=fx: (dd.ell(fx + s * 14, 834, 3, 3, fill=(230, 200, 120)),
                                                           dd.ell(fx - 6, 858, 5, 3, fill=light(color, .4))))
            paint(cv, Mask().rect(fx - fw - 2, 866, fx + fw + 2, 876, r=4), dark(color, .6))
        elif kind == 'sandal':
            st = Mask()
            st.rect(fx - fw, 838, fx + fw, 848, r=4).rect(fx - fw + 2, 852, fx + fw - 2, 860, r=4)
            st.rect(fx - G['lw'][2] / 2 - 4, 816, fx + G['lw'][2] / 2 + 4, 824, r=4)
            st.rect(fx - 4, 816, fx + 4, 846)
            paint(cv, st, color)
            paint(cv, Mask().rect(fx - fw - 2, 866, fx + fw + 2, 878, r=6), accent or dark(color, .7))
        elif kind == 'boot':
            top_y = 740 if g == 'm' else 682
            t = leg_t(G, top_y)
            x, y, w = leg_at(G, t)
            bm = Mask().limb([(CX + s * x, top_y), (fx - s * 4, 832)], [w + 18, G['lw'][2] + 16])
            bm.rect(fx - fw - 1, 820, fx + fw + 1, 870, r=18)
            bm.cut(Mask().rect(0, 0, W, top_y - 2))

            def bd(dd, fx=fx, x=x, w=w):
                dd.rect(CX + s * x - w / 2 - 12, top_y - 4, CX + s * x + w / 2 + 12, top_y + 12, fill=accent or dark(color, .8))
                if g == 'm':
                    for yy in range(top_y + 22, 830, 16):
                        dd.ell(fx - s * 2 - 8, yy, 2.5, 2.5, fill=(230, 210, 170))
                        dd.ell(fx - s * 2 + 8, yy, 2.5, 2.5, fill=(230, 210, 170))
                        dd.line([(fx - s * 2 - 8, yy), (fx - s * 2 + 8, yy + 8)], (230, 210, 170), 1.6)
                else:
                    dd.line([(fx - s * 6, top_y + 18), (fx - s * 4, 846)], dark(color, .8), 1.6)
            paint(cv, bm, color, detail=bd)
            paint(cv, Mask().rect(fx - fw - 3, 866, fx + fw + 3, 878, r=5), dark(color, .5))
    return finish(cv)


# ---------- 목록 (이름은 모두 임시) ----------
def items():
    def shirt_m():
        im = top('m', (150, 186, 222), 'long', 506, 'collar', shirt_detail, cuff=(130, 166, 206))
        im.alpha_composite(finish(shirt_collar((150, 186, 222))))
        return im

    def blouse():
        im = top('f', (238, 170, 180), 'short', 492, 'crew', blouse_detail, puff=True)
        return im

    return {
        'm': {
            'top': [('tshirt', '티셔츠', '주황빛 반소매 티셔츠', lambda: top('m', (217, 100, 74), 'short', 500)),
                    ('shirt', '셔츠', '하늘색 체크무늬 긴소매 셔츠(깃·단추·주머니)', shirt_m),
                    ('knit', '니트', '초록색 꽈배기 무늬 니트', lambda: top('m', (96, 132, 88), 'long', 498, 'crew', knit_detail)),
                    ('hoodie', '후드티', '회색 후드티(모자·끈·앞주머니)', lambda: top('m', (140, 146, 156), 'long', 512, 'crew', hood_detail((140, 146, 156)), hood=True))],
            'bottom': [('jeans', '청바지', '파란 청바지(노란 박음질)', lambda: pants('m', (64, 96, 150), detail=jeans_detail, cuff=(88, 124, 178))),
                       ('chino', '면바지', '베이지색 긴 면바지(주름선)', lambda: pants('m', (200, 176, 130), crease=(176, 152, 108))),
                       ('shorts', '반바지', '카키색 반바지', lambda: pants('m', (150, 150, 96), 'short', cuff=(132, 132, 82))),
                       ('track', '운동복 바지', '검은 운동복 바지(옆 흰 줄·발목 고무단)', lambda: pants('m', (60, 62, 70), detail=track_detail, cuff=(44, 46, 54)))],
            'shoes': [('sneakers', '운동화', '흰색·파랑 운동화', lambda: shoes('m', 'sneaker', (250, 250, 248), (64, 110, 190))),
                      ('dress', '구두', '갈색 구두', lambda: shoes('m', 'oxford', (110, 66, 40))),
                      ('sandals', '샌들', '진갈색 끈 샌들', lambda: shoes('m', 'sandal', (90, 60, 40), (60, 50, 44))),
                      ('boots', '부츠', '갈색 끈 부츠(종아리 높이)', lambda: shoes('m', 'boot', (150, 96, 56)))],
        },
        'f': {
            'top': [('tshirt', '줄무늬 티셔츠', '흰색·남색 줄무늬 반소매 티셔츠', lambda: top('f', (248, 246, 240), 'short', 492, 'crew', stripes((52, 70, 110)))),
                    ('blouse', '블라우스', '분홍 블라우스(레이스 깃·부푼 소매)', blouse),
                    ('knit', '카디건', '겨자색 긴소매 카디건(단추·주머니)', lambda: top('f', (214, 164, 64), 'long', 498, 'v', cardi_detail)),
                    ('hoodie', '후드티', '민트색 후드티(모자·끈·앞주머니)', lambda: top('f', (140, 196, 176), 'long', 508, 'crew', hood_detail((140, 196, 176)), hood=True))],
            'bottom': [('jeans', '청바지', '파란 청바지(노란 박음질)', lambda: pants('f', (76, 110, 168), detail=jeans_detail, cuff=(100, 136, 192))),
                       ('wide', '와이드 바지', '갈색 통 넓은 면바지', lambda: pants('f', (176, 132, 96), wide=12, crease=(150, 110, 78))),
                       ('shorts', '반바지', '연두빛 반바지', lambda: pants('f', (132, 160, 112), 'short', cuff=(114, 142, 96))),
                       ('skirt', '치마', '빨간 주름 치마(무릎 위)', lambda: skirt('f', (200, 80, 72)))],
            'shoes': [('sneakers', '운동화', '흰색·분홍 운동화', lambda: shoes('f', 'sneaker', (250, 250, 248), (226, 120, 150))),
                      ('dress', '구두', '검은 끈 구두(메리제인)', lambda: shoes('f', 'mary', (40, 38, 42))),
                      ('sandals', '샌들', '금빛 끈 샌들', lambda: shoes('f', 'sandal', (206, 164, 90), (170, 130, 80))),
                      ('boots', '부츠', '밤색 무릎 부츠', lambda: shoes('f', 'boot', (156, 90, 52), (130, 74, 44)))],
        },
    }


CAT = {'top': '상의', 'bottom': '하의', 'shoes': '신발'}
GEN = {'m': '남자', 'f': '여자'}


def save(im, path):
    im.save(path, optimize=True)


def thumb(layer, under=None):
    """under가 있으면(신발) 발과 함께 보여 준다."""
    a = layer.getchannel('A')
    x0, y0, x1, y1 = a.getbbox()
    pad = 14
    if under is not None:
        base = under.copy()
        base.alpha_composite(layer)
        layer = base
    crop = layer.crop((x0 - pad, y0 - pad, x1 + pad, y1 + pad))
    k = min((TW - 24) / crop.width, (TW - 24) / crop.height, 1.6)
    crop = crop.convert('RGBa').resize((round(crop.width * k), round(crop.height * k)), Image.LANCZOS).convert('RGBA')
    t = Image.new('RGBA', (TW, TW), (0, 0, 0, 0))
    t.alpha_composite(crop, ((TW - crop.width) // 2, (TW - crop.height) // 2 + 6))
    return stamp(t, scale=.85)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    man = []
    st_txt = f'오른쪽 위 빨간 「임시생성」 도장(모든 층이 같은 자리·같은 크기, 겹치면 도장 하나로 보임)'
    for g in ('m', 'f'):
        p = OUT / f'{g}-model.png'
        bare = model(g)
        save(stamp(bare, scale=STAMP), p)
        man.append({'file': f'src/games/4-1/img/{p.name}',
                    'desc': f'{GEN[g]} 모델(종이 인형 몸). 옷을 입히는 바탕 그림',
                    'structure': f'배경 없음(투명) / 정면으로 선 {GEN[g]} 사람 도형(살구색 피부, {"짧은 갈색 머리" if g == "m" else "어깨까지 오는 갈색 머리"}, 웃는 얼굴, 연회색 민소매·회색 속바지) / 이름표 없음 / {st_txt} / {W}×{H}px PNG',
                    'used_in': '남자·여자 고르기 화면 보기, 옷 고르기 화면 미리보기와 완성 화면의 맨 아래 층'})
        print(p.name)
        for cat, lst in items()[g].items():
            for key, name, desc, fn in lst:
                lay = fn()
                p = OUT / f'{g}-{cat}-{key}.png'
                save(stamp(lay, scale=STAMP), p)
                tp = OUT / f'thumb-{g}-{cat}-{key}.png'
                save(thumb(lay, bare if cat == 'shoes' else None), tp)
                man.append({'file': f'src/games/4-1/img/{p.name}',
                            'desc': f'{GEN[g]} {CAT[cat]} 「{name}」(임시 이름) — {desc}. 모델 위에 겹쳐 입히는 층',
                            'structure': f'배경 없음(투명) / 모델과 같은 자리에 맞춰 그린 옷 도형만 / 이름표 없음 / {st_txt} / {W}×{H}px PNG',
                            'used_in': f'{CAT[cat]} 고르기 화면의 미리보기, 완성 화면(입은 모습)'})
                man.append({'file': f'src/games/4-1/img/{tp.name}',
                            'desc': f'{GEN[g]} {CAT[cat]} 「{name}」(임시 이름) 보기 그림 — {desc}',
                            'structure': f'배경 없음(투명) / 위 층 그림에서 옷만 잘라 가운데에 크게{"(신발은 모델의 발·종아리와 함께)" if cat == "shoes" else ""} / 이름표 없음(이름은 화면 글자로) / 오른쪽 위 빨간 「임시생성」 도장(작게) / {TW}×{TW}px PNG',
                            'used_in': f'{CAT[cat]} 고르기 화면의 보기 버튼 4개 중 하나'})
                print(p.name, tp.name)
    MAN.parent.mkdir(parents=True, exist_ok=True)
    MAN.write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding='utf-8')
    print(len(man), 'files')


if __name__ == '__main__':
    main()

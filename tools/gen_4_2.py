"""전4-2 「나의 공간 아름답게 꾸미기」 임시 그림을 만든다.

빈 방 배경 1장(JPEG) + 가구 7종 x 디자인 3개 = 21개(투명 PNG).
모두 2배 크기로 그린 뒤 줄여서 가장자리를 부드럽게 하고, 「임시생성」 도장을 찍는다.
가구 PNG의 픽셀 크기는 방 배경(1200x900) 위에서의 실제 크기와 같다(index.html의 SIZE와 맞출 것).

    python tools/gen_4_2.py
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402
from placeholder import WALL, WALL2, OAK, OAK2, SKY, LEAF, stamp  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / 'src' / 'games' / '4-2' / 'img'
SS = 2  # 2배로 그린 뒤 줄인다


def dk(c, f=.78):
    return tuple(max(0, round(v * f)) for v in c[:3]) + tuple(c[3:])


def lt(c, f=.35):
    return tuple(round(v + (255 - v) * f) for v in c[:3]) + tuple(c[3:])


class C:
    """최종 픽셀 좌표로 그리면 내부에서 2배로 그려 준다."""

    def __init__(s, w, h, mode='RGBA', bg=(0, 0, 0, 0)):
        s.w, s.h = w, h
        s.im = Image.new(mode, (w * SS, h * SS), bg)
        s.d = ImageDraw.Draw(s.im)

    @staticmethod
    def _b(b):
        return [v * SS for v in b]

    def rect(s, b, fill=None, ol=None, w=2, r=0):
        b = s._b(b)
        if r:
            s.d.rounded_rectangle(b, r * SS, fill=fill, outline=ol, width=w * SS if ol else 0)
        else:
            s.d.rectangle(b, fill=fill, outline=ol, width=w * SS if ol else 0)

    def ell(s, b, fill=None, ol=None, w=2):
        s.d.ellipse(s._b(b), fill=fill, outline=ol, width=w * SS if ol else 0)

    def poly(s, pts, fill=None, ol=None, w=2):
        p = [(x * SS, y * SS) for x, y in pts]
        s.d.polygon(p, fill=fill)
        if ol:
            s.d.line(p + [p[0]], fill=ol, width=w * SS, joint='curve')

    def line(s, pts, fill, w=2):
        s.d.line([(x * SS, y * SS) for x, y in pts], fill=fill, width=round(w * SS), joint='curve')

    def paste(s, layer, xy=(0, 0)):
        s.im.alpha_composite(layer, (xy[0] * SS, xy[1] * SS))

    def done(s):
        return s.im.resize((s.w, s.h), Image.LANCZOS)


# ---------------------------------------------------------------- 방 배경
def room():
    w, h, floor = 1200, 900, 562
    c = C(w, h, 'RGB', WALL)
    d = c.d
    for i in range(floor * SS):  # 벽
        t = i / (floor * SS)
        d.line([(0, i), (w * SS, i)], fill=tuple(round(a + (b - a) * t) for a, b in zip(WALL, WALL2)))
    for x in range(0, w, 40):  # 아주 옅은 벽지 줄무늬
        c.line([(x, 0), (x, floor)], (236, 227, 212), 1)
    # 바닥: 밝은 원목 마루, 아래로 갈수록 판이 넓어진다
    for i in range((h - floor) * SS):
        t = i / ((h - floor) * SS)
        d.line([(0, floor * SS + i), (w * SS, floor * SS + i)], fill=tuple(round(a + (b - a) * t) for a, b in zip(OAK, OAK2)))
    rnd = random.Random(42)
    ys = [floor + round((h - floor) * (k / 7) ** 1.25) for k in range(8)]
    for k, y in enumerate(ys[1:], 1):
        c.line([(0, y), (w, y)], (180, 138, 96), 2)
        y0 = ys[k - 1]
        x = rnd.randint(0, 160)
        while x < w:
            c.line([(x, y0), (x, y)], (184, 142, 100), 2)
            x += rnd.randint(220, 340)
    c.rect((0, floor - 14, w, floor + 2), (250, 247, 240))  # 걸레받이
    c.line([(0, floor + 2), (w, floor + 2)], (214, 202, 184), 2)
    # 창문 (커튼 그림이 380~820 x 60~440에 겹친다)
    c.rect((418, 88, 782, 412), (250, 248, 242), r=6)
    for i in range(300 * SS):
        t = i / (300 * SS)
        d.line([(432 * SS, 100 * SS + i), (768 * SS, 100 * SS + i)], fill=tuple(round(a + (b - a) * t) for a, b in zip((190, 216, 234), SKY)))
    c.ell((470, 140, 560, 180), (250, 252, 252))  # 구름
    c.ell((510, 124, 600, 176), (250, 252, 252))
    for cx, cy, r in [(470, 380, 60), (540, 360, 50), (720, 372, 64), (668, 392, 44)]:  # 바깥 나무
        c.ell((cx - r, cy - r, cx + r, cy + r), LEAF)
    c.rect((432, 100, 768, 400), None, (250, 248, 242), 10)
    c.line([(600, 100), (600, 400)], (250, 248, 242), 10)
    c.line([(432, 250), (768, 250)], (250, 248, 242), 8)
    c.rect((400, 404, 800, 420), (246, 242, 234), (220, 210, 196), 2, r=3)  # 창틀
    # 문
    c.rect((936, 136, 1134, floor), (246, 242, 234), (214, 202, 184), 2)
    c.rect((950, 150, 1120, floor), (214, 186, 150), (186, 156, 120), 2)
    c.rect((970, 176, 1100, 340), None, (192, 162, 126), 3, r=4)
    c.rect((970, 370, 1100, 530), None, (192, 162, 126), 3, r=4)
    c.ell((1084, 344, 1104, 364), (214, 174, 84), (170, 132, 60), 2)
    im = c.done()
    im = stamp(im.convert('RGB'), .75, pos=(20, 18))
    im.save(OUT / 'room.jpg', 'JPEG', quality=84, optimize=True, progressive=True)


# ---------------------------------------------------------------- 커튼 (440x380)
def _panel(c, outline, fill_layer, folds, shade, ol):
    """outline: 다각형 점들. fill_layer: 무늬가 그려진 전체 RGBA. 주름은 세로 띠로."""
    W, H = c.w * SS, c.h * SS
    mask = Image.new('L', (W, H), 0)
    ImageDraw.Draw(mask).polygon([(x * SS, y * SS) for x, y in outline], fill=255)
    lay = fill_layer.copy()
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    xs = [p[0] for p in outline]
    x0, x1 = min(xs), max(xs)
    step = (x1 - x0) / folds
    for k in range(folds):
        a = x0 + step * k + step * .55
        sd.rectangle(((a) * SS, 0, (a + step * .35) * SS, H), fill=shade)
    sh = sh.filter(ImageFilter.GaussianBlur(4 * SS))
    lay.alpha_composite(sh)
    lay.putalpha(Image.composite(lay.getchannel('A'), Image.new('L', (W, H), 0), mask))
    c.im.alpha_composite(lay)
    c.poly(outline, None, ol, 2)


def curtain(kind):
    c = C(440, 380)
    W, H = c.w * SS, c.h * SS
    if kind == 1:  # 베이지 린넨, 묶음끈
        base = (226, 206, 170)
        lay = Image.new('RGBA', (W, H), base + (255,))
        tie = (176, 140, 96)
    elif kind == 2:  # 초록 체크
        base = (250, 248, 240)
        lay = Image.new('RGBA', (W, H), base + (255,))
        ld = ImageDraw.Draw(lay)
        g = (120, 160, 110, 150)
        for x in range(0, W, 24 * SS):
            ld.rectangle((x, 0, x + 12 * SS, H), fill=g)
        ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        for y in range(0, H, 24 * SS):
            od.rectangle((0, y, W, y + 12 * SS), fill=g)
        lay.alpha_composite(ov)
        base = (150, 182, 136)
        tie = None
    else:  # 분홍 꽃무늬, 물결 덮개
        base = (240, 190, 192)
        lay = Image.new('RGBA', (W, H), base + (255,))
        ld = ImageDraw.Draw(lay)
        rnd = random.Random(7)
        for yy in range(10, 380, 34):
            for xx in range(6 + (yy // 34 % 2) * 17, 440, 34):
                x, y = (xx + rnd.randint(-3, 3)) * SS, (yy + rnd.randint(-3, 3)) * SS
                r = 4 * SS
                for dx, dy in [(-r, 0), (r, 0), (0, -r), (0, r)]:
                    ld.ellipse((x + dx - r, y + dy - r, x + dx + r, y + dy + r), fill=(255, 250, 246))
                ld.ellipse((x - r * .7, y - r * .7, x + r * .7, y + r * .7), fill=(236, 186, 84))
        tie = (200, 120, 130)
    shade = dk(base, .7)[:3] + (110,)
    c.line([(8, 22), (432, 22)], (130, 100, 70), 7)  # 봉
    for x in (10, 430):
        c.ell((x - 10, 12, x + 10, 32), (150, 116, 80), (110, 84, 56), 2)
    if kind == 2:
        L = [(16, 24), (136, 24), (130, 376), (14, 376)]
        R = [(304, 24), (424, 24), (426, 376), (310, 376)]
    else:
        L = [(16, 24), (150, 24), (128, 150), (86, 246), (118, 330), (138, 376), (14, 376)]
        R = [(290, 24), (424, 24), (426, 376), (302, 376), (322, 330), (354, 246), (312, 150)]
    _panel(c, L, lay, 5, shade, dk(base, .72))
    _panel(c, R, lay, 5, shade, dk(base, .72))
    for x in range(30, 424, 30) if kind != 3 else []:  # 고리
        if x < 150 or x > 290:
            c.ell((x - 5, 16, x + 5, 28), None, (110, 84, 56), 2)
    if tie:
        c.rect((72, 238, 100, 256), tie, dk(tie), 2, r=6)
        c.rect((340, 238, 368, 256), tie, dk(tie), 2, r=6)
    if kind == 3:  # 물결 덮개
        n = 8
        mask = Image.new('L', (W, H), 0)
        md = ImageDraw.Draw(mask)
        md.rectangle((4 * SS, 14 * SS, 436 * SS, 54 * SS), fill=255)
        for k in range(n):
            x0 = 4 + 432 * k / n
            md.ellipse((x0 * SS, 34 * SS, (x0 + 432 / n) * SS, 74 * SS), fill=255)
        v = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        v.alpha_composite(lay)
        v.putalpha(mask)
        c.im.alpha_composite(v)
        edge = mask.filter(ImageFilter.FIND_EDGES).point(lambda p: 255 if p > 40 else 0).filter(ImageFilter.MaxFilter(3))
        e = Image.new('RGBA', (W, H), dk(base, .72) + (255,))
        e.putalpha(edge)
        c.im.alpha_composite(e)
    im = c.done()
    return stamp(im, .55, pos=(330, 120))


# ---------------------------------------------------------------- 책꽂이 (200x340)
BOOKS = [(185, 84, 60), (63, 111, 168), (79, 122, 58), (201, 138, 28), (140, 96, 150), (230, 214, 190), (90, 120, 130)]


def _books(c, x0, x1, ybot, hmax, seed):
    rnd = random.Random(seed)
    x = x0 + 2
    while x < x1 - 10:
        bw = rnd.randint(8, 14)
        bh = rnd.randint(int(hmax * .7), hmax)
        if x + bw > x1 - 2:
            break
        col = rnd.choice(BOOKS)
        if rnd.random() < .12 and x + bh < x1:  # 눕힌 책
            c.rect((x, ybot - bw, x + bh, ybot), col, dk(col), 1)
            x += bh + 2
            continue
        c.rect((x, ybot - bh, x + bw, ybot), col, dk(col), 1)
        c.line([(x + 2, ybot - bh + 6), (x + bw - 2, ybot - bh + 6)], lt(col, .5), 1.5)
        x += bw + 1


def _pot(c, cx, ybot, s=1.0, pot=(236, 228, 214)):
    c.rect((cx - 12 * s, ybot - 18 * s, cx + 12 * s, ybot), pot, dk(pot, .85), 1, r=3)
    for dx, dy, r in [(-8, -26, 9), (7, -30, 10), (0, -40, 9)]:
        c.ell((cx + (dx - r) * s, ybot + (dy - r) * s, cx + (dx + r) * s, ybot + (dy + r) * s), LEAF, dk(LEAF), 1)


def shelf(kind):
    c = C(200, 340)
    if kind == 1:  # 원목 4칸
        wood = (200, 158, 108)
        c.rect((10, 10, 190, 334), wood, dk(wood), 2, r=3)
        c.rect((22, 22, 178, 322), dk(wood, .82))
        ys = [22, 96, 172, 248, 322]
        for k in range(4):
            top, bot = ys[k], ys[k + 1]
            if k == 1:
                _books(c, 22, 120, bot, bot - top - 12, k)
                _pot(c, 150, bot, .9)
            else:
                _books(c, 22, 178, bot, bot - top - 12, k + 3)
            if k < 3:
                c.rect((22, bot - 1, 178, bot + 9), wood, dk(wood), 1)
    elif kind == 2:  # 화이트 큐브 2x3 + 위에 화분
        wh = (248, 246, 240)
        c.rect((14, 60, 186, 334), wh, (200, 194, 184), 2, r=3)
        cells = []
        for r in range(3):
            for q in range(2):
                x0, y0 = 24 + q * 81, 70 + r * 88
                c.rect((x0, y0, x0 + 71, y0 + 78), (232, 228, 220), (210, 204, 194), 1)
                cells.append((x0, y0))
        _books(c, cells[0][0], cells[0][0] + 71, cells[0][1] + 78, 64, 11)
        c.rect((cells[1][0] + 6, cells[1][1] + 34, cells[1][0] + 65, cells[1][1] + 78), (196, 170, 130), dk((196, 170, 130)), 1, r=4)  # 바구니
        for k in range(3):
            c.line([(cells[1][0] + 10, cells[1][1] + 46 + k * 10), (cells[1][0] + 61, cells[1][1] + 46 + k * 10)], dk((196, 170, 130)), 1)
        _books(c, cells[2][0], cells[2][0] + 71, cells[2][1] + 78, 60, 12)
        _pot(c, cells[3][0] + 36, cells[3][1] + 78, 1.1, (250, 214, 190))
        _books(c, cells[4][0], cells[4][0] + 71, cells[4][1] + 78, 62, 13)
        _books(c, cells[5][0], cells[5][0] + 71, cells[5][1] + 78, 56, 14)
        _pot(c, 100, 60, 1.4)
    else:  # 검정 사다리 + 호두나무 선반
        metal, wal = (60, 56, 52), (140, 98, 66)
        c.line([(14, 336), (66, 6)], metal, 6)
        c.line([(186, 336), (134, 6)], metal, 6)
        for k, y in enumerate((80, 160, 240, 322)):  # 선반 높이
            x0, x1 = 14 + (336 - y) * 52 / 330, 186 - (336 - y) * 52 / 330
            if k < 3:
                _books(c, x0 + 4, x1 - 4 - (40 if k == 0 else 0), y - 4, 56, 20 + k)
            if k == 0:
                _pot(c, x1 - 22, y - 4, .8, (220, 120, 90))
            if k == 3:
                c.rect((x0 + 20, y - 40, x1 - 20, y - 4), (230, 214, 190), dk((230, 214, 190)), 1, r=4)  # 상자
            c.rect((x0 - 4, y - 4, x1 + 4, y + 6), wal, dk(wal), 1, r=2)
    return stamp(c.done(), 1.15)


# ---------------------------------------------------------------- 침대 (460x260)
def bed(kind):
    c = C(460, 260)
    if kind == 1:
        frame, blank = (200, 158, 108), (106, 146, 196)
        c.rect((10, 40, 62, 250), frame, dk(frame), 2, r=14)  # 머리판
        c.rect((420, 130, 450, 250), frame, dk(frame), 2, r=8)  # 발판
        c.rect((44, 176, 444, 214), frame, dk(frame), 2, r=4)
        for x in (56, 420):
            c.rect((x, 210, x + 16, 252), dk(frame, .9), dk(frame, .7), 1)
    elif kind == 2:
        frame, blank = (52, 66, 104), (210, 214, 220)
        c.rect((6, 20, 76, 248), frame, dk(frame), 2, r=34)
        for y in range(56, 200, 36):
            for x in (28, 54):
                c.ell((x - 3, y - 3, x + 3, y + 3), dk(frame, .7))
        c.rect((60, 180, 452, 224), frame, dk(frame), 2, r=10)
        for x in (80, 432):
            c.rect((x, 222, x + 12, 246), (150, 116, 80))
    else:
        frame, blank = (248, 246, 240), (240, 176, 180)
        ol = (196, 190, 180)
        c.rect((10, 40, 22, 250), frame, ol, 2, r=4)
        c.rect((58, 40, 70, 250), frame, ol, 2, r=4)
        c.rect((10, 34, 70, 52), frame, ol, 2, r=8)
        for x in (28, 40, 52):
            c.rect((x - 2, 52, x + 2, 176), frame, ol, 1)
        c.rect((424, 120, 434, 250), frame, ol, 2, r=4)
        c.rect((444, 120, 454, 250), frame, ol, 2, r=4)
        c.rect((420, 112, 456, 126), frame, ol, 2, r=6)
        c.rect((40, 176, 440, 206), frame, ol, 2, r=4)
    c.rect((54, 128, 432, 182), (252, 251, 248), (214, 208, 198), 2, r=10)  # 매트리스
    c.ell((70, 98, 168, 142), (250, 250, 246), (210, 204, 196), 2)  # 베개
    c.poly([(176, 118), (432, 120), (440, 210), (176, 206)], blank, dk(blank), 2)  # 이불
    c.rect((170, 116, 440, 134), lt(blank, .25), dk(blank), 2, r=8)
    if kind == 2:
        c.line([(180, 170), (438, 172)], (160, 166, 176), 6)
    if kind == 3:
        for y in range(146, 204, 18):
            for x in range(190 + (y // 18 % 2) * 12, 430, 24):
                c.ell((x - 3, y - 3, x + 3, y + 3), (255, 248, 248))
    return stamp(c.done(), 1.0, pos=(380, 4))


# ---------------------------------------------------------------- 책상 (300x210)
def desk(kind):
    c = C(300, 210)
    if kind == 1:
        wood = (200, 158, 108)
        c.rect((14, 86, 26, 206), dk(wood, .9), dk(wood, .7), 1)
        c.rect((274, 86, 286, 206), dk(wood, .9), dk(wood, .7), 1)
        c.rect((180, 86, 274, 124), wood, dk(wood), 2)
        c.rect((216, 102, 238, 108), (120, 90, 60), r=2)
        c.rect((4, 70, 296, 88), wood, dk(wood), 2, r=3)
        for k, col in enumerate([(63, 111, 168), (185, 84, 60), (230, 214, 190)]):  # 책 더미
            c.rect((30 + k * 3, 58 - k * 10, 100 - k * 3, 70 - k * 10), col, dk(col), 1, r=2)
        c.rect((220, 40, 246, 70), (250, 248, 240), (200, 194, 184), 2, r=4)  # 연필꽂이
        for x, col in [(226, (201, 138, 28)), (233, (185, 84, 60)), (240, (63, 111, 168))]:
            c.line([(x, 40), (x - 2, 22)], col, 3)
    elif kind == 2:
        wh, ol = (248, 246, 240), (200, 194, 184)
        c.rect((12, 86, 104, 206), wh, ol, 2)
        for k in range(3):
            y = 92 + k * 38
            c.rect((18, y, 98, y + 32), wh, ol, 1, r=2)
            c.rect((48, y + 14, 68, y + 18), (170, 166, 158), r=2)
        c.rect((278, 86, 290, 206), wh, ol, 2)
        c.rect((4, 70, 296, 88), wh, ol, 2, r=3)
        # 스탠드
        c.ell((210, 62, 250, 72), (90, 90, 90))
        c.line([(230, 66), (248, 30), (222, 14)], (90, 90, 90), 4)
        c.poly([(206, 10), (236, 4), (232, 30)], (241, 201, 107), dk((241, 201, 107)), 2)
        c.rect((140, 60, 186, 70), (63, 111, 168), dk((63, 111, 168)), 1, r=2)
    else:
        mint, leg = (158, 206, 190), (54, 54, 54)
        for x0 in (20, 260):
            c.line([(x0, 90), (x0 + 6, 206), (x0 + 12, 90)], leg, 3)
        c.rect((4, 66, 296, 90), mint, dk(mint), 2, r=8)
        c.rect((150, 52, 230, 66), (180, 182, 188), (120, 122, 128), 2, r=2)  # 노트북
        c.poly([(160, 52), (220, 52), (232, 6), (172, 6)], (196, 198, 204), (120, 122, 128), 2)
        _pot(c, 60, 66, 1.0, (250, 248, 240))
    return stamp(c.done(), 1.2)


# ---------------------------------------------------------------- 옷장 (230x400)
def closet(kind):
    c = C(230, 400)
    if kind == 1:
        wood = (196, 152, 102)
        c.rect((14, 380, 30, 398), dk(wood, .7))
        c.rect((200, 380, 216, 398), dk(wood, .7))
        c.rect((10, 22, 220, 382), wood, dk(wood), 2, r=3)
        c.rect((4, 10, 226, 26), lt(wood, .1), dk(wood), 2, r=3)  # 윗장식
        for x0 in (20, 117):
            c.rect((x0, 34, x0 + 93, 372), lt(wood, .08), dk(wood, .85), 2, r=3)
            c.rect((x0 + 12, 50, x0 + 81, 200), None, dk(wood, .88), 2, r=3)
            c.rect((x0 + 12, 216, x0 + 81, 356), None, dk(wood, .88), 2, r=3)
        c.ell((100, 200, 110, 210), (214, 174, 84), (150, 116, 60), 1)
        c.ell((120, 200, 130, 210), (214, 174, 84), (150, 116, 60), 1)
    elif kind == 2:
        wh, ol = (248, 246, 240), (196, 190, 180)
        c.rect((10, 10, 220, 390), wh, ol, 2, r=4)
        for k in range(3):
            x0 = 18 + k * 66
            c.rect((x0, 18, x0 + 62, 296), wh, ol, 2, r=2)
            kx = x0 + (52 if k == 0 else 6)
            c.rect((kx, 140, kx + 4, 176), (160, 156, 150), r=2)
        for k in range(2):
            y0 = 302 + k * 42
            c.rect((18, y0, 212, y0 + 38), wh, ol, 2, r=2)
            c.rect((100, y0 + 16, 130, y0 + 21), (160, 156, 150), r=2)
    else:
        gr = (132, 150, 170)
        c.rect((16, 382, 28, 398), (90, 80, 70))
        c.rect((202, 382, 214, 398), (90, 80, 70))
        c.rect((10, 10, 220, 384), gr, dk(gr), 2, r=22)
        c.rect((22, 26, 112, 370), (214, 232, 242), dk(gr, .9), 3, r=14)  # 거울 문
        c.line([(36, 120), (88, 60)], (250, 252, 255), 6)
        c.line([(40, 160), (100, 92)], (250, 252, 255), 3)
        c.rect((118, 26, 208, 370), lt(gr, .12), dk(gr, .9), 2, r=14)
        c.rect((124, 180, 130, 230), (230, 230, 230), r=3)
        c.rect((100, 180, 106, 230), (230, 230, 230), r=3)
    return stamp(c.done(), 1.05)


# ---------------------------------------------------------------- 테이블 (210x130)
def table(kind):
    c = C(210, 130)
    if kind == 1:
        wood = (200, 158, 108)
        c.ell((60, 112, 150, 128), dk(wood, .85), dk(wood, .7), 2)
        c.rect((96, 50, 114, 118), dk(wood, .9), dk(wood, .7), 2)
        c.ell((6, 44, 204, 66), dk(wood, .9), dk(wood, .7), 2)
        c.ell((6, 36, 204, 58), wood, dk(wood), 2)
        c.rect((120, 18, 142, 46), (250, 248, 240), (190, 184, 174), 2, r=4)  # 컵
        c.ell((140, 24, 152, 38), None, (190, 184, 174), 3)
    elif kind == 2:
        wh, ol = (248, 246, 240), (196, 190, 180)
        c.rect((30, 64, 38, 112), (228, 224, 216))
        c.rect((172, 64, 180, 112), (228, 224, 216))
        c.rect((14, 96, 196, 104), wh, ol, 2)
        c.rect((12, 64, 22, 126), wh, ol, 2)
        c.rect((188, 64, 198, 126), wh, ol, 2)
        c.rect((4, 52, 206, 66), wh, ol, 2, r=3)
        for k, col in enumerate([(63, 111, 168), (201, 138, 28)]):
            c.rect((40 + k * 4, 88 - k * 8, 110 - k * 4, 96 - k * 8), col, dk(col), 1, r=2)
        c.ell((140, 40, 176, 54), (241, 201, 107), dk((241, 201, 107)), 2)  # 접시
    else:
        ye, leg = (240, 196, 84), (200, 158, 108)
        for a, b in [((52, 64), (26, 128)), ((158, 64), (184, 128)), ((105, 66), (105, 126))]:
            c.line([a, b], dk(leg), 7)
            c.line([a, b], leg, 4)
        c.ell((20, 56, 190, 74), dk(ye, .85), dk(ye, .7), 2)
        c.ell((20, 50, 190, 68), ye, dk(ye), 2)
        c.rect((90, 26, 116, 58), (120, 160, 190), dk((120, 160, 190)), 2, r=8)  # 꽃병
        c.line([(103, 26), (96, 8)], LEAF, 3)
        c.line([(103, 26), (112, 6)], LEAF, 3)
        c.ell((90, 2, 102, 14), (230, 110, 120))
        c.ell((106, 0, 118, 12), (250, 250, 246), (200, 194, 184), 1)
    return stamp(c.done(), 1.3)


# ---------------------------------------------------------------- 의자 (150x190)
def chair(kind):
    c = C(150, 190)
    if kind == 1:
        wood = (196, 152, 102)
        for x in (36, 104):
            c.rect((x, 10, x + 10, 116), wood, dk(wood), 2, r=3)
        for y in (20, 46, 72):
            c.rect((40, y, 110, y + 12), wood, dk(wood), 2, r=3)
        for x in (32, 108):
            c.rect((x, 118, x + 10, 186), dk(wood, .9), dk(wood, .7), 1)
        c.poly([(26, 104), (124, 104), (130, 122), (20, 122)], lt(wood, .05), dk(wood), 2)
    elif kind == 2:
        pk = (232, 160, 168)
        c.rect((30, 164, 40, 186), (120, 90, 60))
        c.rect((110, 164, 120, 186), (120, 90, 60))
        c.rect((22, 26, 128, 128), pk, dk(pk), 2, r=34)  # 등받이
        c.rect((4, 86, 40, 168), pk, dk(pk), 2, r=16)  # 팔걸이
        c.rect((110, 86, 146, 168), pk, dk(pk), 2, r=16)
        c.rect((30, 112, 120, 168), lt(pk, .12), dk(pk), 2, r=12)  # 방석
        c.line([(36, 140), (114, 140)], dk(pk, .9), 2)
    else:
        bl, leg = (74, 128, 196), (60, 56, 52)
        for a, b in [((48, 124), (26, 186)), ((102, 124), (124, 186)), ((66, 126), (58, 180)), ((84, 126), (92, 180))]:
            c.line([a, b], leg, 4)
        c.rect((32, 14, 118, 104), bl, dk(bl), 2, r=36)
        c.rect((44, 26, 106, 90), lt(bl, .1), None, r=28)
        c.ell((20, 98, 130, 130), bl, dk(bl), 2)
        c.ell((28, 100, 122, 120), lt(bl, .12))
    return stamp(c.done(), 1.3)


def save_png(im, name):
    # 색 수를 줄여(알파 포함) 크기를 줄인다
    q = im.quantize(colors=200, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
    q.save(OUT / name, optimize=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True, exist_ok=True)
    room()
    for fn in (curtain, shelf, bed, desk, closet, table, chair):
        for k in (1, 2, 3):
            save_png(fn(k), f'{fn.__name__}-{k}.png')
    tot = 0
    for p in sorted(OUT.iterdir()):
        tot += p.stat().st_size
        print(p.name, p.stat().st_size // 1024, 'KB')
    print('합계', tot // 1024, 'KB')

"""빠진 사진 대신 쓰는 임시 일러스트를 만든다. 진짜 사진이 오면 같은 파일 이름으로 덮어쓰면 된다.

기존 사진(밝은 낮빛, 크림 벽, 밝은 원목 바닥, 화분)과 같은 색감으로 배경을 그리고,
가운데에 이모지 그림, 아래에 이름표, 오른쪽 위에 빨간 「임시생성」 도장을 찍는다.

    from placeholder import scene, stamp
    scene(out_path, '스트레칭', '🧘', bg='room')           # JPEG 사진 대용
    img = stamp(rgba_image)                                 # 직접 그린 그림에 도장만 찍기
"""
import random
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONTS = Path('C:/Windows/Fonts')
KO = str(FONTS / 'malgunbd.ttf')
EMOJI = str(FONTS / 'seguiemj.ttf')

# 기존 사진에서 뽑은 색
WALL = (241, 233, 220)
WALL2 = (230, 219, 202)
OAK = (205, 163, 116)
OAK2 = (186, 142, 98)
SKY = (214, 230, 238)
LEAF = (110, 140, 92)
INK = (69, 63, 54)
RED = (185, 84, 60)


def font(size, path=KO):
    return ImageFont.truetype(path, size)


def _vgrad(d, box, top, bottom):
    x0, y0, x1, y1 = box
    h = max(1, y1 - y0)
    for i in range(h):
        t = i / h
        d.line([(x0, y0 + i), (x1, y0 + i)], fill=tuple(round(a + (b - a) * t) for a, b in zip(top, bottom)))


def _plant(d, x, y, s=1.0):
    d.rounded_rectangle((x - 26 * s, y - 44 * s, x + 26 * s, y), 8 * s, fill=(236, 228, 214), outline=(214, 202, 184), width=2)
    for dx, dy, r in [(-22, -80, 26), (18, -92, 28), (0, -118, 26), (-30, -112, 20), (30, -124, 20)]:
        d.ellipse((x + (dx - r) * s, y + (dy - r) * s, x + (dx + r) * s, y + (dy + r) * s), fill=LEAF)


def background(w, h, bg='room'):
    im = Image.new('RGB', (w, h), WALL)
    d = ImageDraw.Draw(im)
    floor = round(h * .68)
    if bg in ('room', 'kitchen', 'bath', 'bedroom'):
        _vgrad(d, (0, 0, w, floor), WALL, WALL2)
        if bg == 'bath':
            for x in range(0, w, 60):
                d.line([(x, 0), (x, floor)], fill=(222, 214, 200), width=2)
            for y in range(0, floor, 60):
                d.line([(0, y), (w, y)], fill=(222, 214, 200), width=2)
            _vgrad(d, (0, floor, w, h), (214, 210, 200), (196, 190, 178))
        else:
            # 창문
            wx = round(w * .66)
            d.rounded_rectangle((wx, round(h * .08), wx + round(w * .26), round(h * .52)), 6, fill=SKY, outline=(250, 248, 242), width=10)
            d.line([(wx + round(w * .13), round(h * .08)), (wx + round(w * .13), round(h * .52))], fill=(250, 248, 242), width=8)
            _vgrad(d, (0, floor, w, h), OAK, OAK2)
            for x in range(-h, w, 120):
                d.line([(x, h), (x + (h - floor) * 2, floor)], fill=(194, 151, 106), width=2)
        if bg == 'kitchen':
            d.rectangle((0, round(h * .50), round(w * .55), floor), fill=(232, 222, 205))
            d.rectangle((0, round(h * .47), round(w * .55), round(h * .50)), fill=(250, 247, 240))
        if bg == 'bedroom':
            d.rounded_rectangle((round(w * .05), round(h * .48), round(w * .40), round(h * .74)), 16, fill=(250, 248, 244), outline=(220, 210, 196), width=3)
            d.rounded_rectangle((round(w * .05), round(h * .60), round(w * .40), round(h * .74)), 10, fill=(70, 86, 120))
        d.rectangle((0, floor - 6, w, floor), fill=(250, 247, 240))
        if bg != 'bath':
            _plant(d, round(w * .08), floor - 4, h / 800)
    elif bg == 'outdoor':
        _vgrad(d, (0, 0, w, floor), (200, 224, 238), (236, 240, 232))
        for cx, r in [(.1, .14), (.27, .1), (.86, .16), (.7, .09)]:
            x, rr = round(w * cx), round(h * r)
            d.rectangle((x - 8, floor - rr * 2, x + 8, floor), fill=(140, 108, 76))
            d.ellipse((x - rr, floor - rr * 3, x + rr, floor - rr), fill=(132, 166, 104))
        _vgrad(d, (0, floor, w, h), (168, 196, 126), (140, 172, 104))
        d.polygon([(w * .42, h), (w * .5, floor), (w * .56, floor), (w * .7, h)], fill=(226, 214, 190))
    elif bg == 'town':
        _vgrad(d, (0, 0, w, floor), (206, 226, 238), (238, 238, 230))
        rnd = random.Random(w + h)
        x = 0
        while x < w:
            bw, bh = rnd.randint(90, 170), rnd.randint(round(h * .2), round(h * .5))
            d.rectangle((x, floor - bh, x + bw, floor), fill=rnd.choice([(226, 214, 196), (214, 200, 184), (232, 226, 214)]))
            for wy in range(floor - bh + 20, floor - 30, 44):
                for wx in range(x + 16, x + bw - 24, 36):
                    d.rectangle((wx, wy, wx + 18, wy + 22), fill=SKY)
            x += bw + 8
        _vgrad(d, (0, floor, w, h), (196, 190, 180), (176, 170, 160))
    else:  # paper
        _vgrad(d, (0, 0, w, h), (255, 250, 240), (244, 239, 223))
    return im


def _glyph(f, ch):
    im = Image.new('L', (f.size * 2, f.size * 2))
    ImageDraw.Draw(im).text((0, 0), ch, font=f, fill=255)
    return im.tobytes()


def emoji_layer(chars, size):
    """이모지 문자열을 색 그림으로 그려 투명 RGBA로 돌려준다."""
    f = ImageFont.truetype(EMOJI, size)
    if '‍' in chars:
        print(f'경고: {chars!r} — ZWJ 이모지는 합쳐지지 않고 따로 그려집니다. 한 글자 이모지를 쓰세요', file=sys.stderr)
    for ch in chars:
        if ch not in '‍️' and _glyph(f, ch) == _glyph(f, '􏿽'):
            raise ValueError(f'Segoe UI Emoji에 없는 이모지: {ch!r} (U+{ord(ch):04X}) — 다른 이모지를 쓰세요')
    l, t, r, b = f.getbbox(chars)
    layer = Image.new('RGBA', (r - l + 20, b - t + 20), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((10 - l, 10 - t), chars, font=f, embedded_color=True)
    return layer


def stamp(im, scale=1.0, pos=None, text='임시생성'):
    """빨간 원형 「임시생성」 도장을 찍는다(오른쪽 위, -14도). RGB·RGBA 모두 된다."""
    w, h = im.size
    s = round(min(w, h) * .26 * scale)
    st = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(st)
    c = RED + (235,)
    lw = max(3, s // 26)
    d.ellipse((lw, lw, s - lw, s - lw), outline=c, width=lw)
    d.ellipse((lw * 3, lw * 3, s - lw * 3, s - lw * 3), outline=c, width=max(2, lw // 2))
    f = font(round(s * .16))
    tw = d.textlength(text, font=f)
    d.text(((s - tw) / 2, s / 2 - s * .15), text, font=f, fill=c)
    f2 = font(round(s * .085))
    for y, t in [(s * .18, 'TEMP'), (s * .7, '사진 교체 예정')]:
        tw = d.textlength(t, font=f2)
        d.text(((s - tw) / 2, y), t, font=f2, fill=c)
    # 도장 잉크가 군데군데 빠진 느낌
    rnd = random.Random(s)
    mask = st.getchannel('A')
    md = ImageDraw.Draw(mask)
    for _ in range(s * 2):
        x, y, r = rnd.randrange(s), rnd.randrange(s), rnd.choice([1, 1, 2, 3])
        md.ellipse((x - r, y - r, x + r, y + r), fill=0)
    st.putalpha(mask)
    st = st.rotate(14, resample=Image.BICUBIC, expand=True)
    if pos is None:
        pos = (w - st.width - round(w * .02), round(h * .02))
    base = im.convert('RGBA')
    base.alpha_composite(st, pos)
    return base if im.mode == 'RGBA' else base.convert('RGB')


def label(im, text, sub=None):
    """아래쪽 가운데에 종이 이름표를 붙인다."""
    w, h = im.size
    d = ImageDraw.Draw(im)
    f = font(round(h * .075))
    tw = d.textlength(text, font=f)
    pad = round(h * .03)
    bw = tw + pad * 4
    bh = round(h * .075) + pad * 2 + (round(h * .045) + 4 if sub else 0)
    x0, y0 = (w - bw) / 2, h - bh - round(h * .05)
    d.rounded_rectangle((x0 + 4, y0 + 6, x0 + bw + 4, y0 + bh + 6), 14, fill=(0, 0, 0, 40) if im.mode == 'RGBA' else (200, 186, 166))
    d.rounded_rectangle((x0, y0, x0 + bw, y0 + bh), 14, fill=(255, 250, 240), outline=(216, 201, 179), width=3)
    d.text(((w - tw) / 2, y0 + pad - h * .012), text, font=f, fill=INK)
    if sub:
        f2 = font(round(h * .04))
        sw = d.textlength(sub, font=f2)
        d.text(((w - sw) / 2, y0 + pad + round(h * .08)), sub, font=f2, fill=(128, 118, 105))
    return im


def scene(out, text, emoji, bg='room', size=(1200, 800), sub=None, quality=84):
    """배경 + 이모지 그림 + 이름표 + 도장을 그려 JPEG으로 저장한다. text=None이면 이름표 없이."""
    w, h = size
    im = background(w, h, bg).convert('RGBA')
    em = emoji_layer(emoji, round(h * .32))
    if em.width > w * .8:
        k = w * .8 / em.width
        em = em.resize((round(em.width * k), round(em.height * k)), Image.LANCZOS)
    cx, cy = w // 2, round(h * (.44 if text else .5))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((cx - em.width * .42, cy + em.height * .36, cx + em.width * .42, cy + em.height * .52), fill=(60, 40, 20, 70))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
    im.alpha_composite(em, (cx - em.width // 2, cy - em.height // 2))
    im = im.convert('RGB')
    if text:
        label(im, text, sub)
    im = stamp(im)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    im.save(out, 'JPEG', quality=quality, optimize=True, progressive=True)
    return out


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    o = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
    for bg, t, e in [('room', '스트레칭', '🧘'), ('outdoor', '산책', '🚶'), ('kitchen', '요리', '🍳'), ('town', '버스 타기', '🚌'), ('bath', '양치', '🪥'), ('bedroom', '잠자기', '😴')]:
        print(scene(o / f'sample-{bg}.jpg', t, e, bg))

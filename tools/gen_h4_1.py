"""후4-1 「위급 신호 몸으로 따라 하기」 — 증상 대표 사진과 단계 그림을 만든다.
사용: python tools/gen_h4_1.py   → src/games/h4-1/img/*.jpg, tools/placeholder_manifest/h4-1.json

- 증상 대표 사진 3장(face·arm·chest.jpg)은 「후 4-3」 폴더의 진짜 사진을 줄여 쓴다(도장 없음).
- 「갑자기 머리가 매우 아파요」 대표 사진(head.jpg)과 단계 사진 16장(<증상>-<1~4>.jpg)은 원본이 없어
  임시 그림으로 그린다: 거실 배경 + 이모지 + 동작 문구 이름표 + 빨간 「임시생성」 도장.
  진짜 사진이 오면 같은 파일 이름으로 덮어쓰고, 매니페스트에서 그 항목을 지운다.
"""
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
from placeholder import background, emoji_layer, stamp, font, INK  # noqa: E402

SRC = ROOT / 'data' / '_1102' / '후기 게임자료' / '게임개발' / '후 4-3'
OUT = ROOT / 'src' / 'games' / 'h4-1' / 'img'
SIZE = (1200, 800)
REAL = [('face.jpg', '얼굴이 비뚤어짐.png'), ('arm.jpg', '한쪽 팔에 힘이 빠짐.png'), ('chest.jpg', '가슴 통증.png')]

# 증상 키, 증상 문구, 단계 4개(요청서 문구 그대로, 이모지)
SYMS = [
    ('face', '얼굴이 비뚤어졌어요', [('거울을 봐요', '👀🙂'), ('‘이’하고 소리를 내요', '😬🗣'),
                               ('소리를 내며 손가락으로 한 쪽 입술 끝을 눌러요', '👉👄'), ('누른 입술 끝을 아래로 내려요', '👄👇')]),
    ('arm', '갑자기 한쪽 팔에 힘이 없어요', [('두 팔을 앞으로 들어요', '🙌'), ('한쪽 팔에 힘을 빼요', '💪👇'),
                                    ('한 쪽 어깨도 힘을 빼요', '🤷'), ('힘을 뺀 팔을 아래로 내려요', '✋⬇')]),
    ('chest', '가슴이 쥐어짜듯이 아파요', [('한 손을 가슴에 대요', '✋❤'), ('두 손으로 가슴을 꾹 눌러요', '🤲❤'),
                                  ('몸을 앞으로 숙여요', '🙇'), ('아픈 표정을 지어요', '😣')]),
    ('head', '갑자기 머리가 매우 아파요', [('한 손을 머리에 대요', '✋🤕'), ('두 손으로 머리를 잡아요', '🙌🤕'),
                                  ('눈을 찡그려요', '😖'), ('머리가 아프다고 말해요', '🤕💬')]),
]


def fit_label(im, text, sub=None):
    """아래쪽 종이 이름표. 글이 길면 글자를 줄이고, 그래도 길면 두 줄로 나눈다."""
    w, h = im.size
    d = ImageDraw.Draw(im)
    size = round(h * .07)
    lines = [text]
    while d.textlength(text, font=font(size)) > w * .84 and size > h * .05:
        size -= 2
    if d.textlength(text, font=font(size)) > w * .84:
        words = text.split(' ')
        cut = len(words) // 2
        lines = [' '.join(words[:cut]), ' '.join(words[cut:])]
    f = font(size)
    lh = round(size * 1.25)
    pad = round(h * .03)
    tw = max(d.textlength(t, font=f) for t in lines)
    sf = font(round(h * .038))
    bw = tw + pad * 4
    bh = lh * len(lines) + pad * 2 + (round(h * .05) if sub else 0)
    x0, y0 = (w - bw) / 2, h - bh - round(h * .045)
    d.rounded_rectangle((x0 + 4, y0 + 6, x0 + bw + 4, y0 + bh + 6), 14, fill=(200, 186, 166))
    d.rounded_rectangle((x0, y0, x0 + bw, y0 + bh), 14, fill=(255, 250, 240), outline=(216, 201, 179), width=3)
    y = y0 + pad
    if sub:
        sw = d.textlength(sub, font=sf)
        d.text(((w - sw) / 2, y - 4), sub, font=sf, fill=(185, 84, 60))
        y += round(h * .05)
    for t in lines:
        d.text(((w - d.textlength(t, font=f)) / 2, y - size * .12), t, font=f, fill=INK)
        y += lh
    return y0


def draw(out, text, emoji, sub=None, size=SIZE):
    w, h = size
    im = background(w, h, 'room').convert('RGBA')
    em = emoji_layer(emoji, round(h * .30))
    if em.width > w * .7:
        k = w * .7 / em.width
        em = em.resize((round(em.width * k), round(em.height * k)), Image.LANCZOS)
    cx, cy = w // 2, round(h * .36)
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((cx - em.width * .42, cy + em.height * .36, cx + em.width * .42, cy + em.height * .52), fill=(60, 40, 20, 70))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
    im.alpha_composite(em, (cx - em.width // 2, cy - em.height // 2))
    im = im.convert('RGB')
    fit_label(im, text, sub)
    im = stamp(im)
    im.save(out, 'JPEG', quality=83, optimize=True, progressive=True)


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True, exist_ok=True)
    for out, src in REAL:
        im = Image.open(SRC / src).convert('RGB')
        im.thumbnail((900, 900), Image.LANCZOS)
        im.save(OUT / out, 'JPEG', quality=83, optimize=True, progressive=True)
        print(out, '<-', src, '(진짜 사진)')
    man = []
    struct = '배경 거실(크림 벽·원목 바닥·창문·화분) / 가운데 이모지 그림 {e} / 이름표 「{t}」 / 오른쪽 위 빨간 「임시생성」 도장(짧은 변의 약 26%) / 1200×800px JPEG'
    # 두통 대표 그림(진짜 사진 없음)
    draw(OUT / 'head.jpg', '갑자기 머리가 매우 아파요', '🤕', size=(900, 900))  # 대표 사진은 정사각형으로 잘려 보이므로 정사각형
    man.append({'file': 'src/games/h4-1/img/head.jpg', 'desc': '갑자기 머리가 매우 아파 머리를 감싸 쥔 사람(증상 대표 사진)',
                'structure': struct.format(e='🤕', t='갑자기 머리가 매우 아파요').replace('1200×800', '900×900'),
                'used_in': '4번째 증상 「갑자기 머리가 매우 아파요」 소개 화면·결과 목록의 대표 사진'})
    print('head.jpg (임시)')
    for key, sym, steps in SYMS:
        for i, (t, e) in enumerate(steps, 1):
            name = f'{key}-{i}.jpg'
            draw(OUT / name, t, e, sub=f'{i}단계')
            man.append({'file': f'src/games/h4-1/img/{name}',
                        'desc': f'「{sym}」 따라 하기 {i}단계: {t} — 사람이 이 동작을 하는 사진',
                        'structure': struct.format(e=e, t=t) + ' / 이름표 위에 「' + f'{i}단계」',
                        'used_in': f'「{sym}」 {i}단계 화면의 동작 사진'})
            print(name, '(임시)')
    mf = ROOT / 'tools' / 'placeholder_manifest' / 'h4-1.json'
    mf.write_text(json.dumps(man, ensure_ascii=False, indent=2), encoding='utf-8')
    print(mf.relative_to(ROOT))


if __name__ == '__main__':
    main()

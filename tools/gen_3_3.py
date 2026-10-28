"""전3-3 「내 마음 표현하기」 임시 상황 그림 4장을 만든다. (마음·이유 보기는 화면 글자라 그림이 없다)
    python tools/gen_3_3.py
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from PIL import Image, ImageDraw, ImageFilter
from placeholder import background, emoji_layer, stamp

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'src/games/3-3/img'
SIZE = (1200, 800)


def pic(out, emoji, bg):
    """placeholder.scene과 같지만 결과 화면의 작은 썸네일에서도 보이게 그림을 크게(높이의 약 48%) 그린다."""
    w, h = SIZE
    im = background(w, h, bg).convert('RGBA')
    em = emoji_layer(emoji, round(h * .48))
    if em.width > w * .86:
        k = w * .86 / em.width
        em = em.resize((round(em.width * k), round(em.height * k)), Image.LANCZOS)
    cx, cy = w // 2, round(h * .52)
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((cx - em.width * .42, cy + em.height * .36, cx + em.width * .42, cy + em.height * .52), fill=(60, 40, 20, 70))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
    im.alpha_composite(em, (cx - em.width // 2, cy - em.height // 2))
    im = stamp(im.convert('RGB'), scale=1.15)
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, 'JPEG', quality=84, optimize=True, progressive=True)

IMGS = [
    ('sit-date.jpg', 'town', '💑', '상황 1: 여자친구·남자친구를 만났어요', '1번 상황 화면, 결과 화면'),
    ('sit-cancel.jpg', 'room', '📱📅❌', '상황 2: 약속이 취소되었어요(휴대폰으로 취소 연락을 받음)', '2번 상황 화면, 결과 화면'),
    ('sit-strange.jpg', 'town', '🗺️❓', '상황 3: 낯선 곳에 갔어요(지도를 보며 두리번거림)', '3번 상황 화면, 결과 화면'),
    ('sit-gift.jpg', 'room', '🎂🎁', '상황 4: 생일 선물을 받았어요', '4번 상황 화면, 결과 화면'),
]
BG = {'room': '방(크림색 벽·창문·원목 바닥·화분)', 'town': '동네 거리(하늘·건물)'}

man = []
for f, bg, em, desc, used in IMGS:
    pic(OUT / f, em, bg)
    print(f)
    man.append({'file': f'src/games/3-3/img/{f}', 'desc': desc,
                'structure': f'배경: {BG[bg]} / 가운데 그림: 이모지 {em}(높이의 약 48%로 크게) / 이름표: 없음(상황 문장은 게임 화면 글자로 보여 줌) / 도장: 오른쪽 위, 짧은 변의 약 30% 크기 / {SIZE[0]}×{SIZE[1]}px JPEG',
                'used_in': f'전3-3 {used}'})
(ROOT / 'tools/placeholder_manifest/3-3.json').write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding='utf-8')
print(len(man), 'images')

"""전3-1 「건강 빨간불을 초록불로 만들기」 임시 그림 20장을 만든다.
빨간불 행동 5장 + 초록불 보기 15장(문항마다 3장). 진짜 사진이 오면 같은 파일 이름으로 덮어쓰면 된다.
    python tools/gen_3_1.py
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from PIL import Image, ImageDraw, ImageFilter
from placeholder import background, emoji_layer, stamp

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'src/games/3-1/img'
SIZE = (960, 640)


def pic(out, emoji, bg):
    """placeholder.scene과 같지만 보기 카드(작은 썸네일)에서도 잘 보이게 그림을 크게(높이의 약 52%) 그린다."""
    w, h = SIZE
    im = background(w, h, bg).convert('RGBA')
    em = emoji_layer(emoji, round(h * .52))
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

# (파일, 배경, 이모지, 설명, 쓰는 곳)
IMGS = [
    # 1. 누워 있는 것을 좋아해요
    ('red-lie.jpg', 'bedroom', '🛌', '빨간불 행동: 누워 있는 것을 좋아해요', '1번 문제 빨간불 그림'),
    ('stretch.jpg', 'room', '🧘', '초록불 정답: 일어나서 스트레칭을 해요', '1번 문제 보기(정답), 결과 화면'),
    ('sofa-tv.jpg', 'room', '🛋️📺', '틀린 보기: 소파에 누워 텔레비전을 봐요', '1번 문제 보기(오답)'),
    ('sleep-all-day.jpg', 'bedroom', '😴', '틀린 보기: 하루 종일 잠만 자요', '1번 문제 보기(오답)'),
    # 2. 라면을 자주 먹어요
    ('red-ramen.jpg', 'kitchen', '🍜', '빨간불 행동: 라면을 자주 먹어요', '2번 문제 빨간불 그림'),
    ('rice-veg.jpg', 'kitchen', '🍚🥗', '초록불 정답: 밥과 채소 반찬을 먹어요', '2번 문제 보기(정답), 결과 화면'),
    ('ramen-two.jpg', 'kitchen', '🍜🍜', '틀린 보기: 라면을 두 개 끓여 먹어요', '2번 문제 보기(오답)'),
    ('snack-meal.jpg', 'kitchen', '🍪', '틀린 보기: 밥 대신 과자를 먹어요', '2번 문제 보기(오답)'),
    # 3. 탄산음료를 자주 마셔요
    ('red-soda.jpg', 'kitchen', '🥤', '빨간불 행동: 탄산음료를 자주 마셔요', '3번 문제 빨간불 그림'),
    ('water.jpg', 'kitchen', '🚰', '초록불 정답: 목마르면 물을 마셔요', '3번 문제 보기(정답), 결과 화면'),
    ('soda-more.jpg', 'kitchen', '🥤🥤', '틀린 보기: 탄산음료를 한 잔 더 마셔요', '3번 문제 보기(오답)'),
    ('juice.jpg', 'kitchen', '🧃', '틀린 보기: 달콤한 주스를 많이 마셔요', '3번 문제 보기(오답)'),
    # 4. 운동을 안 해요
    ('red-noexercise.jpg', 'room', '🛋️', '빨간불 행동: 운동을 안 해요', '4번 문제 빨간불 그림'),
    ('walk.jpg', 'outdoor', '🚶', '초록불 정답: 공원에서 걸어요', '4번 문제 보기(정답), 결과 화면'),
    ('game.jpg', 'room', '🎮', '틀린 보기: 하루 종일 게임만 해요', '4번 문제 보기(오답)'),
    ('sit-all-day.jpg', 'room', '🪑', '틀린 보기: 하루 종일 앉아만 있어요', '4번 문제 보기(오답)'),
    # 5. 밤늦게 음식을 먹어요
    ('red-latefood.jpg', 'kitchen', '🌙🍗', '빨간불 행동: 밤늦게 음식을 먹어요', '5번 문제 빨간불 그림'),
    ('early-dinner.jpg', 'kitchen', '🕖🍽️', '초록불 정답: 저녁을 일찍 먹어요', '5번 문제 보기(정답), 결과 화면'),
    ('chicken-night.jpg', 'kitchen', '🍗', '틀린 보기: 밤에 치킨을 시켜 먹어요', '5번 문제 보기(오답)'),
    ('pizza-bed.jpg', 'bedroom', '🍕', '틀린 보기: 자기 전에 피자를 먹어요', '5번 문제 보기(오답)'),
]
BG = {'room': '방(크림색 벽·창문·원목 바닥·화분)', 'bedroom': '침실(크림색 벽·창문·침대·원목 바닥)',
      'kitchen': '주방(크림색 벽·조리대·원목 바닥)', 'outdoor': '야외(하늘·나무·잔디)'}

man = []
for f, bg, em, desc, used in IMGS:
    pic(OUT / f, em, bg)
    print(f)
    man.append({'file': f'src/games/3-1/img/{f}', 'desc': desc,
                'structure': f'배경: {BG[bg]} / 가운데 그림: 이모지 {em}(높이의 약 52%로 크게) / 이름표: 없음(게임 화면 글자로 보여 줌) / 도장: 오른쪽 위, 짧은 변의 약 30% 크기 / {SIZE[0]}×{SIZE[1]}px JPEG',
                'used_in': f'전3-1 {used}'})
(ROOT / 'tools/placeholder_manifest/3-1.json').write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding='utf-8')
print(len(man), 'images')

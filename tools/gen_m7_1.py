"""중7-1 「우리집 위험 요소를 찾아보세요」 — 방 그림 4장과 '안전해진 모습' 스티커 9장을 만든다.
사용: python tools/gen_m7_1.py
  → src/games/m7-1/img/living.jpg, kitchen.jpg, bath.jpg, entrance.jpg   (진짜 그림, 도장 없음)
  → src/games/m7-1/img/safe-*.png                                       (임시 스티커, 「임시생성」 도장)
  → tools/placeholder_manifest/m7-1.json

방 그림은 원본 PNG(거실·주방·욕실·현관)를 긴 변 1200px JPEG로 줄인다.
요청서에는 '누르면 위험하지 않은 요소로 바뀐다'고 되어 있지만 안전한 상태 그림이 없어서,
위험 요소마다 '안전해진 모습' 스티커(투명 PNG: 흰 테두리 원 + 이모지 + 짧은 문구 + 초록 체크)를 그린다.
게임에서는 위험 요소를 누르면 그 자리에 스티커가 붙는다.
진짜 그림이 오면 같은 파일 이름(safe-*.png)으로 덮어쓰면 된다(투명 PNG, 정사각에 가깝게).
"""
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
from placeholder import emoji_layer, stamp, font, INK  # noqa: E402

SRC = next((ROOT / 'data').glob('나관엽*/나관엽*/중7-1 활용 그림'))
OUT = ROOT / 'src' / 'games' / 'm7-1' / 'img'
ROOMS = [('거실', 'living.jpg'), ('주방', 'kitchen.jpg'), ('욕실', 'bath.jpg'), ('현관', 'entrance.jpg')]

GREEN = (79, 122, 58)
PALE = (238, 245, 230)
W, H = 360, 400   # 스티커 크기(px)

# (파일, 이모지, 짧은 문구, 금지선 긋기, 방, 설명)
STICKERS = [
    ('safe-heater.png', '🔥', '히터 끔', True, '거실', '전기히터를 끄고 커튼에서 멀리 둔 모습'),
    ('safe-blanket.png', '🛏', '장판 끔', False, '거실', '전기장판을 펴고 전원을 끈 모습'),
    ('safe-pot.png', '🍲', '불 끔', False, '주방', '가스불을 끄고 냄비 옆을 지키는 모습'),
    ('safe-knife.png', '🔪', '칼꽂이에', False, '주방', '칼을 칼꽂이에 꽂아 정리한 모습'),
    ('safe-microwave.png', '🥣', '전용 그릇', False, '주방', '금속 그릇 대신 전자레인지용 그릇을 쓰는 모습'),
    ('safe-floor.png', '🧽', '물기 닦음', False, '화장실', '바닥의 물기를 닦아 낸 모습'),
    ('safe-dryer.png', '🔌', '코드 뺌', False, '화장실', '헤어드라이기 코드를 뽑고 물에서 멀리 둔 모습'),
    ('safe-door.png', '🔒', '문 잠금', False, '현관', '현관문을 닫고 잠근 모습'),
    ('safe-multitap.png', '⚡', '플러그 정리', True, '현관', '문어발 콘센트를 정리해 플러그를 줄인 모습'),
]


def sticker(emoji, text, slash):
    """흰 테두리 원형 스티커(투명 배경). 가운데 이모지, 아래 문구 띠, 오른쪽 아래 초록 체크."""
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    cx, cy, r = W // 2, 172, 150
    # 그림자
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((cx - r + 4, cy - r + 10, cx + r + 4, cy + r + 10), fill=(40, 30, 20, 90))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    d = ImageDraw.Draw(im)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 255, 255, 255))
    d.ellipse((cx - r + 14, cy - r + 14, cx + r - 14, cy + r - 14), fill=PALE + (255,), outline=GREEN + (255,), width=6)
    em = emoji_layer(emoji, 150)
    k = min(190 / em.width, 170 / em.height)
    em = em.resize((round(em.width * k), round(em.height * k)), Image.LANCZOS)
    im.alpha_composite(em, (cx - em.width // 2, cy - 20 - em.height // 2))
    if slash:  # '끔·정리'를 금지 표시로 보여 준다
        rr = 92
        d.ellipse((cx - rr, cy - 20 - rr, cx + rr, cy - 20 + rr), outline=(205, 60, 50, 235), width=14)
        d.line([(cx - rr * .7, cy - 20 + rr * .7), (cx + rr * .7, cy - 20 - rr * .7)], fill=(205, 60, 50, 235), width=14)
    # 문구 띠
    f = font(52)
    tw = d.textlength(text, font=f)
    bw = max(tw + 44, 200)
    by = cy + r - 64
    d.rounded_rectangle((cx - bw / 2 + 3, by + 5, cx + bw / 2 + 3, by + 72 + 5), 20, fill=(40, 30, 20, 70))
    d.rounded_rectangle((cx - bw / 2, by, cx + bw / 2, by + 72), 20, fill=(255, 250, 240, 255), outline=GREEN + (255,), width=4)
    d.text((cx - tw / 2, by + 2), text, font=f, fill=INK)
    # 초록 체크 배지
    bx, byy, br = cx + r - 34, cy - r + 40, 40
    d.ellipse((bx - br - 5, byy - br - 5, bx + br + 5, byy + br + 5), fill=(255, 255, 255, 255))
    d.ellipse((bx - br, byy - br, bx + br, byy + br), fill=GREEN + (255,))
    d.line([(bx - 20, byy + 2), (bx - 5, byy + 17), (bx + 21, byy - 15)], fill=(255, 255, 255, 255), width=10, joint='curve')
    # 작은 「임시생성」 도장(왼쪽 위, 잘 보이게 흰 바탕 위에)
    d.ellipse((6, 6, 110, 110), fill=(255, 255, 255, 235))
    return stamp(im, scale=1.0, pos=(1, 1))


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True, exist_ok=True)
    for ko, name in ROOMS:
        im = Image.open(SRC / f'{ko}.png').convert('RGB')
        im.thumbnail((1200, 1200), Image.LANCZOS)
        im.save(OUT / name, 'JPEG', quality=83, optimize=True, progressive=True)
        print(f'{name}\t{im.size}\t{(OUT / name).stat().st_size // 1024}KB (진짜 그림)')
    man = []
    for name, emoji, text, slash, room, desc in STICKERS:
        im = sticker(emoji, text, slash)
        im.save(OUT / name, 'PNG', optimize=True)
        print(f'{name}\t{(OUT / name).stat().st_size // 1024}KB (임시)')
        man.append({
            'file': f'src/games/m7-1/img/{name}',
            'desc': f'안전해진 모습 스티커: {desc}',
            'structure': f'투명 배경 / 흰 테두리 원(연초록 바탕·초록 테두리) / 가운데 이모지 {emoji}'
                         f'{"(빨간 금지선)" if slash else ""} / 아래 문구 띠 「{text}」 / 오른쪽 위 초록 체크 배지 / '
                         f'왼쪽 위 작은 빨간 「임시생성」 도장 / {W}×{H}px PNG',
            'used_in': f'중7-1 {room} 장면 — 위험 요소를 누르면 그 자리에 붙는 스티커',
        })
    mf = ROOT / 'tools' / 'placeholder_manifest' / 'm7-1.json'
    mf.write_text(json.dumps(man, ensure_ascii=False, indent=2), encoding='utf-8')
    print(mf.relative_to(ROOT))


if __name__ == '__main__':
    main()

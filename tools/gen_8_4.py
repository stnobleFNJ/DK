"""전8-4 「나와 맞는 행사 찾기」 — 행사 포스터 사진 10장을 세로 사진으로 잘라 저장한다.
사용: python tools/gen_8_4.py   → src/games/8-4/img/ev01.jpg … ev10.jpg, tools/placeholder_manifest/8-4.json

원본: data/_1102/게임(전기2,8단원)/게임/8-4 우리 동네 함께 즐기기/*.png
  1920×1080 흰 바탕 가운데에 세로 사진(약 768×1080)이 있다 → 흰 여백을 잘라 768×1080 JPEG로 저장.
  사진에는 글자가 없다. 날짜·시간·장소·계절·준비물은 교재 92쪽 행사 카드에서 가져와 index.html에 적었다.

단풍길 러닝 페스타.png는 압축 파일에서부터 512KB에서 잘려(손상) 위쪽 약 40%만 남아 있다.
  → 남은 진짜 단풍 부분을 위에 두고, 아래는 단풍길·달리는 사람 이모지를 그려 채운 뒤 「임시생성」 도장을 찍는다.
  온전한 원본이 오면 이 스크립트를 다시 실행하면 진짜 사진으로 바뀐다(손상 여부를 스스로 검사한다).
  그때 매니페스트 8-4.json도 지운다.
"""
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFile, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
from placeholder import emoji_layer, stamp, _vgrad  # noqa: E402

SRC = next((ROOT / 'data' / '_1102' / '게임(전기2,8단원)' / '게임').glob('8-4*'))
OUT = ROOT / 'src' / 'games' / '8-4' / 'img'
MANIFEST = ROOT / 'tools' / 'placeholder_manifest' / '8-4.json'
BOX = (576, 0, 1344, 1080)   # 세로 사진 부분

# 파일 번호는 교재 92쪽 카드 번호와 같다.
FILES = [
    ('ev01.jpg', '별빛 재즈 나이트'), ('ev02.jpg', '도시 책 산책'), ('ev03.jpg', '한여름 워터 나이트'),
    ('ev04.jpg', '설빛 얼음왕국'), ('ev05.jpg', '호박빛 나이트 퍼레이드'), ('ev06.jpg', '벚꽃 버스킹 데이'),
    ('ev07.jpg', '단풍길 러닝 페스타'), ('ev08.jpg', '윈터 마켓 빛축제'), ('ev09.jpg', '오늘의 아트 산책'),
    ('ev10.jpg', '서울 패션 위크'),
]


def is_broken(p):
    try:
        Image.open(p).load()
        return False
    except OSError:
        return True


def patch_marathon(p):
    """손상된 단풍길 사진: 남은 위쪽 진짜 사진 + 아래쪽 그림 + 도장."""
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    try:
        src = Image.open(p).convert('RGB').crop(BOX)
    finally:
        ImageFile.LOAD_TRUNCATED_IMAGES = False
    w, h = src.size
    # 남은 줄 찾기: 아래에서부터 검은(빈) 줄을 건너뛴다
    px = src.load()
    keep = h
    while keep > 0 and all(px[x, keep - 1] == (0, 0, 0) for x in range(0, w, 16)):
        keep -= 1
    keep = max(0, keep - 6)
    im = Image.new('RGB', (w, h))
    d = ImageDraw.Draw(im)
    _vgrad(d, (0, keep - 60, w, h), (196, 120, 80), (150, 104, 76))           # 단풍 그늘
    d.polygon([(w * .28, keep), (w * .72, keep), (w * 1.05, h), (-w * .05, h)], fill=(176, 168, 160))  # 길
    d.polygon([(w * .47, keep), (w * .53, keep), (w * .56, h), (w * .44, h)], fill=(214, 206, 196))
    for i in range(160):  # 떨어진 잎
        x, y = (i * 97) % w, keep + (i * 53) % (h - keep)
        r = 4 + i % 5
        d.ellipse((x - r, y - r, x + r, y + r), fill=[(214, 74, 40), (236, 140, 40), (190, 50, 34)][i % 3])
    im = im.filter(ImageFilter.GaussianBlur(1.2))
    # 진짜 사진 아래 끝 60px을 점점 투명하게 겹쳐 이음매를 부드럽게
    top = src.crop((0, 0, w, keep))
    mask = Image.new('L', top.size, 255)
    md = ImageDraw.Draw(mask)
    for i in range(60):
        md.line([(0, keep - 60 + i), (w, keep - 60 + i)], fill=round(255 * (1 - i / 60)))
    im.paste(top, (0, 0), mask)
    im = im.convert('RGBA')
    em = emoji_layer('🏃🏃🏃', round(h * .14))
    im.alpha_composite(em, ((w - em.width) // 2, round(h * .66) - em.height // 2))
    # 도장은 회색 길 위(오른쪽 아래)에 찍어 잘 보이게
    return stamp(im.convert('RGB'), scale=1.1, pos=(round(w * .5), round(h * .76)))


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True, exist_ok=True)
    man = []
    for name, title in FILES:
        p = SRC / f'{title}.png'
        out = OUT / name
        if is_broken(p):
            im = patch_marathon(p)
            man.append({
                'file': f'src/games/8-4/img/{name}',
                'desc': f'「{title}」 포스터 사진(원본 PNG가 잘려 손상됨) — 단풍길 마라톤 대회',
                'structure': '위 약 40%: 원본에 남아 있는 진짜 단풍 나무 사진 / 아래: 그려 넣은 단풍 그늘·회색 길·떨어진 잎 + '
                             '달리는 사람 이모지 🏃🏃🏃 / 오른쪽 위 빨간 「임시생성」 도장 / 768×1080px JPEG',
                'used_in': '행사 7번 단풍길 러닝 페스타 — 추천 카드, 포스터 크게 보기, 행사 목록, 소개 카드',
            })
            tag = '손상 → 임시 보정'
        else:
            im = Image.open(p).convert('RGB').crop(BOX)
            tag = '진짜 사진'
        im.save(out, 'JPEG', quality=83, optimize=True, progressive=True)
        print(f'{name}\t{title}\t{tag}\t{out.stat().st_size // 1024}KB')
    if man:
        MANIFEST.write_text(json.dumps(man, ensure_ascii=False, indent=2), encoding='utf-8')
        print(MANIFEST.relative_to(ROOT))
    elif MANIFEST.exists():
        MANIFEST.unlink()
        print('매니페스트 삭제(임시 그림 없음)')


if __name__ == '__main__':
    main()

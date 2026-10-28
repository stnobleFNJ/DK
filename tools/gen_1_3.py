"""전1-3 「내일 계획 만들기」 활동 사진 16장(아직 없음)을 임시 일러스트로 만든다.
사용: python tools/gen_1_3.py   → src/games/1-3/img/act-*.jpg, tools/placeholder_manifest/1-3.json
진짜 사진이 오면 같은 파일 이름으로 덮어쓰면 된다. 주제 표지(theme-*.jpg)와 첫 화면(start.jpg)은
실제 사진이므로 optimize_images.py 1-3 으로 만든다.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
from placeholder import scene  # noqa: E402

OUT = ROOT / 'src' / 'games' / '1-3' / 'img'
SIZE = (1200, 800)
BGNAME = {'room': '거실(크림 벽·원목 바닥·창문·화분)', 'kitchen': '부엌(크림 벽·조리대·원목 바닥)',
          'bedroom': '침실(크림 벽·침대·원목 바닥)', 'outdoor': '야외(하늘·나무·잔디·산책길)',
          'town': '동네 거리(하늘·건물)', 'bath': '욕실(타일)', 'paper': '종이'}

# (파일, 활동 이름, 이모지, 배경, 주제, 콜라주에 있는 활동인지)
ITEMS = [
    ('act-meal.jpg', '밥 먹기', '🍚', 'kitchen', '나를 돌봐요', True),
    ('act-walk.jpg', '산책하기', '🚶', 'outdoor', '나를 돌봐요', True),
    ('act-sleep.jpg', '푹 자기', '😴', 'bedroom', '나를 돌봐요', True),
    ('act-stretch.jpg', '스트레칭', '🧘', 'room', '나를 돌봐요', False),
    ('act-cafe.jpg', '카페 가기', '☕', 'town', '사람들과 함께 해요', True),
    ('act-family.jpg', '가족과 식사', '👪', 'kitchen', '사람들과 함께 해요', True),
    ('act-program.jpg', '지역 프로그램', '🏫', 'room', '사람들과 함께 해요', True),
    ('act-call.jpg', '친구와 전화', '📞', 'room', '사람들과 함께 해요', False),
    ('act-market.jpg', '장보기', '🛒', 'town', '내 생활을 챙겨요', True),
    ('act-laundry.jpg', '빨래하기', '🧺', 'room', '내 생활을 챙겨요', True),
    ('act-clean.jpg', '청소하기', '🧹', 'room', '내 생활을 챙겨요', True),
    ('act-dishes.jpg', '설거지하기', '🍽️', 'kitchen', '내 생활을 챙겨요', False),
    ('act-movie.jpg', '영화 보기', '🍿', 'town', '내가 하고 싶은 일을 해요', True),
    ('act-karaoke.jpg', '노래방 가기', '🎤', 'town', '내가 하고 싶은 일을 해요', True),
    ('act-camping.jpg', '캠핑하기', '⛺', 'outdoor', '내가 하고 싶은 일을 해요', True),
    ('act-draw.jpg', '그림 그리기', '🎨', 'room', '내가 하고 싶은 일을 해요', False),
]


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    man = []
    for name, text, emoji, bg, theme, real in ITEMS:
        out = OUT / name
        scene(out, None, emoji, bg, size=SIZE)
        print(f'{out.relative_to(ROOT)}\t{out.stat().st_size // 1024}KB')
        src = (f'콜라주 「{theme}」에 나오는 활동 — 콜라주를 자르거나 낱장 사진으로 교체'
               if real else '콜라주에 없는 네 번째 활동(임시로 정함) — 활동을 확정한 뒤 사진 교체')
        man.append({
            'file': f'src/games/1-3/img/{name}',
            'desc': f'「{theme}」 주제의 활동 「{text}」 사진 대용 그림. {src}',
            'structure': f'배경: {BGNAME[bg]} / 가운데 그림: 이모지 {emoji} (그림자 포함) / 이름표: 없음(활동 이름은 화면 글자로 표시) '
                         f'/ 도장: 오른쪽 위, 짧은 변의 26% 크기 빨간 원형 「임시생성」 / {SIZE[0]}×{SIZE[1]}px JPEG',
            'used_in': f'주제 고르기 화면 「{theme}」의 활동 카드, 결과 화면 「나의 내일은?」의 작은 사진',
        })
    mp = ROOT / 'tools' / 'placeholder_manifest' / '1-3.json'
    mp.parent.mkdir(parents=True, exist_ok=True)
    mp.write_text(json.dumps(man, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(mp.relative_to(ROOT), len(man))


if __name__ == '__main__':
    main()

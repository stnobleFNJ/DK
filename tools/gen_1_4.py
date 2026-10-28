"""전1-4 「내가 원하는 프로그램 고르기」 이미지(모두 없음)를 임시 일러스트로 만든다.
사용: python tools/gen_1_4.py   → src/games/1-4/img/*.jpg, tools/placeholder_manifest/1-4.json
프로그램 10개의 이름은 아직 정해지지 않아 임시로 정했다. 진짜 사진이 오면 같은 파일 이름으로 덮어쓰면 된다.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
from placeholder import scene  # noqa: E402

OUT = ROOT / 'src' / 'games' / '1-4' / 'img'
SIZE = (1200, 800)
BGNAME = {'room': '거실(크림 벽·원목 바닥·창문·화분)', 'kitchen': '부엌(크림 벽·조리대·원목 바닥)',
          'bedroom': '침실(크림 벽·침대·원목 바닥)', 'outdoor': '야외(하늘·나무·잔디·산책길)',
          'town': '동네 거리(하늘·건물)', 'bath': '욕실(타일)', 'paper': '종이'}

# (파일, 프로그램 이름, 이모지, 배경) — 프로그램 이름은 모두 임시
PROGRAMS = [
    ('prog-cook.jpg', '요리 교실', '🍳', 'kitchen'),
    ('prog-art.jpg', '미술 교실', '🎨', 'room'),
    ('prog-exercise.jpg', '건강 체조', '🤸', 'room'),
    ('prog-sing.jpg', '노래 교실', '🎤', 'room'),
    ('prog-computer.jpg', '컴퓨터 교실', '💻', 'room'),
    ('prog-garden.jpg', '원예 교실', '🌱', 'outdoor'),
    ('prog-book.jpg', '책 읽기 모임', '📚', 'room'),
    ('prog-dance.jpg', '댄스 교실', '💃', 'room'),
    ('prog-photo.jpg', '사진 교실', '📷', 'outdoor'),
    ('prog-bowling.jpg', '볼링', '🎳', 'town'),
]


def entry(name, desc, emoji, bg, used):
    return {
        'file': f'src/games/1-4/img/{name}',
        'desc': desc,
        'structure': f'배경: {BGNAME[bg]} / 가운데 그림: 이모지 {emoji} (그림자 포함) / 이름표: 없음(이름은 화면 글자로 표시) '
                     f'/ 도장: 오른쪽 위, 짧은 변의 26% 크기 빨간 원형 「임시생성」 / {SIZE[0]}×{SIZE[1]}px JPEG',
        'used_in': used,
    }


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    man = []
    out = OUT / 'start.jpg'
    scene(out, None, '📅✏️', 'room', size=SIZE)
    print(f'{out.relative_to(ROOT)}\t{out.stat().st_size // 1024}KB')
    man.append(entry('start.jpg', '첫 화면 표지 그림: 일주일 시간표(달력)와 연필 — 수강신청을 시작하는 장면 대용',
                     '📅✏️', 'room', '첫 화면 표지 사진'))
    for name, text, emoji, bg in PROGRAMS:
        out = OUT / name
        scene(out, None, emoji, bg, size=SIZE)
        print(f'{out.relative_to(ROOT)}\t{out.stat().st_size // 1024}KB')
        man.append(entry(name, f'프로그램 「{text}」(이름 임시) 사진 대용 그림 — 프로그램 목록이 정해지면 사진 교체',
                         emoji, bg, '프로그램 고르기 카드, 시간표 칸의 작은 사진, 결과 시간표 「내 프로그램 내 손으로」'))
    mp = ROOT / 'tools' / 'placeholder_manifest' / '1-4.json'
    mp.parent.mkdir(parents=True, exist_ok=True)
    mp.write_text(json.dumps(man, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(mp.relative_to(ROOT), len(man))


if __name__ == '__main__':
    main()

"""전5-2 「우리집 한바퀴」 — 빠진 '알맞은 행동' 그림 5장을 임시 일러스트로 만든다.
사용: python tools/gen_5_2.py   → src/games/5-2/img/q*-good.jpg, sp-*.jpg, tools/placeholder_manifest/5-2.json

거실·주방·화장실 칸(1·3·4·6·8)은 '알맞지 않은 행동' 사진만 있어서, 알맞은 행동 그림을 임시로 그린다.
진짜 사진이 오면 같은 파일 이름(q1-good.jpg …)으로 덮어쓰면 된다.
보드판·상황 사진은 실제 사진이므로 optimize_images.py 5-2 로 만든다.
sp-*.jpg(칸 공간 사진)는 실제 보드판에서 잘라 낸 것이라 도장을 찍지 않는다.
"""
import json
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
from placeholder import scene  # noqa: E402

OUT = ROOT / 'src' / 'games' / '5-2' / 'img'
BOARD = ROOT / 'data' / '큐알활동사진_생애주기_전기_1,5,6,7단원' / '5-2 우리집공간사용법' / '1. 우리집 한바퀴 생활공간 보드.png'
SIZE = (1200, 675)
BGNAME = {'room': '거실(크림 벽·원목 바닥·창문·화분)', 'kitchen': '주방(크림 벽·조리대·원목 바닥)',
          'bath': '화장실(타일 벽·바닥)', 'bedroom': '침실'}

# (파일, 이름표, 이모지, 배경, 칸, 설명)
ITEMS = [
    ('q1-good.jpg', '소파를 함께 나눠 앉기', '👪🛋', 'room', '1번 칸 거실',
     '거실 소파에 가족이 자리를 나눠 함께 앉는 모습(알맞은 행동)'),
    ('q3-good.jpg', '식탁 위 내 물건 치우기', '🎒📚👉🚪', 'kitchen', '3번 칸 주방(식탁)',
     '식탁 위에 둔 가방과 책을 내 방으로 치우는 모습(알맞은 행동)'),
    ('q4-good.jpg', '이어폰으로 음악 듣기', '🙂🎧🎵', 'room', '4번 칸 거실',
     '거실에서 이어폰을 끼고 조용히 음악을 듣는 모습(알맞은 행동)'),
    ('q6-good.jpg', '화장실 빨리 쓰고 나오기', '🚽⏱👍', 'bath', '6번 칸 화장실',
     '화장실을 짧게 쓰고 다음 사람을 위해 나오는 모습(알맞은 행동)'),
    ('q8-good.jpg', '식사 후 그릇 치우기', '🍽🧽✨', 'kitchen', '8번 칸 주방(식탁)',
     '밥을 다 먹고 그릇을 싱크대로 옮겨 치우는 모습(알맞은 행동)'),
]

# 보드판(1672×941)에서 칸 그림 부분을 잘라 문제 화면 머리 사진으로 쓴다(실제 사진, 도장 없음)
CROPS = [('sp-living.jpg', (362, 238, 646, 462)), ('sp-room.jpg', (702, 238, 980, 462)),
         ('sp-kitchen.jpg', (1033, 238, 1317, 462)), ('sp-bath.jpg', (363, 648, 647, 874))]


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True, exist_ok=True)
    board = Image.open(BOARD).convert('RGB')
    for name, box in CROPS:
        board.crop(box).save(OUT / name, 'JPEG', quality=84, optimize=True)
        print(f'{name}\t(보드판 자르기)')
    man = []
    for name, text, emoji, bg, cell, desc in ITEMS:
        out = OUT / name
        scene(out, text, emoji, bg, size=SIZE)
        print(f'{out.relative_to(ROOT)}\t{out.stat().st_size // 1024}KB')
        man.append({
            'file': f'src/games/5-2/img/{name}',
            'desc': desc,
            'structure': f'배경 {BGNAME[bg]} / 가운데 이모지 그림 {emoji} / 이름표 「{text}」 / '
                         f'오른쪽 위 빨간 「임시생성」 도장(짧은 변의 약 26%) / {SIZE[0]}×{SIZE[1]}px JPEG',
            'used_in': f'{cell} 문제 — 행동 보기 2장 중 정답(알맞은 행동) 그림',
        })
    mf = ROOT / 'tools' / 'placeholder_manifest' / '5-2.json'
    mf.parent.mkdir(parents=True, exist_ok=True)
    mf.write_text(json.dumps(man, ensure_ascii=False, indent=2), encoding='utf-8')
    print(mf.relative_to(ROOT))


if __name__ == '__main__':
    main()

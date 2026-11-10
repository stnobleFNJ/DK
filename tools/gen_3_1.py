"""전3-1 「건강 빨간불을 초록불로 만들기」 실제 사진 20장을 게임용 JPEG로 만든다.
사용: python tools/gen_3_1.py   → src/games/3-1/img/q1-red.jpg … q5-g3.jpg

원본: data/_1102/게임(전기3,4단원)/게임(전기3,4)/전3-1 건강 습관 점검하기/
  건강 빨간불 행동N/<문장>.png                    → qN-red.jpg
  건강 초록불 행동N(빨간불 행동N과 연결)/<문장>.png → qN-g1.jpg(정답) · qN-g2.jpg · qN-g3.jpg
원본 파일 이름이 곧 화면 문장이다(‘(정답)’ 표시는 정답 파일 고르기에만 쓴다).
원본은 1672×941 PNG(사진). 비율은 그대로 두고 긴 변 1200px, JPEG quality 83으로 줄인다. 도장은 찍지 않는다.
여러 번 실행해도 같은 결과가 나온다.
"""
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'data' / '_1102' / '게임(전기3,4단원)' / '게임(전기3,4)' / '전3-1 건강 습관 점검하기'
OUT = ROOT / 'src' / 'games' / '3-1' / 'img'
MAXW = 1200

# 문항별: (빨간불 문장, [초록불 정답, 오답, 오답]) — 원본 파일 이름 앞부분으로 찾는다(점·공백 차이 무시)
Q = [
    ('누워있는 것을 좋아해요', ['몸을 움직여요', '천천히 오래 씹어 먹어요', '물을 자주 마셔요']),
    ('라면을 자주 먹어요', ['라면은 일주일에 한 번만 먹어요', '밤 늦게까지 휴대폰을 보지 않아요', '밥을 먹고 산책해요']),
    ('탄산음료를 자주 마셔요', ['물을 하루에 6~8잔 마셔요', '밤 12시 전에 자요', '자전거를 타요']),
    ('운동을 안 해요', ['매일 30분 이상 운동해요', '채소와 과일을 먹어요', '아침에 일찍 일어나요']),
    ('밤 늦게 음식을 먹어요', ['잠자기 전에는 음식을 먹지 않아요', '낮잠을 오래 자지 않아요', '가까운 거리는 걸어가요']),
]


def find(folder_prefix, text):
    dirs = [d for d in SRC.iterdir() if d.is_dir() and d.name.startswith(folder_prefix)]
    assert len(dirs) == 1, (folder_prefix, dirs)
    hits = [p for p in dirs[0].glob('*.png') if p.stem.rstrip('.').startswith(text)]
    assert len(hits) == 1, (text, hits)
    return hits[0]


def save(src, out):
    im = Image.open(src).convert('RGB')
    if max(im.size) > MAXW:
        k = MAXW / max(im.size)
        im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    im.save(out, 'JPEG', quality=83, optimize=True, progressive=True)
    print(f'{out.name}\t{im.width}x{im.height}\t{out.stat().st_size // 1024}KB\t{src.name}')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True, exist_ok=True)
    for n, (red, greens) in enumerate(Q, 1):
        save(find(f'건강 빨간불 행동{n}', red), OUT / f'q{n}-red.jpg')
        for k, g in enumerate(greens, 1):
            p = find(f'건강 초록불 행동{n}', g)
            assert ('(정답)' in p.name) == (k == 1), p   # 첫째가 정답 파일인지 확인
            save(p, OUT / f'q{n}-g{k}.jpg')


if __name__ == '__main__':
    main()

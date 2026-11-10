"""전3-3 「내 마음 표현하기」 실제 사진 36장(상황 4 · 마음 16 · 이유 16)을 게임용 JPEG로 만든다.
사용: python tools/gen_3_3.py   → src/games/3-3/img/s1-sit.jpg, s1-f1.jpg … s4-w4.jpg

원본: data/_1102/게임(전기3,4단원)/게임(전기3,4)/전3-3 오늘의 마음 살펴보기/<상황>/{상황,감정,이유}/<문장>.png
  상황 → sN-sit.jpg, 감정 → sN-f1~f4.jpg, 이유 → sN-w1~w4.jpg (번호 순서 = 「사진 적용시 참고 사항」의 보기 순서)
원본은 1672×941 PNG(사진). 비율은 그대로 두고 긴 변 1200px, JPEG quality 83으로 줄인다. 도장은 찍지 않는다.
여러 번 실행해도 같은 결과가 나온다.
"""
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'data' / '_1102' / '게임(전기3,4단원)' / '게임(전기3,4)' / '전3-3 오늘의 마음 살펴보기'
OUT = ROOT / 'src' / 'games' / '3-3' / 'img'
MAXW = 1200

# (원본 상황 폴더, 상황 문장, 마음 4개, 이유 4개) — 원본 파일 이름 앞부분으로 찾는다(점·공백 차이 무시)
S = [
    ('여자친구를 만났어요', '여자친구를 만났어요',
     ['기뻐요', '설레요', '긴장돼요', '미안해요'],
     ['오랜만에 만나서요', '함께 놀러 갈 거라서요', '무슨 말을 해야 할지 몰라서요', '약속 시간에 늦어서요']),
    ('약속이 취소 되었어요', '약속이 취소되었어요',
     ['슬퍼요', '실망스러워요', '속상해요', '짜증 나요'],
     ['보고 싶었던 사람을 못 만나서요', '함께 놀러 가기로 했는데 못 가서요', '나갈 준비를 다 했는데 못 만나게 돼서요', '미리 말하지 않고 갑자기 취소해서요']),
    ('낯선 곳에 갔어요', '낯선 곳에 갔어요',
     ['설레요', '긴장돼요', '무서워요', '걱정돼요'],
     ['새로운 것을 구경할 수 있어서요', '어디로 가야 할지 몰라서요', '길을 잃을까 봐요', '집으로 돌아가는 길을 몰라서요']),
    ('생일 선물을 받았어요', '생일 선물을 받았어요',
     ['기뻐요', '고마워요', '궁금해요', '실망스러워요'],
     ['갖고 싶었던 선물을 받아서요', '내 생일을 기억하고 선물을 준비해 줘서요', '포장 안에 무엇이 들어 있는지 몰라서요', '내가 좋아하는 선물이 아니라서요']),
]


def find(folder, text):
    hits = [p for p in folder.glob('*.png') if p.stem.rstrip('.').replace(' ', '') == text.replace(' ', '')]
    assert len(hits) == 1, (folder, text, hits)
    return hits[0]


def save(src, out):
    im = Image.open(src).convert('RGB')
    if max(im.size) > MAXW:
        k = MAXW / max(im.size)
        im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    im.save(out, 'JPEG', quality=83, optimize=True, progressive=True)
    print(f'{out.name}\t{im.width}x{im.height}\t{out.stat().st_size // 1024}KB\t{src.parent.parent.name}/{src.parent.name}/{src.name}')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True, exist_ok=True)
    for n, (folder, sit, feels, whys) in enumerate(S, 1):
        d = SRC / folder
        save(find(d / '상황', sit), OUT / f's{n}-sit.jpg')
        for k, t in enumerate(feels, 1):
            save(find(d / '감정', t), OUT / f's{n}-f{k}.jpg')
        for k, t in enumerate(whys, 1):
            save(find(d / '이유', t), OUT / f's{n}-w{k}.jpg')


if __name__ == '__main__':
    main()

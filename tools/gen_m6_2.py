"""중6-2 「내가 살고 싶은 집(주거 이상형 월드컵)」 — 문구 ①~⑫ 그림 12장을 줄여 저장한다.
사용: python tools/gen_m6_2.py   → src/games/m6-2/img/h01.jpg … h12.jpg (12장)

원본: data/나관엽 - 게임 참고자료 (10.26)/…/중6-2 활용 그림/<유형> <①~⑫> <문구>  <다른 문구>.png (1448×1086)
파일 이름의 동그라미 숫자(①~⑫)로 찾아 hNN.jpg로 저장한다. 보기 24개는 index.html에서 이 12장을 다시 쓴다.
모두 실제 그림이므로 임시 그림·도장은 없다. 자르지 않고 긴 변 1200px로만 줄인다.
다시 실행해도 같은 결과가 나온다.
"""
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'data' / '나관엽 - 게임 참고자료 (10.26)' / '나관엽 - 게임 참고자료 (10.26)' / '중6-2 활용 그림'
OUT = ROOT / 'src' / 'games' / 'm6-2' / 'img'
LONG = 1200
QUALITY = 83
CIRCLED = '①②③④⑤⑥⑦⑧⑨⑩⑪⑫'


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True, exist_ok=True)
    files = sorted(SRC.glob('*.png'))
    for i, c in enumerate(CIRCLED, 1):
        hits = [f for f in files if f' {c} ' in f.name]
        if len(hits) != 1:
            raise SystemExit(f'원본을 찾지 못함: {c} → {hits}')
        im = Image.open(hits[0]).convert('RGB')
        s = LONG / max(im.size)
        if s < 1:
            im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        out = OUT / f'h{i:02d}.jpg'
        im.save(out, 'JPEG', quality=QUALITY, optimize=True, progressive=True)
        print(f'{out.relative_to(ROOT)}\t{im.size[0]}×{im.size[1]}\t{out.stat().st_size // 1024}KB\t← {hits[0].name}')
    print(len(CIRCLED), '장')


if __name__ == '__main__':
    main()

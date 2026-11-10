"""후3-1 「나에게 맞는 도움 고르기」 — 주제 그림 8장을 줄이고, 각 그림의 2×2 칸을 잘라 선택지 그림 32장을 만든다.
사용: python tools/gen_h3_1.py   → src/games/h3-1/img/<주제>.jpg, <주제>-1.jpg … <주제>-4.jpg

원본: data/_1102/후기 게임자료/게임개발/후 3-1/<주제>.png (1536×1024, 흰 줄로 나뉜 2×2 그림)
- 「삽화_32장_검토용.jpg」(300×200칸)와 같은 그림이 주제 그림 안에 더 크게(약 760×500) 들어 있어 주제 그림에서 자른다.
- 칸 순서: 왼쪽 위 1, 오른쪽 위 2, 왼쪽 아래 3, 오른쪽 아래 4 (검토용 시트의 줄 순서와 같다)
- 흰 칸막이는 그림마다 몇 px씩 달라서 밝은 줄을 찾아 자른다.
진짜 그림이므로 도장을 찍지 않는다.
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'data' / '_1102' / '후기 게임자료' / '게임개발' / '후 3-1'
OUT = ROOT / 'src' / 'games' / 'h3-1' / 'img'
TOPICS = [('dress', '옷 입기'), ('medicine', '약 복용'), ('hospital', '병원 가기'), ('meal', '식사 지원'),
          ('clean', '청소와 빨래'), ('outing', '외출'), ('health', '건강한 생활'), ('alone', '혼자 있을 때')]
Q = 83


def gutter(profile, lo, hi):
    """lo~hi 사이에서 평균 밝기가 235를 넘는 줄(흰 칸막이)의 처음과 끝."""
    idx = [i for i in range(lo, hi) if profile[i] > 235]
    if not idx:
        raise SystemExit(f'칸막이를 못 찾음 ({lo}~{hi})')
    return idx[0], idx[-1]


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True, exist_ok=True)
    for key, name in TOPICS:
        im = Image.open(SRC / f'{name}.png').convert('RGB')
        w, h = im.size
        a = np.asarray(im.convert('L')).astype(int)
        c0, c1 = gutter(a.mean(0), w // 2 - 120, w // 2 + 120)
        r0, r1 = gutter(a.mean(1), h // 2 - 120, h // 2 + 120)
        m = 3  # 칸막이 가장자리의 흐린 줄을 조금 더 깎는다
        boxes = [(0, 0, c0 - m, r0 - m), (c1 + 1 + m, 0, w, r0 - m),
                 (0, r1 + 1 + m, c0 - m, h), (c1 + 1 + m, r1 + 1 + m, w, h)]
        t = im.copy()
        t.thumbnail((1200, 1200), Image.LANCZOS)
        t.save(OUT / f'{key}.jpg', 'JPEG', quality=Q, optimize=True, progressive=True)
        for i, b in enumerate(boxes, 1):
            im.crop(b).save(OUT / f'{key}-{i}.jpg', 'JPEG', quality=Q, optimize=True, progressive=True)
        print(f'{key}\t{name}\t칸막이 x{c0}-{c1} y{r0}-{r1}')


if __name__ == '__main__':
    main()

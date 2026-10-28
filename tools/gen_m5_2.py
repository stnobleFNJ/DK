"""중5-2 「나의 권리 말판 게임」 — 원본 그림을 잘라 게임용 JPEG로 만든다.
사용: python tools/gen_m5_2.py   → src/games/m5-2/img/q02-scene.jpg … q12-bad.jpg, qNN-thumb.jpg (44장)

원본: data/나관엽 - 게임 참고자료 (10.26)/…/중5-2 활용 그림/
  - 칸마다 권리 침해 상황 그림 1장(예: '3- 반말하는 상황.png') → qNN-scene.jpg, 말판 칸 그림 qNN-thumb.jpg
  - 'N- ⭕ … ❌ ….png' 는 두 그림이 붙은 한 장이다. 가운데 흰 줄을 찾아 나눈다.
    위·아래면 위가 ⭕, 좌·우면(7번) 왼쪽이 ⭕. → qNN-good.jpg(⭕), qNN-bad.jpg(❌)
모두 진짜 그림이라 도장을 찍지 않는다. 자르기 함수는 gen_m5_1.py 와 같은 것을 쓴다.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_m5_1 import ROOT, build  # noqa: E402

if __name__ == '__main__':
    build('중5-2 활용 그림', ROOT / 'src' / 'games' / 'm5-2' / 'img', range(2, 13))

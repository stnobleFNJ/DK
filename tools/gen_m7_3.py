"""중7-3 옆집 아주머니 이야기: 참고자료 그림(이야기 3개 × 20컷)을 src/games/m7-3/img로 옮긴다.
원본: data/큐알활동/중기 - 게임 참고자료 나관엽 (11.14)/…/7-3 (추가 제작)/{비밀번호,통장,신분증}/01~20.jpg (334×470)
결과: img/{pw,bank,id}-01~20.jpg (같은 크기, 프로그레시브 JPEG)"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = next((ROOT / 'data' / '큐알활동').glob('중기 - 게임 참고자료 나관엽*/*/7-3 (추가 제작)'))
OUT = ROOT / 'src' / 'games' / 'm7-3' / 'img'
OUT.mkdir(parents=True, exist_ok=True)
for folder, key in [('비밀번호', 'pw'), ('통장', 'bank'), ('신분증', 'id')]:
    for i in range(1, 21):
        im = Image.open(SRC / folder / f'{i:02d}.jpg').convert('RGB')
        im.save(OUT / f'{key}-{i:02d}.jpg', 'JPEG', quality=82, optimize=True, progressive=True)
print('ok', len(list(OUT.glob('*.jpg'))))

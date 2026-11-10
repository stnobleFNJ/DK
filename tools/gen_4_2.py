"""전4-2 「나의 공간 아름답게 꾸미기」 — 진짜 사진(빈 방 1장 + 가구 7종 × 3개)을 게임용으로 만든다.

원본: data/_1102/게임(전기3,4단원)/게임(전기3,4)/전4-2 내 공간 정리하기/
      빈 방 이미지.png, {옷장|의자|책꽂이|책상|침대|커튼|테이블}/<색·재질> <가구>.png (모두 1672×941 RGB)
결과: src/games/4-2/img/
      room.jpg               빈 방(1200×675 JPEG)
      {closet|chair|shelf|desk|bed|table}-{1-3}.png   배경을 지운 가구(긴 변 600px, 투명 PNG)
      curtain-{1-3}.png      창문+커튼(방 사진 좌표에 맞춘 크기, 아래 CUR 참고)

- 가구: tools/gen_4_1.py의 cutout()으로 흰 배경을 가장자리부터 flood-fill로 지우고,
  바닥 그림자는 검은 반투명 그림자로 바꾼다(흰 방 바닥 위에서 자연스럽게 보이도록).
  원목 침대는 흰 이불이 바닥과 이어져 지워지므로 protect=True(나무 틀의 볼록 껍질 안은 지우지 않음).
- 커튼: 사진에 창문과 벽이 같이 찍혀 있다. 커튼 천만 오려 내는 대신, 벽만 지우고(창문+커튼+봉 남김)
  사진 속 창문을 방 사진의 창문 자리에 맞춰 겹친다(방 창문을 완전히 덮음).
  커튼 아랫단은 방의 벽-바닥 경계선(y=346)에서 자른다(바닥까지 내려온 커튼처럼 보임).
  방 조명에 맞춰 조금 어둡게(×0.93) 한다. 놓는 자리는 마지막에 출력하는 % 값(index.html .room .cur).
- 진짜 사진이므로 「임시생성」 도장은 찍지 않는다.

    python tools/gen_4_2.py

다시 실행해도 같은 결과가 나온다. 필요한 것: Pillow, numpy.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from gen_4_1 import cutout, save_png, trim  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'data' / '_1102' / '게임(전기3,4단원)' / '게임(전기3,4)' / '전4-2 내 공간 정리하기'
OUT = ROOT / 'src' / 'games' / '4-2' / 'img'

# (폴더, 파일 키, [디자인 1~3 원본 이름], cutout 옵션)
FURN = [
    ('옷장', 'closet', ['블랙 옷장', '원목 옷장', '화이트 옷장'], {}),
    ('의자', 'chair', ['블랙 의자', '원목 의자', '화이트 의자'], {}),
    ('책꽂이', 'shelf', ['블랙 책꽂이', '원목 책꽂이', '화이트 책꽂이'], {}),
    ('책상', 'desk', ['블랙 책상', '원목 책상', '화이트 책상'], {}),
    ('침대', 'bed', ['블랙 침대', '빨간 꽃무늬 침대', '원목 침대'], {}),
    ('테이블', 'table', ['블랙 테이블', '원목 테이블', '화이트 테이블'], {}),
]
PROTECT = {'원목 침대'}
CURTAINS = ['블랙 커튼', '와인 커튼', '화이트 커튼']

# 창문 맞추기: 커튼 사진 속 창문 바깥 틀(398~1274, 125~776)을
# 방 사진(1672×941) 창문 바깥 틀(677~997, 87~327)에 맞춘다. 살짝 크게(0.37) 덮는다.
RW, RH = 1672, 941
CUR_S = 0.37
CUR_X = 837 - 836 * CUR_S          # 창문 가운데 x 맞춤
CUR_Y = 87 - 125 * CUR_S           # 창문 위 틀 맞춤
FLOOR_Y = 346                      # 방 벽-바닥 경계(커튼 아랫단을 여기서 자름)


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True, exist_ok=True)
    room = Image.open(SRC / '빈 방 이미지.png').convert('RGB')
    assert room.size == (RW, RH), room.size
    room.resize((1200, round(RH * 1200 / RW)), Image.LANCZOS).save(OUT / 'room.jpg', 'JPEG', quality=84, optimize=True)
    print('room.jpg')
    for folder, key, names, kw in FURN:
        for i, n in enumerate(names, 1):
            im = Image.open(SRC / folder / f'{n}.png')
            im = trim(cutout(im, shadow=True, protect=n in PROTECT, **kw), maxside=600, thr=40)
            dst = OUT / f'{key}-{i}.png'
            save_png(im, dst)
            print(f'{dst.name}\t{im.size[0]}×{im.size[1]}\t{dst.stat().st_size // 1024}KB\t← {n}')
    for i, n in enumerate(CURTAINS, 1):
        im = cutout(Image.open(SRC / '커튼' / f'{n}.png'), shadow=True, sgain=0)
        im = im.crop((0, 0, im.width, round((FLOOR_Y - CUR_Y) / CUR_S)))
        im = im.resize((round(im.width * CUR_S), round(im.height * CUR_S)), Image.LANCZOS)
        a = np.asarray(im).astype(np.float32)
        a[..., :3] *= 0.93
        im = Image.fromarray(a.clip(0, 255).astype(np.uint8), 'RGBA')
        dst = OUT / f'curtain-{i}.png'
        save_png(im, dst)
        print(f'{dst.name}\t{im.size[0]}×{im.size[1]}\t{dst.stat().st_size // 1024}KB\t← {n}')
    w, h = round(1672 * CUR_S), round((FLOOR_Y - CUR_Y) / CUR_S) * CUR_S
    print(f'커튼 자리(%): left {CUR_X / RW * 100:.3f} top {CUR_Y / RH * 100:.3f} width {w / RW * 100:.3f}')


if __name__ == '__main__':
    main()

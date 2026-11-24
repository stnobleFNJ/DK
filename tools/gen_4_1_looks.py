"""전4-1 완성 옷차림 사진 128장 만들기.

원본: data/큐알활동/3,4단원_QR활동수정요청_조가영(1118).hwpx 안의 그림 image15~22
(1254×1254, 4×4 칸). 한 장 = 상의 1개. 줄(위→아래) = 하의 1~4, 칸(왼→오) = 신발 1~4.
  image15~18: 남자 상의 4(흰 셔츠)·1(베이지 맨투맨)·2(초록 긴팔)·3(파란 반팔)
  image19~22: 여자 상의 1(하늘 블라우스)·2(노란 반팔)·3(흰 블라우스)·4(자주 카디건)
결과: src/games/4-1/img/look/{m|f}-{상의}{하의}{신발}.jpg  (예: m-312.jpg)
"""
import sys, zipfile, io
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'data/큐알활동/3,4단원_QR활동수정요청_조가영(1118).hwpx'
OUT = ROOT / 'src/games/4-1/img/look'
MAP = {15: ('m', 4), 16: ('m', 1), 17: ('m', 2), 18: ('m', 3),
       19: ('f', 1), 20: ('f', 2), 21: ('f', 3), 22: ('f', 4)}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    z = zipfile.ZipFile(SRC)
    n = 0
    for k, (g, top) in MAP.items():
        im = Image.open(io.BytesIO(z.read(f'BinData/image{k}.png'))).convert('RGB')
        W, H = im.size
        for r in range(4):          # 하의
            for c in range(4):      # 신발
                x0, x1 = W * c / 4, W * (c + 1) / 4
                y0, y1 = H * r / 4, H * (r + 1) / 4
                tw = x1 - x0
                # 칸 사이 선을 빼고, 사람이 있는 가운데만 세로로 길게(3:5) 자른다
                box = (round(x0 + tw * .2), round(y0 + 6), round(x1 - tw * .2), round(y1 - 6))
                t = im.crop(box)
                t = t.resize((240, round(240 * t.height / t.width)), Image.LANCZOS)
                t.save(OUT / f'{g}-{top}{r + 1}{c + 1}.jpg', quality=84, optimize=True)
                n += 1
    print(n, 'files ->', OUT)

if __name__ == '__main__':
    main()

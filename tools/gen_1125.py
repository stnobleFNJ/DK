"""11/25 수정 요청서(hwpx) 안의 그림으로 게임 이미지를 바꾼다.
사용: python tools/gen_1125.py   (gen_3_3·gen_5_2·gen_8_4·gen_h4_1·gen_h5_2를 다시 돌렸다면 그 뒤에 실행)

- 전3-3: 상황1 「쑥스러워요」 얼굴(s1-f2.jpg)      - 전8-4: 단풍길 러닝 페스타 포스터(ev07.jpg)
- 전5-2: 보드판 제목 글자 「공간 바르게 사용하기」   - 후5-2: 「어디였나요?」 삽화 5장(사람 없는 장소)
- 후2-1(h4-1): 대표 사진 arm·leg, 단계 사진 16장   - 후2-3(h4-3): leg 대표 사진
단계 사진·장소 삽화는 요청서에 들어 있는 크기가 약 240px뿐이라 키워서 쓴다(원본이 오면 교체).
"""
import io
import sys
import zipfile
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / 'data' / '큐알활동수정요청(1125)'
G = ROOT / 'src' / 'games'


def pics(key):
    z = zipfile.ZipFile(next(D.glob(f'*{key}*.hwpx')))
    return {Path(n).stem[5:]: Image.open(io.BytesIO(z.read(n))).convert('RGB') for n in z.namelist() if n.startswith('BinData/')}


def save(im, rel):
    im.save(G / rel, 'JPEG', quality=86, optimize=True, progressive=True)
    print(rel, im.size)


def quad(im, pts, side):
    """기울어진 폴라로이드 안의 사진만 반듯한 정사각형으로 편다(왼위·오른위·오른아래·왼아래)."""
    m = cv2.getPerspectiveTransform(np.float32(pts), np.float32([[0, 0], [side, 0], [side, side], [0, side]]))
    return Image.fromarray(cv2.warpPerspective(np.array(im), m, (side, side), flags=cv2.INTER_CUBIC))


def up(im, w):
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))


def step(im, side=(11, 10)):
    """가장자리 흰 줄을 잘라 내고 11:10으로 맞춘다."""
    im = im.crop((4, 4, im.width - 4, im.height - 4))
    w, h = im.size
    tw, th = (w, round(w * side[1] / side[0]))
    if th > h:
        tw, th = round(h * side[0] / side[1]), h
    x = (w - tw) // 2
    return up(im.crop((x, 0, x + tw, th)), 720)


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    shy = pics('조가영')['2']
    save(shy.resize((1200, 675), Image.LANCZOS), '3-3/img/s1-f2.jpg')

    run = pics('김유린')['1']
    w = round(run.height * 768 / 1080)
    x = (run.width - w) // 2
    save(run.crop((x, 0, x + w, run.height)).resize((768, 1080), Image.LANCZOS), '8-4/img/ev07.jpg')

    h = pics('후기')
    arm = quad(h['5'], [(64, 92), (1130, 92), (1108, 1160), (38, 1144)], 900)
    leg = quad(h['7'], [(62, 86), (1128, 86), (1108, 1152), (38, 1132)], 900)
    save(arm, 'h4-1/img/arm.jpg')
    save(leg, 'h4-1/img/leg.jpg')
    save(leg, 'h4-3/img/leg.jpg')
    # 가슴 사진 왼쪽 위 번호표(1.~4.)를 같은 장소인 팔 사진(14)의 창문으로 가린다
    for n in '17', '18', '19', '20':
        im = h[n]
        patch = h['14'].crop((0, 0, 36, 38))
        mask = Image.new('L', patch.size, 0)
        ImageDraw.Draw(mask).rectangle((0, 0, 32, 33), fill=255)
        im.paste(patch, (0, 0), mask.filter(ImageFilter.GaussianBlur(1)))
    for key, start in ('face', 9), ('arm', 13), ('chest', 17), ('leg', 21):
        for i in range(4):
            save(step(h[str(start + i)]), f'h4-1/img/{key}-{i + 1}.jpg')
    W = {'mall': (27, [(10, 8), (229, 13), (227, 236), (4, 232)]), 'home': (28, [(6, 11), (229, 6), (235, 231), (11, 235)]),
         'park': (29, [(11, 9), (236, 5), (241, 230), (16, 235)]), 'cafe': (30, [(12, 12), (237, 15), (231, 242), (8, 238)]),
         'trip': (31, [(11, 10), (235, 5), (240, 228), (17, 233)])}
    for k, (n, pts) in W.items():
        save(quad(h[str(n)], pts, 720).filter(ImageFilter.UnsharpMask(2, 60, 2)), f'h5-2/img/where-{k}.jpg')

    b = Image.open(G / '5-2/img/board.jpg').convert('RGB')
    s = b.width / 1600
    d = ImageDraw.Draw(b)
    d.rounded_rectangle([v * s for v in (492, 15, 1108, 123)], 24 * s, fill=(2, 35, 83))
    d.text((800 * s, 68 * s), '공간 바르게 사용하기', font=ImageFont.truetype('malgunbd.ttf', round(60 * s)), fill='white', anchor='mm')
    save(b, '5-2/img/board.jpg')


if __name__ == '__main__':
    main()

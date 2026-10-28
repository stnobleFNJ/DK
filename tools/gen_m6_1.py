"""중6-1 「나에게 필요한 서비스 이상형 월드컵」 — 서비스 설명 그림 14장을 줄여 저장한다.
사용: python tools/gen_m6_1.py   → src/games/m6-1/img/<서비스>-<1|2>.jpg (14장)

원본: data/나관엽 - 게임 참고자료 (10.26)/…/중6-1 활용 그림/<서비스 이름> <1|2>. <설명>.png (1448×1086)
모두 실제 그림이므로 임시 그림·도장은 없다. 자르지 않고 긴 변 1200px로만 줄인다.
(평생교육 이용권 1 은 중7-4 8번 그림과 바이트가 같은 파일이지만 그대로 쓴다.)
다시 실행해도 같은 결과가 나온다.
"""
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'data' / '나관엽 - 게임 참고자료 (10.26)' / '나관엽 - 게임 참고자료 (10.26)' / '중6-1 활용 그림'
OUT = ROOT / 'src' / 'games' / 'm6-1' / 'img'
LONG = 1200
QUALITY = 83

# 원본 파일 이름 앞부분(서비스 이름) → 저장 이름 앞부분
SERVICES = {
    '장애인 스포츠 강좌 이용권': 'sports',
    '평생교육 이용권': 'edu',
    '장애인연금': 'pension',
    '장애인활동지원': 'activity',
    '공공후견': 'guardian',
    '개인별지원계획': 'plan',
    '권익옹호': 'rights',
}


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True, exist_ok=True)
    n = 0
    for svc, key in SERVICES.items():
        for no in (1, 2):
            hits = sorted(SRC.glob(f'{svc} {no}. *.png'))
            if len(hits) != 1:
                raise SystemExit(f'원본을 찾지 못함: {svc} {no} → {hits}')
            im = Image.open(hits[0]).convert('RGB')
            s = LONG / max(im.size)
            if s < 1:
                im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
            out = OUT / f'{key}-{no}.jpg'
            im.save(out, 'JPEG', quality=QUALITY, optimize=True, progressive=True)
            n += 1
            print(f'{out.relative_to(ROOT)}\t{im.size[0]}×{im.size[1]}\t{out.stat().st_size // 1024}KB\t← {hits[0].name}')
    print(n, '장')


if __name__ == '__main__':
    main()

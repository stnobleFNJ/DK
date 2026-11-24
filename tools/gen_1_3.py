"""전1-3 「하루 계획하기(내일 계획 만들기)」 사진을 11/18 수정 의견(오승은) 원본 사진으로 만든다.
사용: python tools/gen_1_3.py   → src/games/1-3/img/*.jpg
원본: data/큐알활동/게임(전기)1단원 수정의견261118/…/전1-3 하루 계획하기/
  - 하루계획 첫장면.png → start.jpg
  - 주제 콜라주 4장 → theme-*.jpg  (파일 「내 생활을 돌봐요.png」 = 주제 「내 생활을 챙겨요」)
  - 활동12개/*.png → act-*.jpg
예전의 임시생성 그림(act-*.jpg 16장)은 모두 실제 사진으로 바뀌었다.
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'data' / '큐알활동' / '게임(전기)1단원 수정의견261118' / '게임(전기)1단원 수정의견261118' / '전1-3 하루 계획하기'
OUT = ROOT / 'src' / 'games' / '1-3' / 'img'

FILES = {
    'start.jpg': '하루계획 첫장면.png',
    'theme-self.jpg': '나를 돌봐요.png',
    'theme-life.jpg': '내 생활을 돌봐요.png',
    'theme-people.jpg': '사람들과 함께 해요.png',
    'theme-fun.jpg': '내가 하고 싶은 일을 해요.png',
    'act-meal.jpg': '활동12개/01_식사하기_16대9_1920x1080.png',
    'act-exercise.jpg': '활동12개/02_운동하기_16대9_1920x1080.png',
    'act-hospital.jpg': '활동12개/03_병원가기_16대9_1920x1080.png',
    'act-market.jpg': '활동12개/04_장보기_16대9_1920x1080.png',
    'act-laundry.jpg': '활동12개/05_세탁하기_16대9_1920x1080.png',
    'act-clean.jpg': '활동12개/06_청소하기_16대9_1920x1080.png',
    'act-friend.jpg': '활동12개/07_친구와_함께하기_16대9_1920x1080.png',
    'act-family.jpg': '활동12개/08_가족과_함께하기_16대9_1920x1080.png',
    'act-program.jpg': '활동12개/09_센터프로그램_지역행사참여하기_16대9_1920x1080.png',
    'act-movie.jpg': '활동12개/10_영화보기_16대9_1920x1080.png',
    'act-travel.jpg': '활동12개/11_여행가기_16대9_1920x1080.png',
    'act-dining.jpg': '활동12개/12_외식하기_16대9_1920x1080.png',
}
OLD_TEMP = ['act-sleep.jpg', 'act-stretch.jpg', 'act-walk.jpg', 'act-cafe.jpg', 'act-call.jpg',
            'act-dishes.jpg', 'act-karaoke.jpg', 'act-camping.jpg', 'act-draw.jpg']


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for out, src in FILES.items():
        im = Image.open(SRC / src).convert('RGB')
        if out.startswith('act-'):  # 활동 사진은 위아래에 흐린 띠(약 140px)가 있어 사진 부분만 자른다
            im = im.crop((0, 150, im.width, im.height - 152))
        im.thumbnail((1200, 1200), Image.LANCZOS)
        im.save(OUT / out, 'JPEG', quality=82, optimize=True, progressive=True)
        print(out, im.size, (OUT / out).stat().st_size // 1024, 'KB')
    for n in OLD_TEMP:
        p = OUT / n
        if p.exists():
            p.unlink()
            print('삭제', n)


if __name__ == '__main__':
    main()

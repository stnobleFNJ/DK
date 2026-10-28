"""data 폴더의 원본 PNG를 게임용 JPEG(가로 최대 1600px, 품질 82)로 변환한다.
사용: python tools/optimize_images.py [게임 폴더 ...]   (예: 5-2 — 지정하면 그 게임만 변환)
"""
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'data' / '큐알활동사진_생애주기_전기_1,5,6,7단원'

# 게임 폴더 → [(원본 경로, 저장 이름)]
MAP = {
    '1-2': [
        ('전1-2 일주일 돌아보기/영미와 나눈 대화.png', 'chat.jpg'),
        ('전1-2 일주일 돌아보기/중화요리 영수증.png', 'receipt.jpg'),
        ('전1-2 일주일 돌아보기/영화티켓.png', 'ticket.jpg'),
    ],
    '1-3': [
        ('전1-3 하루 계획하기/하루계획 첫장면.png', 'start.jpg'),
        ('전1-3 하루 계획하기/나를 돌봐요.png', 'theme-self.jpg'),
        ('전1-3 하루 계획하기/사람들과 함께 해요.png', 'theme-people.jpg'),
        ('전1-3 하루 계획하기/내 생활을 돌봐요.png', 'theme-life.jpg'),
        ('전1-3 하루 계획하기/내가 하고 싶은 일을 해요.png', 'theme-fun.jpg'),
    ],
    '5-3a': [
        ('5-3 가족에게 내마음 전하기/도입 사회적 상황이야기/1. 상황 - 어머니가 무언가를 들고 보고있는상황.png', 'situation.jpg'),
        ('5-3 가족에게 내마음 전하기/도입 사회적 상황이야기/선택 1-1)나무 테이블 위 스마트폰.png', 'pick-phone.jpg'),
        ('5-3 가족에게 내마음 전하기/도입 사회적 상황이야기/선택 1-2) 나무 테이블 위 손편지와 봉투.png', 'pick-letter.jpg'),
        ('5-3 가족에게 내마음 전하기/도입 사회적 상황이야기/선택 1-3) 나무 테이블 위 네이비 백팩.png', 'pick-bag.jpg'),
        ('5-3 가족에게 내마음 전하기/도입 사회적 상황이야기/선택 2-1) 기분나빠요.png', 'pick-upset.jpg'),
        ('5-3 가족에게 내마음 전하기/도입 사회적 상황이야기/선택 2-2) 부끄러워요.png', 'pick-shy.jpg'),
        ('5-3 가족에게 내마음 전하기/도입 사회적 상황이야기/선택 2-3) 화나요.png', 'pick-angry.jpg'),
        ('5-3 가족에게 내마음 전하기/도입 사회적 상황이야기/선택 3-1) 아무말도 하지 않는다.png', 'pick-silent.jpg'),
        ('5-3 가족에게 내마음 전하기/도입 사회적 상황이야기/선택 3-2) 큰소리로 화를낸다.png', 'pick-shout.jpg'),
        ('5-3 가족에게 내마음 전하기/도입 사회적 상황이야기/선택 3-3) 운다.png', 'pick-cry.jpg'),
        ('5-3 가족에게 내마음 전하기/도입 사회적 상황이야기/사회적 상황이야기 결과(장면1)/엄마가 휴대폰을 보고있는경우.png', 's1-phone.jpg'),
        ('5-3 가족에게 내마음 전하기/도입 사회적 상황이야기/사회적 상황이야기 결과(장면1)/엄마가 편지를 보고있는경우.png', 's1-letter.jpg'),
        ('5-3 가족에게 내마음 전하기/도입 사회적 상황이야기/사회적 상황이야기 결과(장면1)/엄마가 가방을 보고있는경우.png', 's1-bag.jpg'),
        ('5-3 가족에게 내마음 전하기/도입 사회적 상황이야기/사회적 상황이야기 결과(장면2)/기분나빠요.png', 's2-upset.jpg'),
        ('5-3 가족에게 내마음 전하기/도입 사회적 상황이야기/사회적 상황이야기 결과(장면2)/부끄러워요.png', 's2-shy.jpg'),
        ('5-3 가족에게 내마음 전하기/도입 사회적 상황이야기/사회적 상황이야기 결과(장면2)/화나요.png', 's2-angry.jpg'),
        ('5-3 가족에게 내마음 전하기/도입 사회적 상황이야기/사회적 상황이야기(장면3)/아무말도 하지 않는다.png', 's3-silent.jpg'),
        ('5-3 가족에게 내마음 전하기/도입 사회적 상황이야기/사회적 상황이야기(장면3)/선택 3-2) 큰소리로 화를낸다.png', 's3-shout.jpg'),
        ('5-3 가족에게 내마음 전하기/도입 사회적 상황이야기/사회적 상황이야기(장면3)/운다.png', 's3-cry.jpg'),
        ('5-3 가족에게 내마음 전하기/도입 사회적 상황이야기/사회적상황이야기(장면4)/어머니의 난처한 표정.png', 's4.jpg'),
        ('5-3 가족에게 내마음 전하기/도입 사회적 상황이야기/사회적상황이야기(장면5)/시우와 엄마의 마음 대화.png', 's5.jpg'),
    ],
    '5-3b': [
        ('5-3 가족에게 내마음 전하기/활동3 룰렛보드/1. 네 가지 상황 룰렛 보드.png', 'board.jpg'),
        ('5-3 가족에게 내마음 전하기/활동3 룰렛보드/상황 1. 노크 없이 들어온 엄마.png', 'case1.jpg'),
        ('5-3 가족에게 내마음 전하기/활동3 룰렛보드/상황2. 허락 없이 과자를 먹은 동생.png', 'case2.jpg'),
        ('5-3 가족에게 내마음 전하기/활동3 룰렛보드/상황3. 내 새 옷을 입은 형, 놀란 동생.png', 'case3.jpg'),
        ('5-3 가족에게 내마음 전하기/활동3 룰렛보드/상황4. 잠들려는 아들에게 외출을 권하는 엄마.png', 'case4.jpg'),
    ],
    '6-2': [
        ('6-2 배려하며 말하기/시작화면.png', 'start.jpg'),
        ('6-2 배려하며 말하기/문제1.png', 'room1.jpg'),
        ('6-2 배려하며 말하기/문제2.png', 'room2.jpg'),
        ('6-2 배려하며 말하기/ChatGPT 이미지 2026년 10월 22일 오전 11_16_38-3.png', 'room3.jpg'),
        ('6-2 배려하며 말하기/ChatGPT 이미지 2026년 10월 22일 오전 11_16_39-4.png', 'room4.jpg'),
        ('6-2 배려하며 말하기/탈출화면.png', 'escape.jpg'),
    ],
    '7-1': [
        ('7-1.취향찾기/1.메인화면.png', 'main.jpg'),
        ('7-1.취향찾기/문제 01_혼자_같이.png', 'q1.jpg'),
        ('7-1.취향찾기/문제 02_실내_야외.png', 'q2.jpg'),
        ('7-1.취향찾기/문제 03_편안하게_활동적으로.png', 'q3.jpg'),
        ('7-1.취향찾기/문제04_ 활동선택.png', 'q4.jpg'),
        ('7-1.취향찾기/카드뒷면.png', 'card-back.jpg'),
    ] + [(f'7-1.취향찾기/최종결과{i}.png', f'result{i}.jpg') for i in range(1, 9)],
    '7-3': [('7-3.혼자가보기/버스 여행 문제 해결 로드맵.png', 'board.jpg')]
          + [(f'7-3.혼자가보기/문제{i}.png', f'q{i}.jpg') for i in range(1, 7)],
    '5-2': [
        ('5-2 우리집공간사용법/1. 우리집 한바퀴 생활공간 보드.png', 'board.jpg'),
        ('5-2 우리집공간사용법/2-1) 거실 상황- 소파를 가득 차지한 아들, 기다리는 부모.png', 'q1-bad.jpg'),
        ('5-2 우리집공간사용법/2-2)-(1) 내방 적절한 행동찾기- 침실에서 스웨터를 갈아입는 순간.png', 'q2-a.jpg'),
        ('5-2 우리집공간사용법/2-2)-(2) 내방 적절한 행동찾기-소파에 나란히 앉은 한국 가족.png', 'q2-b.jpg'),
        ('5-2 우리집공간사용법/2-3) 주방 상황 - 식탁 위 정리되지 않은 물건들.png', 'q3-bad.jpg'),
        ('5-2 우리집공간사용법/2-4) 거실 상황 - 큰소리로 음악을 들어 아버지가 귀막음.png', 'q4-bad.jpg'),
        ('5-2 우리집공간사용법/2-5)-(1) 내방 적절한 행동찾기 - 침대 위 한식 식사와 작은 얼룩.png', 'q5-a.jpg'),
        ('5-2 우리집공간사용법/2-5)-(2) 내방 적절한 행동 찾기 - 침실에서 스마트폰으로 통화하는 성인 남성.png', 'q5-b.jpg'),
        ('5-2 우리집공간사용법/2-6) 화장실 상황 - 휴대폰을 하며 화장실을 오래사용하는 모습.png', 'q6-bad.jpg'),
        ('5-2 우리집공간사용법/2-7)-(1) 내 방 적절한 행동찾기 - 침실에서 음악을 듣는 모습.png', 'q7-a.jpg'),
        ('5-2 우리집공간사용법/2-7)-(2) 내 방 적절한 행동찾기 - 프라이팬으로 요리하는 모습.png', 'q7-b.jpg'),
        ('5-2 우리집공간사용법/2-8) 주방 상황 - 식사 후 그대로 남은 식탁.png', 'q8-bad.jpg'),
    ],
}


def crop_7_1():
    """7-1 문제 이미지에서 글자를 뺀 사진 부분만 잘라 낸다(hwpx: 결과 문장은 화면에 표시)."""
    d = ROOT / 'src' / 'games' / '7-1' / 'img'
    acts = ['movie', 'draw', 'walk', 'cook', 'talk', 'library', 'show', 'swim']
    q4 = Image.open(d / 'q4.jpg')
    xs = [(50, 390), (441, 775), (827, 1167), (1218, 1552)]
    ys = [(44, 266), (457, 690)]
    for i, ((y0, y1), (x0, x1)) in enumerate((y, x) for y in ys for x in xs):
        q4.crop((x0 + 2, y0 + 2, x1 - 2, y1 - 2)).save(d / f'act-{acts[i]}.jpg', quality=85)
    for q, (a, b), y1 in [('q1', ('alone', 'together'), 580), ('q2', ('indoor', 'outdoor'), 548), ('q3', ('calm', 'active'), 548)]:
        im = Image.open(d / f'{q}.jpg')
        im.crop((54, 356, 786, y1)).save(d / f'{a}.jpg', quality=85)
        im.crop((826, 356, 1546, y1)).save(d / f'{b}.jpg', quality=85)
    for p in ['q1', 'q2', 'q3', 'q4'] + [f'result{i}' for i in range(1, 9)]:
        (d / f'{p}.jpg').unlink(missing_ok=True)


def main(only=()):
    for game, items in MAP.items():
        if only and game not in only:
            continue
        out = ROOT / 'src' / 'games' / game / 'img'
        out.mkdir(parents=True, exist_ok=True)
        for src, name in items:
            im = Image.open(SRC / src).convert('RGB')
            if im.width > 1600:
                im = im.resize((1600, round(im.height * 1600 / im.width)), Image.LANCZOS)
            im.save(out / name, 'JPEG', quality=82, optimize=True, progressive=True)
            print(f'{game}/{name}\t{im.width}x{im.height}\t{(out / name).stat().st_size // 1024}KB')
    if not only or '7-1' in only:
        crop_7_1()


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main(sys.argv[1:])

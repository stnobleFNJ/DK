# DK — 생애주기 게임

성인 전기 과정의 생애주기 학습 게임 모음입니다. 게임 목록과 기획 내용은 `docs/게임개발목록.md`를 봅니다.

## 폴더 구조

```
DK/
├── src/                 # 배포 폴더 — 이 안의 파일을 cafe24 웹 루트(www)에 그대로 올린다
│   ├── index.html       # 게이트(게임 목록) 페이지
│   ├── .htaccess        # Apache 설정(UTF-8, 캐시)
│   └── games/
│       ├── common/      # 공통 테마(paper.css)·도우미(game.js)·로고
│       ├── 1-1/         # 전1-1 오늘의 PICK (data/dk/typeA.html 복사본)
│       └── <차시>/      # index.html + img/
├── data/                # 원본 자료(요청 사진, 전1-1 시안) — 배포하지 않음
├── docs/                # 요청서(hwp)와 정리 문서
├── tools/               # optimize_images.py(원본 → src 이미지), placeholder.py·gen_*.py(임시 그림), preview.html(화면 확인용)
└── tests/
```

## 로컬에서 보기

```
cd src
python -m http.server 8000
```

브라우저에서 http://127.0.0.1:8000/ 을 엽니다.

## 배포(cafe24)

FTP로 `src/` **안의** 파일과 폴더(`.htaccess` 포함)를 `www/`에 올립니다. 모든 경로가 상대 경로라 하위 폴더에 올려도 동작합니다.

## 개발 규칙

- 모든 게임 디자인은 `data/dk/typeA.html`(종이 전시)을 기준으로 하고, `src/games/common/`의 테마를 씁니다.
- 원본 PNG는 `data/`에 두고 `python tools/optimize_images.py`로 `src/games/<차시>/img/`에 JPEG을 만듭니다.
- 성인 중기 게임은 `src/games/m<회기>/`(예: `m5-1`)에 있고, 이미지는 `python tools/gen_m<회기>.py`(예: `gen_m5_1.py`)로 `data/나관엽 - 게임 참고자료 (10.26)/`에서 만듭니다.
- 사진이 없는 이미지는 `tools/gen_<차시>.py`로 「임시생성」 도장이 찍힌 그림을 만듭니다. 목록은 `docs/임시이미지목록.md`(`tools/placeholder_manifest/*.json`에서 생성)에 있고, 실제 사진을 같은 파일 이름으로 덮어쓰면 교체됩니다.

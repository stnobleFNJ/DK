"""tools/placeholder_manifest/*.json 을 모아 docs/임시이미지목록.md 를 다시 만든다.

    python tools/build_placeholder_list.py

임시 그림을 만들거나 진짜 사진으로 바꿔 매니페스트가 바뀌면 다시 실행한다.
"""
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAN = ROOT / 'tools' / 'placeholder_manifest'
OUT = ROOT / 'docs' / '임시이미지목록.md'

# 폴더 → (차시, 게임 이름)
GAMES = {
    '1-3': ('전1-3', '내일 계획 만들기'),
    '1-4': ('전1-4', '내가 원하는 프로그램 고르기'),
    '5-2': ('전5-2', '우리집 한바퀴'),
    '8-4': ('전8-4', '나와 맞는 행사 찾기'),
    'm7-1': ('중7-1', '우리집 위험 요소 찾기'),
    'h4-1': ('후4-1', '위급 신호 몸으로 따라 하기'),
}
ORDER = {'전': 0, '중': 1, '후': 2}


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    secs = []
    for f in MAN.glob('*.json'):
        key = f.stem
        code, name = GAMES.get(key, (key, ''))
        secs.append((ORDER.get(code[0], 9), code, key, name, json.loads(f.read_text(encoding='utf-8'))))
    secs.sort(key=lambda s: (s[0], s[1]))
    total = sum(len(s[4]) for s in secs)
    lines = [
        '# 임시 생성 이미지 목록', '',
        f'{date.today().isoformat()} 기준 · 원본: [Claude Docs](https://claude.ai/artifact/6dgBMKH8fPxrtoFK2AvDpF) · '
        '자동 생성: `python tools/build_placeholder_list.py` (`tools/placeholder_manifest/*.json`)', '',
        f'진짜 사진이 없는 이미지 {total}장({len(secs)}개 게임)을 `tools/placeholder.py`와 게임별 `tools/gen_<폴더>.py`로 직접 그렸습니다. '
        '모든 그림에 빨간 「임시생성」 도장이 있고, 실제 사진을 같은 파일 이름·같은 비율로 `src/games/<폴더>/img/`에 덮어쓰면 교체됩니다.', '',
        '| 차시 | 게임 | 임시 그림 |', '| --- | --- | --- |',
    ]
    lines += [f'| {c} | {n} | {len(m)}장 |' for _, c, _, n, m in secs]
    for _, code, key, name, m in secs:
        lines += ['', f'### {code} {name} ({len(m)}장)', '', f'`src/games/{key}/img/`', '',
                  '| 파일명 | 간단 설명 | 구조 | 쓰는 곳 |', '| --- | --- | --- | --- |']
        lines += [f"| `{Path(e['file']).name}` | {e['desc']} | {e['structure']} | {e['used_in']} |" for e in m]
    OUT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'{OUT.relative_to(ROOT)}: {len(secs)}개 게임, {total}장')


if __name__ == '__main__':
    main()

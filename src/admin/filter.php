<?php
/* 게임 기록 검색·정렬 조건(index.php · export.php 공용) */
if (!defined('DK_ADMIN')) exit;

const SORTS = ['started_at' => '시작 일시', 'done_at' => '완료 일시', 'course' => '과정', 'game' => '게임', 'status' => '완료 여부', 'elapsed' => '걸린 시간', 'steps' => '화면 수', 'ip' => 'IP'];
const STATUS = ['done' => '완료', 'undone' => '미완료(진행·중단)', 'play' => '진행 중', 'exit' => '중단'];

function filters()
{
    $g = function ($k, $d = '') { return isset($_GET[$k]) && is_string($_GET[$k]) ? trim($_GET[$k]) : $d; };
    $f = [
        'status' => $g('status'), 'course' => $g('course'), 'game' => $g('game'), 'q' => mb_substr($g('q'), 0, 100, 'UTF-8'),
        'from' => $g('from'), 'to' => $g('to'), 'sort' => $g('sort', 'started_at'), 'dir' => $g('dir', 'desc'),
        'per' => (int)$g('per', '30'), 'page' => max(1, (int)$g('page', '1')),
    ];
    if (!array_key_exists($f['status'], STATUS)) $f['status'] = '';
    if (!in_array($f['course'], ['전기', '중기', '후기'], true)) $f['course'] = '';
    if (!array_key_exists($f['game'], games())) $f['game'] = '';
    foreach (['from', 'to'] as $k) if (!preg_match('/^\d{4}-\d{2}-\d{2}$/', $f[$k])) $f[$k] = '';
    if (!array_key_exists($f['sort'], SORTS)) $f['sort'] = 'started_at';
    $f['dir'] = $f['dir'] === 'asc' ? 'asc' : 'desc';
    if (!in_array($f['per'], [30, 50, 100, 300], true)) $f['per'] = 30;
    return $f;
}

/* → [WHERE 문, 값 배열] */
function where($f)
{
    $w = ["view_state<>'D'"];  // 삭제한 기록은 어디에도 보이지 않는다
    $a = [];
    if ($f['status'] === 'undone') $w[] = "status<>'done'";
    elseif ($f['status']) { $w[] = 'status=?'; $a[] = $f['status']; }
    if ($f['course']) { $w[] = 'course=?'; $a[] = $f['course']; }
    if ($f['game']) { $w[] = 'game=?'; $a[] = $f['game']; }
    if ($f['from']) { $w[] = 'started_at>=?'; $a[] = $f['from'] . ' 00:00:00'; }
    if ($f['to']) { $w[] = 'started_at<=?'; $a[] = $f['to'] . ' 23:59:59'; }
    if ($f['q'] !== '') {
        $w[] = '(ip LIKE ? OR title LIKE ? OR game LIKE ? OR result LIKE ? OR trail LIKE ? OR data LIKE ?)';
        $like = '%' . addcslashes($f['q'], '%_\\') . '%';
        array_push($a, $like, $like, $like, $like, $like, $like);
    }
    return [' WHERE ' . implode(' AND ', $w), $a];
}

function order_by($f)
{
    // 같은 값이면 최근 것부터
    return ' ORDER BY ' . $f['sort'] . ' ' . strtoupper($f['dir']) . ($f['sort'] === 'started_at' ? '' : ', started_at DESC') . ', id DESC';
}

function dur($s)
{
    $s = (int)$s;
    return $s < 60 ? $s . '초' : floor($s / 60) . '분 ' . ($s % 60) . '초';
}

/* 결과 값(data) → [한국어 이름 => 읽기 쉬운 값] */
function data_rows($data)
{
    $name = ['score' => '점수(맞힌 수)', 'winner' => '승리', 'players' => '인원', 'topic' => '주제', 'win' => '1위', 'second' => '2위', 'third' => '3위',
        'plan' => '고른 계획', 'top' => '상의', 'bottom' => '하의', 'shoes' => '신발', 'pick' => '고른 것', 'act' => '활동', 'card' => '카드 문장',
        'miss' => '필요 없는 물건을 고른 횟수', 'event' => '행사', 'count' => '고른 개수', 'feel' => '마음', 'picked' => '고른 증상', 'champion' => '우승',
        'first' => '1순위', 'type' => '주거 유형', 'level' => '단계', 'retry' => '틀린 문제 다시 풀기', 'tell' => '말할 사람'];
    $fmt = function ($v) use (&$fmt) {
        if (is_bool($v)) return $v ? '예' : '아니요';
        if ($v === null) return '-';
        if (is_array($v)) return implode(', ', array_map($fmt, $v));
        return (string)$v;
    };
    $out = [];
    foreach ((array)$data as $k => $v) $out[is_int($k) ? '값 ' . ($k + 1) : (isset($name[$k]) ? $name[$k] : $k)] = $fmt($v);
    return $out;
}

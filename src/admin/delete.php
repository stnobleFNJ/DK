<?php
/* 게임 기록 삭제(최고 관리자만). 실제로 지우지 않고 view_state를 'D'로 바꾼다 — 목록·요약·CSV·결과 화면 보기에서 빠진다. */
require __DIR__ . '/lib.php';
$u = need_login(true);
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { header('Location: index.php'); exit; }
check_csrf();

$ids = [];
foreach ((array)(isset($_POST['ids']) ? $_POST['ids'] : []) as $v) if (ctype_digit((string)$v)) $ids[(int)$v] = (int)$v;
$ids = array_slice(array_values($ids), 0, 1000);
if ($ids) {
    $n = q('UPDATE ' . T('play') . " SET view_state='D', deleted_at=?, deleted_by=? WHERE view_state<>'D' AND id IN (" . implode(',', array_fill(0, count($ids), '?')) . ')',
        array_merge([now(), $u['username']], $ids));
    flash($n . '개 기록을 삭제했습니다.');
} else flash('삭제할 기록을 고르세요.');

// 보던 검색·정렬·쪽으로 돌아가기(검색 조건 문자열만 받는다)
$back = isset($_POST['back']) && is_string($_POST['back']) ? $_POST['back'] : '';
header('Location: index.php' . ($back !== '' && !preg_match('/[\r\n#]/', $back) ? '?' . $back : ''));

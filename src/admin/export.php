<?php
/* 지금 검색 조건 그대로 CSV(엑셀) 내려받기 */
require __DIR__ . '/lib.php';
require __DIR__ . '/filter.php';
need_login();
$f = filters();
list($w, $a) = where($f);
$rows = q('SELECT * FROM ' . T('play') . $w . order_by($f) . ' LIMIT 50000', $a);
$games = games();
$st = ['done' => '완료', 'play' => '진행 중', 'exit' => '중단'];

header('Content-Type: text/csv; charset=utf-8');
header('Content-Disposition: attachment; filename="dk_game_' . date('Ymd_His') . '.csv"');
$o = fopen('php://output', 'w');
fwrite($o, "\xEF\xBB\xBF");  // 엑셀에서 한글이 깨지지 않게
fputcsv($o, ['번호', '시작 일시', '완료 일시', '과정', '차시', '게임', '완료 여부', '걸린 시간(초)', '화면 수', 'IP', '결과 값', '고른 것', '결과 화면', '브라우저', '세션']);
foreach ($rows as $r) {
    $g = isset($games[$r['game']]) ? $games[$r['game']] : [$r['game'], $r['title']];
    $trail = json_decode((string)$r['trail'], true) ?: [];
    fputcsv($o, [$r['id'], $r['started_at'], $r['done_at'], $r['course'], $g[0], $g[1], isset($st[$r['status']]) ? $st[$r['status']] : $r['status'],
        $r['elapsed'], $r['steps'], $r['ip'], $r['data'], implode(' > ', $trail), $r['result'], $r['ua'], $r['sid']]);
}
fclose($o);

<?php
/* 게임 플레이 기록 받기 (games/common/game.js → POST JSON). 로그인 없이 받지만 값은 모두 검사하고 크기를 제한한다.
   event: start(처음 화면을 벗어남) · exit(중간에 나감, 진행 상황) · done(결과 화면) */
define('DK_API', 1);
require __DIR__ . '/lib.php';

header('Content-Type: text/plain; charset=utf-8');
header('Cache-Control: no-store');
if ($_SERVER['REQUEST_METHOD'] !== 'POST') fail('', 405);

$raw = file_get_contents('php://input', false, null, 0, 1500000);  // 결과 화면 HTML(shot) 때문에 넉넉히
$in = json_decode($raw, true);
if (!is_array($in)) fail('', 400);

$str = function ($k, $max) use ($in) { return isset($in[$k]) && is_scalar($in[$k]) ? mb_substr(trim((string)$in[$k]), 0, $max, 'UTF-8') : ''; };
$int = function ($k) use ($in) { return isset($in[$k]) && is_numeric($in[$k]) ? max(0, min(86400, (int)$in[$k])) : 0; };

$sid = $str('sid', 40);
$game = $str('game', 20);
$event = $str('event', 10);
if (!preg_match('/^[a-z0-9]{8,40}$/', $sid) || !preg_match('/^[a-z0-9-]{1,20}$/', $game) || !in_array($event, ['start', 'exit', 'done'], true)) fail('', 400);
$games = games();
if ($games && !isset($games[$game])) fail('', 400);  // 게이트에 없는 게임은 받지 않음

$title = isset($games[$game]) ? $games[$game][1] : $str('title', 120);
$course = course_of($game);
$ip = isset($_SERVER['REMOTE_ADDR']) ? substr($_SERVER['REMOTE_ADDR'], 0, 45) : '';
$ua = isset($_SERVER['HTTP_USER_AGENT']) ? mb_substr($_SERVER['HTTP_USER_AGENT'], 0, 255, 'UTF-8') : '';
$steps = $int('steps');
$elapsed = $int('elapsed');
$trail = [];
if (isset($in['trail']) && is_array($in['trail']))
    foreach (array_slice($in['trail'], 0, 300) as $t) if (is_scalar($t)) $trail[] = mb_substr((string)$t, 0, 60, 'UTF-8');
$trail = json_encode($trail, JSON_UNESCAPED_UNICODE);
$t = now();

if ($event === 'start') {
    q('INSERT IGNORE INTO ' . T('play') . ' (sid,game,title,course,status,ip,ua,steps,elapsed,trail,started_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
        [$sid, $game, $title, $course, 'play', $ip, $ua, $steps, $elapsed, $trail, $t, $t]);
} else {
    $result = $event === 'done' ? $str('result', 3000) : null;
    $data = $event === 'done' && isset($in['data']) && $in['data'] !== null ? mb_substr(json_encode($in['data'], JSON_UNESCAPED_UNICODE), 0, 2000, 'UTF-8') : null;
    $status = $event === 'done' ? 'done' : 'exit';
    // 결과 화면 HTML(관리자 '게임 결과 화면 보기'). 스크립트·이벤트 속성·javascript: 주소는 지운다.
    // 보여 줄 때도 스크립트를 막은 iframe에서만 연다(snapshot.php).
    $snap = null;
    if ($event === 'done' && isset($in['shot']['html']) && is_string($in['shot']['html']) && trim($in['shot']['html']) !== '' && strlen($in['shot']['html']) < 1000000) {
        $html = preg_replace('#<(script|iframe|object|embed|base|meta|link)\b[^>]*>(.*?</\1\s*>)?#is', '', $in['shot']['html']);
        $html = preg_replace('#\s+on[a-z]+\s*=\s*("[^"]*"|\'[^\']*\'|[^\s>]+)#i', '', $html);
        $html = preg_replace('#(href|src|action|formaction)\s*=\s*(["\']?)\s*javascript:#i', '$1=$2#', $html);
        $root = isset($in['shot']['root']) && is_string($in['shot']['root']) && preg_match('/^[A-Za-z0-9_-]{1,40}$/', $in['shot']['root']) ? $in['shot']['root'] : 'app';
        $snap = json_encode(['root' => $root, 'html' => $html], JSON_UNESCAPED_UNICODE);
    }
    // start가 빠졌어도 기록되도록 없으면 넣고, 이미 완료된 기록은 바꾸지 않는다
    q('INSERT INTO ' . T('play') . ' (sid,game,title,course,status,ip,ua,steps,elapsed,trail,result,data,snap,started_at,updated_at,done_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
       ON DUPLICATE KEY UPDATE
         steps=IF(status=\'done\',steps,VALUES(steps)), elapsed=IF(status=\'done\',elapsed,VALUES(elapsed)), trail=IF(status=\'done\',trail,VALUES(trail)),
         result=IF(status=\'done\',result,VALUES(result)), data=IF(status=\'done\',data,VALUES(data)), snap=IF(status=\'done\',snap,VALUES(snap)),
         done_at=IF(status=\'done\',done_at,VALUES(done_at)),
         updated_at=VALUES(updated_at), status=IF(status=\'done\',status,VALUES(status))',
        [$sid, $game, $title, $course, $status, $ip, $ua, $steps, $elapsed, $trail, $result, $data, $snap, $t, $t, $event === 'done' ? $t : null]);
}
http_response_code(204);

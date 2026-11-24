<?php
/* 모두의 작품 모음(전4-1 옷차림 · 전4-2 공간). 로그인 없이 쓰는 공개 API.
   그림은 올리지 않고 고른 번호만 저장한다 → 게임 화면이 번호로 다시 그린다.
   GET  ?game=4-1          → {"ok":true,"items":[{"id","name","data","at"}]}  (최근 60개, 삭제(D) 제외)
   POST {"game","name","data"} → {"ok":true,"id":…}  · 같은 IP는 10분에 10개까지 */
define('DK_API', 1);
require __DIR__ . '/lib.php';

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
header('X-Content-Type-Options: nosniff');

function out($a, $code = 200) { http_response_code($code); echo json_encode($a, JSON_UNESCAPED_UNICODE); exit; }

/* 게임마다 받을 수 있는 값(고른 번호·자리)을 정해 두고, 그 밖의 값은 버린다 */
function clean_data($game, $d)
{
    if (!is_array($d)) return null;
    $n = function ($v, $max) { return is_int($v) || (is_string($v) && ctype_digit($v)) ? (((int)$v >= 1 && (int)$v <= $max) ? (int)$v : null) : null; };
    if ($game === '4-1') {
        $g = isset($d['g']) ? $d['g'] : '';
        if ($g !== 'm' && $g !== 'f') return null;
        $o = ['g' => $g];
        foreach (['top', 'bottom', 'shoes'] as $k) {
            $v = isset($d[$k]) ? $n($d[$k], 4) : null;
            if ($v === null) return null;
            $o[$k] = $v;
        }
        return $o;
    }
    if ($game === '4-2') {
        if (!isset($d['pick'], $d['pos']) || !is_array($d['pick']) || !is_array($d['pos'])) return null;
        $o = ['pick' => [], 'pos' => []];
        foreach (['curtain', 'shelf', 'bed', 'desk', 'closet', 'table', 'chair'] as $k) {
            $v = isset($d['pick'][$k]) ? $n($d['pick'][$k], 3) : null;
            if ($v === null) return null;
            $o['pick'][$k] = $v;
            if ($k === 'curtain') continue;
            $p = isset($d['pos'][$k]) ? $d['pos'][$k] : null;
            if (!is_array($p) || !isset($p['x'], $p['y']) || !is_numeric($p['x']) || !is_numeric($p['y'])) return null;
            $o['pos'][$k] = ['x' => round(max(0, min(100, (float)$p['x'])), 2), 'y' => round(max(0, min(100, (float)$p['y'])), 2)];
        }
        return $o;
    }
    return null;
}

$games = ['4-1', '4-2'];
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    $game = isset($_GET['game']) ? (string)$_GET['game'] : '';
    if (!in_array($game, $games, true)) out(['ok' => false, 'error' => 'game'], 400);
    $rows = q('SELECT id,name,data,created_at FROM ' . T('gallery') . " WHERE game=? AND view_state<>'D' ORDER BY id DESC LIMIT 60", [$game]);
    $items = [];
    foreach ($rows as $r) {
        $d = json_decode($r['data'], true);
        if ($d) $items[] = ['id' => (int)$r['id'], 'name' => $r['name'], 'data' => $d, 'at' => $r['created_at']];
    }
    out(['ok' => true, 'items' => $items]);
}
if ($_SERVER['REQUEST_METHOD'] !== 'POST') out(['ok' => false], 405);

$in = json_decode(file_get_contents('php://input', false, null, 0, 20000), true);
if (!is_array($in)) out(['ok' => false, 'error' => 'json'], 400);
$game = isset($in['game']) && is_string($in['game']) ? $in['game'] : '';
if (!in_array($game, $games, true)) out(['ok' => false, 'error' => 'game'], 400);

// 이름: 글자만(태그·제어 문자 제거), 1~10자
$name = isset($in['name']) && is_string($in['name']) ? $in['name'] : '';
$name = preg_replace('/[\x00-\x1F\x7F<>]/u', '', strip_tags($name));
$name = trim(preg_replace('/\s+/u', ' ', (string)$name));
$name = mb_substr($name, 0, 10, 'UTF-8');
if ($name === '') out(['ok' => false, 'error' => 'name', 'msg' => '이름을 적어 주세요.'], 400);

$data = clean_data($game, isset($in['data']) ? $in['data'] : null);
if (!$data) out(['ok' => false, 'error' => 'data'], 400);

$ip = isset($_SERVER['REMOTE_ADDR']) ? substr($_SERVER['REMOTE_ADDR'], 0, 45) : '';
$r = q('SELECT COUNT(*) n FROM ' . T('gallery') . ' WHERE ip=? AND created_at > ?', [$ip, date('Y-m-d H:i:s', time() - 600)]);
if ($r && $r[0]['n'] >= 10) out(['ok' => false, 'error' => 'rate', 'msg' => '잠시 뒤에 다시 올려 주세요.'], 429);

$ua = isset($_SERVER['HTTP_USER_AGENT']) ? mb_substr($_SERVER['HTTP_USER_AGENT'], 0, 255, 'UTF-8') : '';
q('INSERT INTO ' . T('gallery') . ' (game,name,data,ip,ua,created_at) VALUES (?,?,?,?,?,?)',
    [$game, $name, json_encode($data, JSON_UNESCAPED_UNICODE), $ip, $ua, now()]);
out(['ok' => true, 'id' => (int)db()->insert_id, 'name' => $name]);

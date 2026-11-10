<?php
/* 게임 결과 화면 보기: 저장해 둔 결과 화면 HTML을 그 게임의 index.html(스타일·그림 그대로)에 끼워 보여 준다.
   게임 스크립트는 모두 빼고, CSP와 sandbox iframe(index.php)으로 스크립트 실행을 막는다. */
require __DIR__ . '/lib.php';
need_login();

$id = isset($_GET['id']) ? (int)$_GET['id'] : 0;
$r = $id ? q('SELECT game, snap FROM ' . T('play') . " WHERE id=? AND view_state<>'D'", [$id]) : [];
$games = games();
$msg = function ($t) {
    header('Content-Type: text/html; charset=utf-8');
    echo '<!doctype html><meta charset="utf-8"><body style="margin:0;display:grid;place-items:center;min-height:100vh;font:15px sans-serif;color:#807669;background:#f4efdf;text-align:center;padding:20px">', h($t), '</body>';
    exit;
};
if (!$r) $msg('기록을 찾을 수 없습니다.');
$game = $r[0]['game'];
$snap = $r[0]['snap'] ? json_decode($r[0]['snap'], true) : null;
if (!isset($games[$game]) || !preg_match('/^[a-z0-9-]{1,20}$/', $game)) $msg('게임을 찾을 수 없습니다.');
if (!$snap || empty($snap['html'])) $msg('저장된 결과 화면이 없습니다. (개인 정보를 보내지 않는 게임이거나, 이 기능을 넣기 전의 기록입니다)');

$page = @file_get_contents(__DIR__ . '/../games/' . $game . '/index.html');
if ($page === false) $msg('게임 파일을 읽을 수 없습니다.');

// 게임 스크립트·도움말 창 빼기. 전1-1처럼 2MB가 넘는 파일은 정규식이 한도를 넘으므로 문자열로 자른다.
function cut_blocks($s, $tag)
{
    $out = '';
    $pos = 0;
    $n = strlen($tag) + 1;
    while (($i = stripos($s, '<' . $tag, $pos)) !== false) {
        $c = substr($s, $i + $n, 1);
        if ($c !== '>' && !ctype_space($c)) { $out .= substr($s, $pos, $i + 1 - $pos); $pos = $i + 1; continue; }  // <scripts 같은 다른 태그
        $out .= substr($s, $pos, $i - $pos);
        $j = stripos($s, '</' . $tag, $i);
        $k = $j === false ? false : strpos($s, '>', $j);
        if ($k === false) return $out;
        $pos = $k + 1;
    }
    return $out . substr($s, $pos);
}
$page = cut_blocks($page, 'script');
$page = cut_blocks($page, 'dialog');
// 그림·스타일 주소가 게임 폴더 기준이 되도록 <base>
$base = '<base href="../games/' . $game . '/">';
$page = preg_replace('#<head([^>]*)>#i', '<head$1>' . $base, $page, 1);
// 미리보기 표시 + 누르기 막기
$style = '<style>.dk-snap-bar{position:sticky;top:0;z-index:99;background:#453f36;color:#fff;font:600 12px/1.4 "Noto Sans KR",sans-serif;padding:6px 10px;text-align:center}'
    . '#' . $snap['root'] . ' *{pointer-events:none!important}#' . $snap['root'] . ' details,#' . $snap['root'] . ' summary{pointer-events:auto!important}'
    . '*,*::before,*::after{animation:none!important;transition:none!important}</style>';
$page = preg_replace('#</head>#i', $style . '</head>', $page, 1);
// 결과 화면 끼워 넣기: 루트 요소(<… id="app" …>) 안에
$bar = '<div class="dk-snap-bar">관리자 미리보기 · 저장된 결과 화면(눌러도 동작하지 않아요)</div>';
$n = 0;
if (preg_match('#<([a-z]+)\b[^>]*\bid="' . preg_quote($snap['root'], '#') . '"[^>]*>#i', $page, $m, PREG_OFFSET_CAPTURE)) {
    $open = $m[0][1] + strlen($m[0][0]);              // 루트 여는 태그 끝
    $close = stripos($page, '</' . $m[1][0] . '>', $open);  // 원본에서 루트는 비어 있다
    if ($close !== false) { $page = substr($page, 0, $open) . $snap['html'] . substr($page, $close); $n = 1; }
}
$page = preg_replace_callback('#<body([^>]*)>#i', function ($m) use ($bar, $snap, $n) { return '<body' . $m[1] . '>' . $bar . ($n ? '' : $snap['html']); }, $page, 1);

header('Content-Type: text/html; charset=utf-8');
header("Content-Security-Policy: script-src 'none'; object-src 'none'; base-uri 'self'; form-action 'none'; frame-ancestors 'self'");
header('X-Content-Type-Options: nosniff');
header('Cache-Control: private, no-store');
echo $page;

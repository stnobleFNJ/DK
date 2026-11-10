<?php
/* 관리자 공통: 설정·DB 연결·표 만들기·로그인·CSRF. PHP 7.0 이상, mysqli(mysqlnd). */
define('DK_ADMIN', 1);
error_reporting(E_ALL);
ini_set('display_errors', '0');

function cfg($k = null)
{
    static $c = null;
    if ($c === null) {
        $f = __DIR__ . '/config.php';
        if (!is_file($f)) fail('설정 파일(admin/config.php)이 없습니다. config.sample.php를 복사해 DB 접속 정보를 채워 주세요.');
        $c = require $f;
        date_default_timezone_set(isset($c['timezone']) ? $c['timezone'] : 'Asia/Seoul');
    }
    return $k === null ? $c : (isset($c[$k]) ? $c[$k] : null);
}

function fail($msg, $code = 500)
{
    http_response_code($code);
    if (defined('DK_API')) exit;
    echo '<!doctype html><meta charset="utf-8"><title>오류</title><body style="font:16px sans-serif;padding:40px">', h($msg), '</body>';
    exit;
}

function h($s) { return htmlspecialchars((string)$s, ENT_QUOTES, 'UTF-8'); }
function now() { return date('Y-m-d H:i:s'); }
function T($name) { return '`' . cfg('prefix') . $name . '`'; }

/* DB 연결. DK_game이 없으면 만들고, 만들 수 없으면 db_fallback을 쓴다. */
function db()
{
    static $db = null;
    if ($db) return $db;
    mysqli_report(MYSQLI_REPORT_OFF);
    $db = @new mysqli(cfg('db_host'), cfg('db_user'), cfg('db_pass'), '', (int)cfg('db_port') ?: 3306);
    if ($db->connect_errno) fail('DB에 접속할 수 없습니다: ' . $db->connect_error);
    $db->set_charset('utf8mb4');
    $name = cfg('db_name');
    if (!@$db->select_db($name)) {
        @$db->query('CREATE DATABASE IF NOT EXISTS `' . $db->real_escape_string($name) . '` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci');
        if (!@$db->select_db($name)) {
            $fb = cfg('db_fallback');
            if (!$fb || !@$db->select_db($fb)) fail("데이터베이스 '$name'을(를) 만들거나 열 수 없습니다. config.php의 db_fallback에 쓸 수 있는 DB 이름을 적어 주세요.");
        }
    }
    $GLOBALS['DK_DB_IN_USE'] = $db->query('SELECT DATABASE()')->fetch_row()[0];
    $db->query("SET time_zone = '" . date('P') . "'");
    schema($db);
    return $db;
}

function schema($db)
{
    $db->query('CREATE TABLE IF NOT EXISTS ' . T('play') . " (
        id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        sid VARCHAR(40) NOT NULL,
        game VARCHAR(20) NOT NULL,
        title VARCHAR(120) NOT NULL DEFAULT '',
        course VARCHAR(10) NOT NULL DEFAULT '',
        status VARCHAR(10) NOT NULL DEFAULT 'play',
        ip VARCHAR(45) NOT NULL,
        ua VARCHAR(255) NOT NULL DEFAULT '',
        steps INT NOT NULL DEFAULT 0,
        elapsed INT NOT NULL DEFAULT 0,
        trail MEDIUMTEXT NULL,
        result MEDIUMTEXT NULL,
        data TEXT NULL,
        snap MEDIUMTEXT NULL,
        view_state CHAR(1) NOT NULL DEFAULT 'Y',
        deleted_at DATETIME NULL,
        deleted_by VARCHAR(40) NULL,
        started_at DATETIME NOT NULL,
        updated_at DATETIME NOT NULL,
        done_at DATETIME NULL,
        UNIQUE KEY sid (sid),
        KEY started_at (started_at),
        KEY game (game),
        KEY course (course),
        KEY status (status),
        KEY view_state (view_state)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4");
    $db->query('CREATE TABLE IF NOT EXISTS ' . T('admin') . " (
        id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(40) NOT NULL,
        pass VARCHAR(255) NOT NULL,
        name VARCHAR(50) NOT NULL DEFAULT '',
        role VARCHAR(10) NOT NULL DEFAULT 'admin',
        created_at DATETIME NOT NULL,
        updated_at DATETIME NOT NULL,
        last_login DATETIME NULL,
        UNIQUE KEY username (username)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4");
    if ($db->error) fail('표를 만들 수 없습니다: ' . $db->error);
    // 나중에 더한 칸: 결과 화면 HTML(게임 결과 화면 보기)
    if (!$db->query('SHOW COLUMNS FROM ' . T('play') . " LIKE 'snap'")->num_rows)
        $db->query('ALTER TABLE ' . T('play') . ' ADD COLUMN snap MEDIUMTEXT NULL AFTER data');
    // 기록 삭제는 지우지 않고 view_state를 'D'로 바꾼다(최고 관리자만)
    if (!$db->query('SHOW COLUMNS FROM ' . T('play') . " LIKE 'view_state'")->num_rows)
        $db->query('ALTER TABLE ' . T('play') . " ADD COLUMN view_state CHAR(1) NOT NULL DEFAULT 'Y' AFTER snap, ADD COLUMN deleted_at DATETIME NULL AFTER view_state, ADD COLUMN deleted_by VARCHAR(40) NULL AFTER deleted_at, ADD KEY view_state (view_state)");
    $r = $db->query('SELECT COUNT(*) FROM ' . T('admin'))->fetch_row();
    if (!$r[0]) {  // 처음 한 번: 최고 관리자
        list($u, $p) = cfg('first_admin') ?: ['dk', 'dk1234'];
        q('INSERT INTO ' . T('admin') . ' (username,pass,name,role,created_at,updated_at) VALUES (?,?,?,?,?,?)',
            [$u, password_hash($p, PASSWORD_DEFAULT), '최고 관리자', 'super', now(), now()]);
    }
}

/* 준비된 문장 실행: q(sql, [값...]) → SELECT면 행 배열, 아니면 영향받은 행 수 */
function q($sql, $args = [])
{
    $db = db();
    $st = $db->prepare($sql);
    if (!$st) fail('쿼리 오류: ' . $db->error);
    if ($args) {
        $types = '';
        foreach ($args as $a) $types .= is_int($a) ? 'i' : 's';
        $refs = [$types];
        foreach ($args as $i => $a) $refs[] = &$args[$i];
        call_user_func_array([$st, 'bind_param'], $refs);
    }
    if (!$st->execute()) fail('쿼리 오류: ' . $st->error);
    $res = $st->get_result();
    $out = $res ? $res->fetch_all(MYSQLI_ASSOC) : $st->affected_rows;
    $st->close();
    return $out;
}

/* ---------- 로그인 ---------- */
function start_session()
{
    if (session_status() === PHP_SESSION_ACTIVE) return;
    session_name('DKADMIN');
    $secure = !empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off';
    ini_set('session.use_strict_mode', '1');
    session_set_cookie_params(0, dirname($_SERVER['SCRIPT_NAME']) . '/', '', $secure, true);
    session_start();
}

function me()
{
    start_session();
    if (empty($_SESSION['aid'])) return null;
    $r = q('SELECT id,username,name,role,last_login FROM ' . T('admin') . ' WHERE id=?', [(int)$_SESSION['aid']]);
    return $r ? $r[0] : null;
}

function need_login($super = false)
{
    $u = me();
    if (!$u) { header('Location: login.php'); exit; }
    if ($super && $u['role'] !== 'super') fail('최고 관리자만 쓸 수 있는 메뉴입니다.', 403);
    return $u;
}

function csrf()
{
    start_session();
    if (empty($_SESSION['csrf'])) $_SESSION['csrf'] = bin2hex(random_bytes(16));
    return $_SESSION['csrf'];
}

function check_csrf()
{
    start_session();
    if (empty($_POST['csrf']) || !hash_equals(csrf(), (string)$_POST['csrf'])) fail('요청이 만료되었습니다. 페이지를 새로 고쳐 다시 시도해 주세요.', 400);
}

function flash($msg = null)
{
    start_session();
    if ($msg !== null) { $_SESSION['flash'] = $msg; return null; }
    $m = isset($_SESSION['flash']) ? $_SESSION['flash'] : '';
    unset($_SESSION['flash']);
    return $m;
}

/* 게이트(../index.html)에서 게임 이름 목록을 읽는다: 폴더 → [차시, 이름] */
function games()
{
    static $g = null;
    if ($g !== null) return $g;
    $g = [];
    $s = @file_get_contents(__DIR__ . '/../index.html');
    if ($s && preg_match_all("/\\{code:'([^']+)',name:'([^']+)',href:'games\\/([^\\/]+)\\/index\\.html'/u", $s, $m, PREG_SET_ORDER))
        foreach ($m as $x) $g[$x[3]] = [$x[1], $x[2]];
    return $g;
}

function course_of($game) { return $game[0] === 'm' ? '중기' : ($game[0] === 'h' ? '후기' : '전기'); }

/* 화면 틀 */
function head_html($title, $u = null, $on = '')
{
    $nav = '';
    if ($u) {
        $nav = '<nav><a href="index.php" class="' . ($on === 'r' ? 'on' : '') . '">게임 기록</a>'
            . ($u['role'] === 'super' ? '<a href="admins.php" class="' . ($on === 'a' ? 'on' : '') . '">관리자 관리</a>' : '')
            . '<span class="who">' . h($u['name'] ?: $u['username']) . ' (' . h($u['username']) . ')</span>'
            . '<form method="post" action="logout.php" class="inl"><input type="hidden" name="csrf" value="' . h(csrf()) . '"><button class="lk">로그아웃</button></form></nav>';
    }
    echo '<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        . '<meta name="robots" content="noindex,nofollow"><title>' . h($title) . ' · 생애주기 게임 관리자</title>'
        . '<link rel="stylesheet" href="admin.css?v=' . @filemtime(__DIR__ . '/admin.css') . '"></head><body><header class="top"><a class="logo" href="index.php"><img src="../games/common/dku-logo.png" alt="단국대학교"><span>생애주기 게임 <b>관리자</b></span></a>' . $nav . '</header><main>';
    $f = flash();
    if ($f) echo '<p class="flash">' . h($f) . '</p>';
}

function foot_html() { echo '</main></body></html>'; }

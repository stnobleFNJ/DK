<?php
/* 모두의 작품 모음 관리: 사용자가 게임 결과 화면에서 올린 옷차림(전4-1)·공간(전4-2).
   보기는 모든 관리자, 삭제는 최고 관리자만(지우지 않고 view_state='D' → 게임 화면 목록에서 빠짐). */
require __DIR__ . '/lib.php';
$u = need_login();
$super = $u['role'] === 'super';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    need_login(true);
    check_csrf();
    $ids = [];
    foreach ((array)(isset($_POST['ids']) ? $_POST['ids'] : []) as $v) if (ctype_digit((string)$v)) $ids[(int)$v] = (int)$v;
    $ids = array_slice(array_values($ids), 0, 1000);
    if ($ids) {
        $n = q('UPDATE ' . T('gallery') . " SET view_state='D', deleted_at=?, deleted_by=? WHERE view_state<>'D' AND id IN (" . implode(',', array_fill(0, count($ids), '?')) . ')',
            array_merge([now(), $u['username']], $ids));
        flash($n . '개 작품을 삭제했습니다.');
    } else flash('삭제할 작품을 고르세요.');
    $back = isset($_POST['back']) && is_string($_POST['back']) ? $_POST['back'] : '';
    header('Location: gallery_admin.php' . ($back !== '' && !preg_match('/[\r\n#]/', $back) ? '?' . $back : ''));
    exit;
}

const G_GAMES = ['4-1' => '전2-1 나의 옷차림 꾸미기', '4-2' => '전2-2 나의 공간 아름답게 꾸미기'];
const G_NAMES = [
    'm' => ['top' => ['베이지 맨투맨', '초록 긴팔 티셔츠', '파란 반팔 티셔츠', '흰 셔츠'], 'bottom' => ['남색 반바지', '회색 반바지', '청바지', '베이지 바지'], 'shoes' => ['갈색 슬립온', '남색 운동화', '흰 운동화', '검정 구두']],
    'f' => ['top' => ['하늘색 블라우스', '노란 반팔 티셔츠', '흰 블라우스', '자주색 카디건'], 'bottom' => ['분홍 치마', '베이지 반바지', '검정 치마', '청바지'], 'shoes' => ['검정 샌들', '베이지 구두', '흰 운동화', '갈색 슬립온']],
];
const R_NAMES = ['curtain' => ['블랙 커튼', '와인 커튼', '화이트 커튼'], 'shelf' => ['블랙 책꽂이', '원목 책꽂이', '화이트 책꽂이'], 'bed' => ['블랙 침대', '빨간 꽃무늬 침대', '원목 침대'],
    'desk' => ['블랙 책상', '원목 책상', '화이트 책상'], 'closet' => ['블랙 옷장', '원목 옷장', '화이트 옷장'], 'table' => ['블랙 테이블', '원목 테이블', '화이트 테이블'], 'chair' => ['블랙 의자', '원목 의자', '화이트 의자']];

$game = isset($_GET['game']) && array_key_exists($_GET['game'], G_GAMES) ? $_GET['game'] : '';
$kw = isset($_GET['q']) ? mb_substr(trim((string)$_GET['q']), 0, 20, 'UTF-8') : '';
$page = max(1, isset($_GET['page']) ? (int)$_GET['page'] : 1);
$per = 60;
$w = ["view_state<>'D'"];
$a = [];
if ($game !== '') { $w[] = 'game=?'; $a[] = $game; }
if ($kw !== '') { $w[] = 'name LIKE ?'; $a[] = '%' . addcslashes($kw, '%_\\') . '%'; }
$where = ' WHERE ' . implode(' AND ', $w);
$total = (int)q('SELECT COUNT(*) n FROM ' . T('gallery') . $where, $a)[0]['n'];
$rows = q('SELECT id,game,name,data,ip,created_at FROM ' . T('gallery') . $where . ' ORDER BY id DESC LIMIT ' . (($page - 1) * $per) . ',' . $per, $a);
$back = $_SERVER['QUERY_STRING'] ?? '';

function desc($game, $d)
{
    if ($game === '4-1' && isset($d['g']) && array_key_exists($d['g'], G_NAMES)) {
        $n = G_NAMES[$d['g']];
        return ($d['g'] === 'm' ? '남자' : '여자') . ' · ' . $n['top'][$d['top'] - 1] . ', ' . $n['bottom'][$d['bottom'] - 1] . ', ' . $n['shoes'][$d['shoes'] - 1];
    }
    if ($game === '4-2' && isset($d['pick'])) {
        $o = [];
        foreach (R_NAMES as $k => $l) if (isset($d['pick'][$k])) $o[] = $l[$d['pick'][$k] - 1];
        return implode(' · ', $o);
    }
    return '';
}

head_html('작품 모음', $u, 'g');
?>
<h1>작품 모음 <small>게임 결과 화면에서 사용자가 올린 옷차림·공간</small></h1>
<form class="search card" method="get">
  <label class="wide">게임<select name="game"><option value="">전체</option><?php foreach (G_GAMES as $k => $v): ?><option value="<?= $k ?>" <?= $game === $k ? 'selected' : '' ?>><?= h($v) ?></option><?php endforeach ?></select></label>
  <label>이름<input name="q" value="<?= h($kw) ?>" maxlength="20" placeholder="이름 일부"></label>
  <div class="acts"><button class="btn pri">검색</button><a class="btn" href="gallery_admin.php">초기화</a></div>
</form>
<p>모두 <b><?= number_format($total) ?></b>개<?= $super ? ' · 삭제하면 게임 화면의 「모두의 … 보기」에서도 빠집니다(데이터는 남아 있음).' : '' ?></p>
<?php if ($super): ?>
<form method="post" id="gdel" onsubmit="return confirm('이 작품을 삭제할까요?')">
  <input type="hidden" name="csrf" value="<?= h(csrf()) ?>"><input type="hidden" name="back" value="<?= h($back) ?>">
</form>
<?php endif ?>
<div class="tbl">
<table class="list">
  <thead><tr><th>#</th><th>게임</th><th>그림</th><th>이름</th><th>고른 것</th><th>올린 때</th><th>IP</th><?php if ($super): ?><th></th><?php endif ?></tr></thead>
  <tbody>
  <?php if (!$rows): ?><tr><td colspan="<?= $super ? 8 : 7 ?>" class="empty">올라온 작품이 없습니다.</td></tr><?php endif ?>
  <?php foreach ($rows as $r): $d = json_decode($r['data'], true) ?: []; ?>
    <tr>
      <td class="n"><?= (int)$r['id'] ?></td>
      <td><?= h(array_key_exists($r['game'], G_GAMES) ? G_GAMES[$r['game']] : $r['game']) ?></td>
      <td><?php if ($r['game'] === '4-1' && isset($d['g'])): ?><img src="../games/4-1/img/look/<?= h($d['g'] . '-' . (int)$d['top'] . (int)$d['bottom'] . (int)$d['shoes']) ?>.jpg" alt="" style="height:90px;width:auto;border-radius:6px;background:#fff"><?php else: ?>—<?php endif ?></td>
      <td><b><?= h($r['name']) ?></b></td>
      <td><?= h(desc($r['game'], $d)) ?></td>
      <td><?= h(substr($r['created_at'], 0, 16)) ?></td>
      <td><?= h($r['ip']) ?></td>
      <?php if ($super): ?><td><button class="btn sm del" form="gdel" name="ids[]" value="<?= (int)$r['id'] ?>">삭제</button></td><?php endif ?>
    </tr>
  <?php endforeach ?>
  </tbody>
</table>
</div>
<?php $pages = (int)ceil($total / $per); if ($pages > 1): ?>
<nav class="pager"><?php for ($i = 1; $i <= $pages; $i++): ?><a class="<?= $i === $page ? 'on' : '' ?>" href="?<?= h(http_build_query(['game' => $game, 'q' => $kw, 'page' => $i])) ?>"><?= $i ?></a><?php endfor ?></nav>
<?php endif ?>
<?php foot_html();

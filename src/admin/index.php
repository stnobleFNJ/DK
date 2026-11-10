<?php
/* 게임 기록(설문 결과) 목록: 완료 여부·과정·게임·기간·검색어로 찾고, 어떤 칸으로든 정렬 */
require __DIR__ . '/lib.php';
require __DIR__ . '/filter.php';
$u = need_login();
$f = filters();
list($w, $a) = where($f);

$total = q('SELECT COUNT(*) n, SUM(status=\'done\') d, AVG(IF(status=\'done\',elapsed,NULL)) t FROM ' . T('play') . $w, $a)[0];
$pages = max(1, (int)ceil($total['n'] / $f['per']));
$f['page'] = min($f['page'], $pages);
$rows = q('SELECT id,sid,game,title,course,status,ip,ua,steps,elapsed,trail,result,data,started_at,updated_at,done_at,(snap IS NOT NULL AND LENGTH(snap) > 60) has_snap FROM ' . T('play') . $w . order_by($f) . ' LIMIT ' . (($f['page'] - 1) * $f['per']) . ',' . $f['per'], $a);
// 과정별 요약(검색 조건 중 과정·게임만 빼고 같게)
$fc = $f; $fc['course'] = ''; $fc['game'] = '';
list($wc, $ac) = where($fc);
$byCourse = [];
foreach (q('SELECT course, COUNT(*) n, SUM(status=\'done\') d FROM ' . T('play') . $wc . ' GROUP BY course', $ac) as $r) $byCourse[$r['course']] = $r;

$link = function ($chg) use ($f) {
    $p = array_merge($f, $chg);
    if (!isset($chg['page'])) $p['page'] = 1;
    return '?' . http_build_query(array_filter($p, function ($v) { return $v !== '' && $v !== null; }));
};
$th = function ($col, $label) use ($f, $link) {
    $on = $f['sort'] === $col;
    $dir = $on && $f['dir'] === 'desc' ? 'asc' : 'desc';
    return '<th><a href="' . h($link(['sort' => $col, 'dir' => $dir])) . '" class="' . ($on ? 'on ' . $f['dir'] : '') . '">' . h($label) . '</a></th>';
};
$games = games();
$super = $u['role'] === 'super';
$back = $_SERVER['QUERY_STRING'] ?? '';
$badge = ['done' => ['완료', 'ok'], 'play' => ['진행 중', 'pl'], 'exit' => ['중단', 'ex']];

head_html('게임 기록', $u, 'r');
?>
<h1>게임 기록 <small>게임을 할 때마다 한 줄씩 쌓여요</small></h1>

<section class="sum">
  <div><b><?= number_format($total['n']) ?></b><span>검색된 기록</span></div>
  <div><b><?= number_format($total['d']) ?></b><span>완료</span></div>
  <div><b><?= $total['n'] ? round($total['d'] / $total['n'] * 100) : 0 ?>%</b><span>완료율</span></div>
  <div><b><?= $total['t'] ? dur($total['t']) : '-' ?></b><span>평균 걸린 시간(완료)</span></div>
  <?php foreach (['전기', '중기', '후기'] as $c): $r = isset($byCourse[$c]) ? $byCourse[$c] : ['n' => 0, 'd' => 0]; ?>
    <div><b><?= number_format($r['n']) ?></b><span>성인 <?= $c ?> · 완료 <?= number_format($r['d']) ?></span></div>
  <?php endforeach ?>
</section>

<form class="search card" method="get">
  <label>완료 여부<select name="status"><option value="">전체</option>
    <?php foreach (STATUS as $k => $v): ?><option value="<?= $k ?>" <?= $f['status'] === $k ? 'selected' : '' ?>><?= h($v) ?></option><?php endforeach ?></select></label>
  <label>분야(과정)<select name="course"><option value="">전체</option>
    <?php foreach (['전기', '중기', '후기'] as $c): ?><option value="<?= $c ?>" <?= $f['course'] === $c ? 'selected' : '' ?>>성인 <?= $c ?></option><?php endforeach ?></select></label>
  <label class="wide">게임<select name="game"><option value="">전체</option>
    <?php foreach ($games as $k => $g): ?><option value="<?= h($k) ?>" <?= $f['game'] === $k ? 'selected' : '' ?>><?= h($g[0] . ' ' . $g[1]) ?></option><?php endforeach ?></select></label>
  <label>시작일<input type="date" name="from" value="<?= h($f['from']) ?>"></label>
  <label>종료일<input type="date" name="to" value="<?= h($f['to']) ?>"></label>
  <label class="wide">검색어<input name="q" value="<?= h($f['q']) ?>" placeholder="IP, 게임 이름, 고른 것, 결과 내용"></label>
  <label>정렬<select name="sort"><?php foreach (SORTS as $k => $v): ?><option value="<?= $k ?>" <?= $f['sort'] === $k ? 'selected' : '' ?>><?= h($v) ?></option><?php endforeach ?></select></label>
  <label>순서<select name="dir"><option value="desc">최근·큰 순</option><option value="asc" <?= $f['dir'] === 'asc' ? 'selected' : '' ?>>오래된·작은 순</option></select></label>
  <label>한 쪽에<select name="per"><?php foreach ([30, 50, 100, 300] as $n): ?><option <?= $f['per'] === $n ? 'selected' : '' ?>><?= $n ?></option><?php endforeach ?></select></label>
  <div class="acts"><button class="btn pri">검색</button><a class="btn" href="index.php">초기화</a>
    <a class="btn" href="export.php<?= h($link([])) ?>">엑셀(CSV) 내려받기</a></div>
</form>

<?php if ($super): ?>
<form method="post" action="delete.php" id="delf" class="delbar" onsubmit="return delSel(this)">
  <input type="hidden" name="csrf" value="<?= h(csrf()) ?>"><input type="hidden" name="back" value="<?= h($back) ?>">
  <span id="selc">0개 선택</span><button class="btn sm del" id="delbtn" disabled>선택한 기록 삭제</button>
  <small>삭제한 기록은 목록·요약·CSV에서 빠집니다(데이터는 남아 있음).</small>
</form>
<form method="post" action="delete.php" id="del1" onsubmit="return confirm('이 기록을 삭제할까요?')">
  <input type="hidden" name="csrf" value="<?= h(csrf()) ?>"><input type="hidden" name="back" value="<?= h($back) ?>">
</form>
<?php endif ?>
<div class="tbl">
<table class="list">
  <thead><tr><?php if ($super): ?><th class="ck"><input type="checkbox" id="ckall" aria-label="이 쪽 모두 고르기"></th><?php endif ?><th>#</th><?= $th('started_at', '시작 일시') ?><?= $th('course', '과정') ?><?= $th('game', '게임') ?><?= $th('status', '완료 여부') ?><?= $th('elapsed', '걸린 시간') ?><?= $th('steps', '화면 수') ?><?= $th('ip', 'IP') ?><?= $th('done_at', '완료 일시') ?><th>내용</th></tr></thead>
  <tbody>
  <?php if (!$rows): ?><tr><td colspan="<?= $super ? 11 : 10 ?>" class="empty">기록이 없습니다.</td></tr><?php endif ?>
  <?php foreach ($rows as $i => $r):
      $g = isset($games[$r['game']]) ? $games[$r['game']] : [$r['game'], $r['title']];
      $b = isset($badge[$r['status']]) ? $badge[$r['status']] : [$r['status'], ''];
      $trail = json_decode((string)$r['trail'], true) ?: [];
      $data = $r['data'] ? json_decode($r['data'], true) : null; ?>
    <tr>
      <?php if ($super): ?><td class="ck"><input type="checkbox" name="ids[]" value="<?= (int)$r['id'] ?>" form="delf" aria-label="기록 <?= (int)$r['id'] ?> 고르기"></td><?php endif ?>
      <td class="n"><?= number_format($total['n'] - (($f['page'] - 1) * $f['per'] + $i)) ?></td>
      <td class="dt"><?= h($r['started_at']) ?></td>
      <td><?= h($r['course']) ?></td>
      <td><b><?= h($g[0]) ?></b> <?= h($g[1]) ?></td>
      <td><span class="bd <?= $b[1] ?>"><?= h($b[0]) ?></span></td>
      <td class="n"><?= dur($r['elapsed']) ?></td>
      <td class="n"><?= (int)$r['steps'] ?></td>
      <td class="ip"><?= h($r['ip']) ?></td>
      <td class="dt"><?= h($r['done_at'] ?: '-') ?></td>
      <td class="cn"><?php if ($r['has_snap']): ?><button type="button" class="btn sm shot" data-id="<?= (int)$r['id'] ?>" data-t="<?= h($g[0] . ' ' . $g[1] . ' · ' . $r['started_at']) ?>">게임 결과 화면 보기</button><?php endif ?>
        <button type="button" class="btn sm dv" data-id="<?= (int)$r['id'] ?>">데이터 보기</button>
        <?php if ($super): ?><button class="btn sm del" form="del1" name="ids[]" value="<?= (int)$r['id'] ?>">삭제</button><?php endif ?>
        <template id="dv<?= (int)$r['id'] ?>">
          <h3 class="dvh"><?= h($g[0] . ' ' . $g[1]) ?> <span class="bd <?= $b[1] ?>"><?= h($b[0]) ?></span></h3>
          <section><h4>기본 정보</h4><dl class="kv">
            <dt>과정</dt><dd>성인 <?= h($r['course']) ?></dd>
            <dt>시작 일시</dt><dd><?= h($r['started_at']) ?></dd>
            <dt>완료 일시</dt><dd><?= h($r['done_at'] ?: '-') ?></dd>
            <dt>걸린 시간</dt><dd><?= dur($r['elapsed']) ?></dd>
            <dt>본 화면 수</dt><dd><?= (int)$r['steps'] ?>개</dd>
            <dt>IP</dt><dd><?= h($r['ip']) ?></dd>
          </dl></section>
          <?php if ($data): ?><section><h4>결과 값</h4><dl class="kv"><?php foreach (data_rows($data) as $k => $v): ?><dt><?= h($k) ?></dt><dd><?= h($v) ?></dd><?php endforeach ?></dl></section><?php endif ?>
          <section><h4>고른 것 <small>누른 순서 · <?= count($trail) ?>개</small></h4>
            <?php if ($trail): ?><ol class="trail"><?php foreach ($trail as $t): ?><li><?= h($t) ?></li><?php endforeach ?></ol><?php else: ?><p class="none">없음</p><?php endif ?></section>
          <section><h4>결과 화면 글</h4><?php if ($r['result']): ?><div class="rtext"><?php foreach (array_filter(array_map('trim', explode("\n", $r['result'])), 'strlen') as $ln): ?><p><?= h($ln) ?></p><?php endforeach ?></div><?php else: ?><p class="none"><?= $r['status'] === 'done' ? '저장된 글이 없습니다.' : '아직 결과 화면까지 가지 않았습니다.' ?></p><?php endif ?></section>
          <p class="ua">기록 번호 <?= (int)$r['id'] ?> · 세션 <?= h($r['sid']) ?> · 마지막 기록 <?= h($r['updated_at']) ?><br><?= h($r['ua']) ?></p>
        </template></td>
    </tr>
  <?php endforeach ?>
  </tbody>
</table>
</div>

<div id="shotdlg" class="shotdlg" role="dialog" aria-modal="true" aria-labelledby="shott" hidden>
  <div class="shotbox">
    <div class="dvhd"><b id="shott">게임 결과 화면</b><button type="button" class="btn sm" id="shotx">닫기 ✕</button></div>
    <iframe id="shotf" title="게임 결과 화면" sandbox referrerpolicy="no-referrer"></iframe>
  </div>
</div>
<dialog id="datadlg" class="datadlg" aria-label="데이터 보기">
  <div class="dvhd"><b>데이터 보기</b><button type="button" class="btn sm" id="datax">닫기 ✕</button></div>
  <div id="datab" class="dvb"></div>
</dialog>
<script>
// 게임 결과 화면 보기: 팝업(PC는 데이터 보기와 같은 크기, 휴대폰은 전체 화면)에 저장된 결과 화면(snapshot.php)을 연다. iframe은 sandbox라 스크립트가 돌지 않는다.
(function(){
  // <dialog>는 전체 화면이 안 되므로 일반 레이어(div)로 띄운다.
  var d=document.getElementById('shotdlg'),f=document.getElementById('shotf'),mobile=matchMedia('(max-width:640px)');
  function closeShot(){if(d.hidden)return;d.hidden=true;f.src='about:blank';document.body.style.overflow='';
    if(document.fullscreenElement)document.exitFullscreen().catch(function(){})}
  document.querySelectorAll('.shot').forEach(function(b){b.onclick=function(){
    document.getElementById('shott').textContent=b.dataset.t;f.src='snapshot.php?id='+b.dataset.id;
    d.hidden=false;document.body.style.overflow='hidden';
    // PC: 데이터 보기와 같은 크기의 창 · 휴대폰: 전체 화면(막히면 화면 전체를 덮는 창)
    if(mobile.matches)try{var r=d.requestFullscreen||d.webkitRequestFullscreen;if(r){var pr=r.call(d);if(pr&&pr.catch)pr.catch(function(){})}}catch(e){}
    document.getElementById('shotx').focus()}});
  document.getElementById('shotx').onclick=closeShot;
  d.addEventListener('click',function(e){if(e.target===d)closeShot()});  // 창 바깥을 누르면 닫기
  document.addEventListener('fullscreenchange',function(){if(!document.fullscreenElement)closeShot()});  // ESC로 전체 화면을 끄면 함께 닫기
  document.addEventListener('keydown',function(e){if(e.key==='Escape')closeShot()});
  // 기록 삭제(최고 관리자): 체크한 개수 표시, 모두 고르기
  var all=document.getElementById('ckall');
  if(all){var cks=document.querySelectorAll('input[name="ids[]"][form=delf]'),cnt=function(){var n=0;cks.forEach(function(c){if(c.checked)n++});
      document.getElementById('selc').textContent=n+'개 선택';document.getElementById('delbtn').disabled=!n;all.checked=n&&n===cks.length};
    all.onchange=function(){cks.forEach(function(c){c.checked=all.checked});cnt()};cks.forEach(function(c){c.onchange=cnt});}
  window.delSel=function(f){var n=f.querySelectorAll?document.querySelectorAll('input[name="ids[]"][form=delf]:checked').length:0;return n&&confirm(n+'개 기록을 삭제할까요?')};
  // 데이터 보기: 줄마다 들어 있는 <template>을 팝업에 옮겨 보여 준다
  var dd=document.getElementById('datadlg'),db=document.getElementById('datab');
  document.querySelectorAll('.dv').forEach(function(b){b.onclick=function(){
    db.innerHTML='';db.appendChild(document.getElementById('dv'+b.dataset.id).content.cloneNode(true));dd.showModal();db.scrollTop=0}});
  document.getElementById('datax').onclick=function(){dd.close()};
  dd.addEventListener('click',function(e){if(e.target===dd)dd.close()});
})();
</script>

<?php if ($pages > 1): ?>
<nav class="pager">
  <?php for ($p = max(1, $f['page'] - 5); $p <= min($pages, $f['page'] + 5); $p++): ?>
    <a href="<?= h($link(['page' => $p])) ?>" class="<?= $p === $f['page'] ? 'on' : '' ?>"><?= $p ?></a>
  <?php endfor ?>
  <span><?= $f['page'] ?> / <?= $pages ?>쪽</span>
</nav>
<?php endif ?>
<?php foot_html();

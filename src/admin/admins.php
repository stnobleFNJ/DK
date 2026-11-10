<?php
/* 관리자 관리(최고 관리자만): 한 페이지에서 등록 · 수정 · 삭제 */
require __DIR__ . '/lib.php';
$u = need_login(true);
$A = T('admin');

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    check_csrf();
    $p = function ($k) { return isset($_POST[$k]) && is_string($_POST[$k]) ? trim($_POST[$k]) : ''; };
    $do = $p('do');
    $role = $p('role') === 'super' ? 'super' : 'admin';
    $supers = function () use ($A) { return (int)q("SELECT COUNT(*) n FROM $A WHERE role='super'")[0]['n']; };
    $pwOk = function ($pw) { return strlen($pw) >= 4 && strlen($pw) <= 72; };

    if ($do === 'add') {
        $id = $p('username');
        $pw = isset($_POST['password']) ? (string)$_POST['password'] : '';
        if (!preg_match('/^[A-Za-z0-9_.-]{2,40}$/', $id)) flash('아이디는 영문·숫자·_ . - 로 2~40자로 써 주세요.');
        elseif (!$pwOk($pw)) flash('비밀번호는 4자 이상으로 써 주세요.');
        elseif (q("SELECT id FROM $A WHERE username=?", [$id])) flash("이미 있는 아이디입니다: $id");
        else {
            q("INSERT INTO $A (username,pass,name,role,created_at,updated_at) VALUES (?,?,?,?,?,?)",
                [$id, password_hash($pw, PASSWORD_DEFAULT), mb_substr($p('name'), 0, 50, 'UTF-8'), $role, now(), now()]);
            flash("관리자 '$id'을(를) 등록했습니다.");
        }
    } elseif ($do === 'edit' || $do === 'del') {
        $tid = (int)$p('id');
        $t = q("SELECT * FROM $A WHERE id=?", [$tid]);
        if (!$t) flash('없는 관리자입니다.');
        else {
            $t = $t[0];
            if ($do === 'del') {
                if ($tid === (int)$u['id']) flash('지금 로그인한 계정은 삭제할 수 없습니다.');
                elseif ($t['role'] === 'super' && $supers() <= 1) flash('최고 관리자가 한 명뿐이라 삭제할 수 없습니다.');
                else { q("DELETE FROM $A WHERE id=?", [$tid]); flash("관리자 '{$t['username']}'을(를) 삭제했습니다."); }
            } else {
                $pw = isset($_POST['password']) ? (string)$_POST['password'] : '';
                if ($t['role'] === 'super' && $role !== 'super' && $supers() <= 1) flash('최고 관리자가 한 명뿐이라 일반 관리자로 바꿀 수 없습니다.');
                elseif ($pw !== '' && !$pwOk($pw)) flash('비밀번호는 4자 이상으로 써 주세요.');
                else {
                    q("UPDATE $A SET name=?, role=?, updated_at=? WHERE id=?", [mb_substr($p('name'), 0, 50, 'UTF-8'), $role, now(), $tid]);
                    if ($pw !== '') q("UPDATE $A SET pass=? WHERE id=?", [password_hash($pw, PASSWORD_DEFAULT), $tid]);
                    flash("관리자 '{$t['username']}'을(를) 수정했습니다." . ($pw !== '' ? ' (비밀번호 변경)' : ''));
                }
            }
        }
    }
    header('Location: admins.php');
    exit;
}

$list = q("SELECT id,username,name,role,created_at,updated_at,last_login FROM $A ORDER BY role='super' DESC, id");
$tok = h(csrf());
head_html('관리자 관리', $u, 'a');
?>
<h1>관리자 관리 <small>등록 · 수정 · 삭제를 이 화면에서 해요</small></h1>

<form method="post" class="card add" autocomplete="off">
  <h2>새 관리자 등록</h2>
  <input type="hidden" name="csrf" value="<?= $tok ?>"><input type="hidden" name="do" value="add">
  <label>아이디<input name="username" required pattern="[A-Za-z0-9_.\-]{2,40}" placeholder="영문·숫자"></label>
  <label>비밀번호<input name="password" type="password" required minlength="4" autocomplete="new-password"></label>
  <label>이름<input name="name" maxlength="50" placeholder="예: 홍길동"></label>
  <label>권한<select name="role"><option value="admin">일반 관리자(기록 보기)</option><option value="super">최고 관리자(관리자 관리 가능)</option></select></label>
  <div class="acts"><button class="btn pri">등록</button></div>
</form>

<div class="tbl">
<table class="list admins">
  <thead><tr><th>아이디</th><th>이름</th><th>권한</th><th>새 비밀번호</th><th>등록일</th><th>마지막 로그인</th><th></th></tr></thead>
  <tbody>
  <?php foreach ($list as $r): $f = 'f' . $r['id']; $self = (int)$r['id'] === (int)$u['id']; ?>
    <tr>
      <td><b><?= h($r['username']) ?></b><?= $self ? ' <span class="bd pl">나</span>' : '' ?></td>
      <td><input form="<?= $f ?>" name="name" value="<?= h($r['name']) ?>" maxlength="50"></td>
      <td><select form="<?= $f ?>" name="role"><option value="admin">일반 관리자</option><option value="super" <?= $r['role'] === 'super' ? 'selected' : '' ?>>최고 관리자</option></select></td>
      <td><input form="<?= $f ?>" name="password" type="password" placeholder="바꿀 때만 입력" minlength="4" autocomplete="new-password"></td>
      <td class="dt"><?= h(substr($r['created_at'], 0, 10)) ?></td>
      <td class="dt"><?= h($r['last_login'] ?: '-') ?></td>
      <td class="row-acts">
        <form id="<?= $f ?>" method="post"><input type="hidden" name="csrf" value="<?= $tok ?>"><input type="hidden" name="id" value="<?= (int)$r['id'] ?>"><input type="hidden" name="do" value="edit"><button class="btn sm pri">수정</button></form>
        <?php if (!$self): ?><form method="post" onsubmit="return confirm('관리자 \'<?= h($r['username']) ?>\'을(를) 삭제할까요?')"><input type="hidden" name="csrf" value="<?= $tok ?>"><input type="hidden" name="id" value="<?= (int)$r['id'] ?>"><input type="hidden" name="do" value="del"><button class="btn sm del">삭제</button></form><?php endif ?>
      </td>
    </tr>
  <?php endforeach ?>
  </tbody>
</table>
</div>
<p class="ua">사용 중인 데이터베이스: <b><?= h($GLOBALS['DK_DB_IN_USE']) ?></b> · 표: <?= h(cfg('prefix')) ?>play(게임 기록), <?= h(cfg('prefix')) ?>admin(관리자)</p>
<?php foot_html();

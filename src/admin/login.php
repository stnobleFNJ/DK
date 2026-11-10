<?php
require __DIR__ . '/lib.php';
start_session();
db();  // 처음 접속 때 DB·표·최고 관리자(dk) 준비
if (me()) { header('Location: index.php'); exit; }

$err = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    check_csrf();
    $id = trim((string)(isset($_POST['username']) ? $_POST['username'] : ''));
    $pw = (string)(isset($_POST['password']) ? $_POST['password'] : '');
    $r = $id !== '' ? q('SELECT id,pass FROM ' . T('admin') . ' WHERE username=?', [$id]) : [];
    if ($r && password_verify($pw, $r[0]['pass'])) {
        session_regenerate_id(true);
        $_SESSION['aid'] = (int)$r[0]['id'];
        q('UPDATE ' . T('admin') . ' SET last_login=? WHERE id=?', [now(), (int)$r[0]['id']]);
        if ($id === 'dk' && $pw === 'dk1234') flash('처음 비밀번호(dk1234)를 쓰고 있어요. 관리자 관리에서 비밀번호를 바꿔 주세요.');
        header('Location: index.php');
        exit;
    }
    usleep(800000);  // 비밀번호 대입을 느리게
    $err = '아이디 또는 비밀번호가 맞지 않습니다.';
}
head_html('로그인');
?>
<form method="post" class="login card">
  <img class="lg" src="../games/common/dku-logo.png" alt="단국대학교">
  <h1>관리자 로그인</h1>
  <input type="hidden" name="csrf" value="<?= h(csrf()) ?>">
  <label>아이디<input name="username" autocomplete="username" required autofocus value="<?= h(isset($_POST['username']) ? $_POST['username'] : '') ?>"></label>
  <label>비밀번호<input name="password" type="password" autocomplete="current-password" required></label>
  <?php if ($err): ?><p class="err"><?= h($err) ?></p><?php endif ?>
  <button class="btn pri">로그인</button>
</form>
<?php foot_html();

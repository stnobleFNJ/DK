<?php
/* 관리자 설정 — 이 파일을 config.php로 복사해 값을 채운다. config.php는 git에 올리지 않는다(.gitignore). */
if (!defined('DK_ADMIN')) exit;

return [
    // MySQL(MariaDB) 접속 정보. cafe24는 보통 host=localhost, user=호스팅 아이디, 비밀번호=DB 비밀번호
    'db_host' => 'localhost',
    'db_user' => '',
    'db_pass' => '',
    'db_port' => 3306,
    // 쓸 데이터베이스. 없으면 만든다(CREATE DATABASE). 만들 권한이 없으면 db_fallback을 쓴다.
    'db_name' => 'DK_game',
    // 데이터베이스를 새로 만들 수 없는 호스팅(cafe24 등)에서 쓸 기존 DB 이름(보통 호스팅 아이디). 비우면 db_name만 쓴다.
    'db_fallback' => '',
    // 표 이름 앞에 붙는 말(같은 DB를 다른 사이트와 함께 쓸 때 겹치지 않게)
    'prefix' => 'dk_',
    // 처음 만들 최고 관리자(관리자 표가 비어 있을 때만 만든다)
    'first_admin' => ['dk', 'dk1234'],
    'timezone' => 'Asia/Seoul',
];

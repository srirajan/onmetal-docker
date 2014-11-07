#!/usr/bin/env bash

cat > /usr/share/nginx/html/db.php <<EOF
<?php
include("/usr/share/nginx/html/db_host.php");
\$db_host  = get_db_host();
\$db_user  = "${APP_USER}";
\$db_password  = "${APP_PW}";
\$db_name  = "${APP_DB_NAME}";
?>
EOF

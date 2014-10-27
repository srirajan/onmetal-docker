#!/usr/bin/env bash

cat > /usr/share/nginx/html/db.php <<EOF
<?php
\$db_host  = "db";
\$db_user  = "${APP_USER}";
\$db_password  = "${APP_PW}";
\$db_name  = "${APP_DB_NAME}";
?>
EOF

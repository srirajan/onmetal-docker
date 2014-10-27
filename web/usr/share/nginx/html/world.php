<link rel="stylesheet" type="text/css" href="styles.css">

<?php

include_once "/srv/www/db.php";

// Connecting, selecting database
$link = mysql_connect( $db_host, $db_user, $db_password)
    or die('Could not connect: ' . mysql_error());
mysql_select_db($db_name) or die('Could not select database');


/* show tables */
$result = mysql_query('SELECT * FROM City',$link) or die('cannot show tables');
		echo '<table cellpadding="0" cellspacing="0" class="db-table">';
		echo '<tr><th>Field</th><th>Type</th><th>Null</th><th>Key</th><th>Default<th>Extra</th></tr>';
while($row2 = mysql_fetch_row($result)) {
			echo '<tr>';
			foreach($row2 as $key=>$value) {
				echo '<td>',$value,'</td>';
			}
			echo '</tr>';
		}
		echo '</table><br />';

?>
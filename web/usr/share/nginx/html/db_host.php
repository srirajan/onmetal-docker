<?php 

function get_db_host() {
	$etcd_url = "http://etcd_host:4001/v2/keys/services/db/db_private_ip";
	$contents = file_get_contents($etcd_url); 
	$contents = utf8_encode($contents); 
	$results = json_decode($contents); 
        $res = json_decode($results->node->value);
        return($res->value);
}
?>



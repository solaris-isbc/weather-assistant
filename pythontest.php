<?php
    error_reporting(-1);
    ini_set("display_errors", 1);

	$locale='de_DE.UTF-8';
	setlocale(LC_ALL,$locale);
	putenv('LC_ALL='.$locale);
	exec('locale charmap');


    // Allow from any origin
    if (isset($_SERVER['HTTP_ORIGIN'])) {
        // Decide if the origin in $_SERVER['HTTP_ORIGIN'] is one
        // you want to allow, and if so:
        header("Access-Control-Allow-Origin: {$_SERVER['HTTP_ORIGIN']}");
        header('Access-Control-Allow-Credentials: true');
    }

    if(isset($_REQUEST["query"])){
	$query = $_REQUEST["query"];
	//$query = str_replace("%20", " ", $query);
	//echo $query;


        $params = preg_replace('/[^\da-zA-ZÖÄÜäöüß,\.;:\-\/\s?]/', '', $query);
        $shell_cmd = "/var/www/html/nlp/venv/bin/python3.6 -v run_assistant.py \"" . $params . "\"";

//	echo $shell_cmd;	
	exec($shell_cmd, $out, $retval);
	if($retval == 0) {
		foreach($out as $o){
			echo $o;
		}
	}else{
		echo "Es ist ein Fehler aufgetreten :(";
	}
	//system($shell_cmd);
    }else{
	echo "Keine Query angegeben :(";
    }

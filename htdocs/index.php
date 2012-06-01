<fieldset style="width: 300px;">
<legend>F3L W-LAN Database</legend>
	<center>
	<title>F3L W-LAN Database</title>
	<a href="/files">KML List</a> - <a href="/map.php">View Map</a><br />
	<a href="/db/all.kml">ALL</a> - <a href="/db/wep.kml">WEP</a> - <a href="/db/open.kml">OPEN</a><br />
	<a href="/cgi-bin/highscore.py">Highscore</a>
	<br /><br />
	<form method="post" enctype="multipart/form-data" action="/cgi-bin/upload.py">
		<input type="file" name="file" id="file" />
		<br /><br />
		<input type="submit" value="Upload" />
	</form>
	<?php echo file_get_contents('db/count.txt'); ?> Networks in Database
	</center>
</fieldset>

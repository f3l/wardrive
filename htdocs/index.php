<fieldset style="width: 300px;">
<legend>F3L W-LAN Database</legend>
	<center>
	<title>F3L W-LAN Database</title>
	<a href="/files">KML List</a> - <a href="http://maps.google.de/?q=http%3A%2F%2Ftest.de%2Fall.kml">View Map</a><br />
	<a href="/all.kml">ALL</a> - <a href="http://maps.google.de/?q=http%3A%2F%2Ftest.de%2Fwep.kml">WEP</a> - <a href="http://maps.google.de/?q=http%3A%2F%2Ftest.de%2Fopen.kml">OPEN</a><br />
	<a href="/cgi-bin/highscore.py">Highscore</a>
	<br /><br />
	<form method="post" enctype="multipart/form-data" action="/cgi-bin/upload.py">
		<input type="file" name="file" id="file" />
		<br /><br />
		<input type="submit" value="Upload" />
	</form>
	<?php echo file_get_contents('count.txt'); ?> Networks in Database
	</center>
</fieldset>

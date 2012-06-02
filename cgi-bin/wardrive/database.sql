CREATE TABLE IF NOT EXISTS `networks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `bssid` varchar(17) COLLATE utf8_unicode_ci NOT NULL,
  `ssid` varchar(32) COLLATE utf8_unicode_ci NOT NULL,
  `channel` int(11) NOT NULL DEFAULT '0',
  `level` int(11) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `encryption` enum('OPEN','WEP','WPA','WPS','IBSS') COLLATE utf8_unicode_ci NOT NULL,
  `lon` float(11,9) NOT NULL,
  `lat` float(11,9) NOT NULL,
  `height` int(11) NOT NULL,
  `psk` varchar(512) COLLATE utf8_unicode_ci NOT NULL,
  `hacked` enum('NO','YES','FAILED') COLLATE utf8_unicode_ci NOT NULL,
  `scanned_by` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  `hacked_by` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  `internet_access` enum('UNKNOWN','YES','NO') COLLATE utf8_unicode_ci NOT NULL,
  `private` enum('UNKNOWN','YES','NO') COLLATE utf8_unicode_ci NOT NULL,
  `comment` text COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `bssid` (`bssid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;

delimiter //
-- DROP PROCEDURE geodist;
-- //

-- returns the 10 nearest networks within /dist/ miles radius
-- eg: CALL geodist(49.7152, 11.6472, 10, 1);
CREATE PROCEDURE geodist(mylat float, mylon float, dist float, mylimit integer)
BEGIN
declare lon1 float;
declare lon2 float;
declare lat1 float;
declare lat2 float;

SET SQL_SELECT_LIMIT = mylimit;

-- calculate lon and lat for the rectangle:
SET lon1 = mylon - dist/ABS(COS(RADIANS(mylat))*69);
SET lon2 = mylon+dist/abs(cos(radians(mylat))*69);
SET lat1 = mylat-(dist/69);
SET lat2 = mylat+(dist/69);

-- run the query:
SELECT *, 3956 * 2 * ASIN(SQRT( POWER(SIN((mylat - lat) * pi()/180 / 2), 2) +
COS(mylat * pi()/180) * COS(lat * pi()/180) *
POWER(SIN((mylon - lon) * pi()/180 / 2), 2) )) as distance
FROM networks
WHERE lon between lon1 and lon2
and lat between lat1 and lat2
having distance < dist ORDER BY distance;

SET SQL_SELECT_LIMIT = DEFAULT;

END;
//
delimiter ;

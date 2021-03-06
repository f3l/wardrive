#!/usr/bin/python
# -*- coding: utf-8 -*-

# algorythm from http://matheplanet.com/matheplanet/nuke/html/viewtopic.php?topic=139705

x = 'x'
y = 'y'
r = 'r'

# remember:
# x = longitude
# y = latutude
# r = radius

def trilaterate(ap):
	"""
	myaps = [
		{y: 49.751399994,   x: 11.541473389,   r: 1},
		{y: 49.751811981,   x: 11.542001724,   r: 1},
		{y: 49.751602173,   x: 11.540295601,   r: 1},
	]

	print trilaterate(myaps)
	"""

	delta = 4 * ( 
		(ap[0][x]-ap[1][x]) * (ap[0][y]-ap[2][y]) -
		(ap[0][x]-ap[2][x]) * (ap[0][y]-ap[1][y])
	) 

	A = pow(ap[1][r],2) - pow(ap[0][r],2) - pow(ap[1][x],2) + pow(ap[0][x],2) - pow(ap[1][y],2) + pow(ap[0][y],2)
	B = pow(ap[2][r],2) - pow(ap[0][r],2) - pow(ap[2][x],2) + pow(ap[0][x],2) - pow(ap[2][y],2) + pow(ap[0][y],2) 

	x0 = (1/delta) * ( 2*A*(ap[0][y]-ap[2][y]) - 2*B*(ap[0][y] - ap[1][y]) )
	y0 = (1/delta) * ( 2*B*(ap[0][x]-ap[1][x]) - 2*A*(ap[0][x] - ap[2][x]) )

	return ([y0, x0, 3])

def bilaterate(ap):
	"""
	myaps = [
		{y: 49.751399994,   x: 11.541473389,   r: 1},
		{y: 49.751811981,   x: 11.542001724,   r: 1},
	]

	print bilaterate(myaps)
	"""

	delta = {}
	delta[x] = ap[1][x] - ap[0][x]
	delta[y] = ap[1][y] - ap[0][y]

	ratio = ap[0][r] / float( ap[0][r] + ap[1][r] )
	delta[x] *= ratio
	delta[y] *= ratio

	x0 = ap[0][x] + delta[x]
	y0 = ap[0][y] + delta[y]

	return ([y0, x0, 2])

def unilaterate(ap):
	"""
	myaps = [
		{y: 49.751399994,   x: 11.541473389,   r: 1},
	]

	print unilaterate(myaps)
	"""

	return ([ap[0][y], ap[0][x], 1])

def laterate(ap):
	"""
	myaps = [
		{y: 49.751399994,   x: 11.541473389,   r: 1},
		{y: 49.751811981,   x: 11.542001724,   r: 1},
		{y: 49.751602173,   x: 11.540295601,   r: 1},
		...
	]

	print laterate(myaps)
	"""

	apc = len(ap)

	if apc >= 3:
		return trilaterate(sorted(ap, key=lambda k: k['r'])[:3])
	elif apc == 2:
		return bilaterate(ap)
	else:
		return unilaterate(ap)

# 0.00120048° = 100m
# 0,000012005° = 1m
# r = | dB |
# 0 <= r < 100
# r = r * 0,000012005
def wifipos(networks, ap):
	"""
	networks = Wardrive().networks
	myaps = [
		{'mac': '00:00:DE:AD:BE:EF', 'signal': -30},
		...
		...
	]

	print wifipos(networks, myaps)
	"""

	pap = []
	for apt in ap:
		daps = networks.get({'bssid': apt['mac'].lower()}, index=True)
		try:
			dap = daps.pop()
			if dap['adhoc']:
				continue
			signal = abs(apt['signal'])
			if signal >= 100:
				signal = 99
			if signal < 1:
				signal = 1
			rsignal = signal * 0.000002005
			try:
				conflict_item = next(index for (index, lap) in enumerate(pap) if lap['x'] == dap['lon'] and lap['y'] == dap['lat'])
				if pap[conflict_item][r] > rsignal:
					pap[conflict_item][r] = rsignal
			except:
				pap.append({
					x: dap['lon'],
					y: dap['lat'],
					r: rsignal,
				})
		except:
			pass
	pos = laterate(pap)
	return {'lat': pos[0], 'lon': pos[1], 'netcount': pos[2]}

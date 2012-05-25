#!/usr/bin/python
# -*- coding: utf-8 -*-

# algorythm from http://www.matheplanet.com/default3.html?call=viewtopic.php?topic=139705

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

	return ([y0, x0])

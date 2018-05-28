#!/usr/bin/python

import sys
from PIL import Image
import numpy
import math

class Function:
	equation = "math.cos(y*x) * math.sin(x) * x"
	xmin = -10.
	ymin = -10.
	xmax = 10.
	ymax = 10.
	xres = 1000
	yres = 1000
	normalize = False
	raw = False
	scaler = 65535

	options = ["equation", "xmin", "ymin", "xmax", "ymax", "xres", "yres", "scaler"]

	def __init__(self, *argv, **kwargs):
		for arg in argv:
			if arg == "raw":
				self.raw = True
			if arg == "normalize":
				self.normalize = True
		for key, value in kwargs.iteritems():
			if key in self.options:
				setattr(self, key, value)
			else:
				print "Didn't recognize option: " + str(key)				
		

class Palette:
	a_r = 0.46
	a_g = 0.5
	a_b = 0.15
	b_r = 0.34
	b_g = 0.47
	b_b = 0.43
	c_r = 1.5
	c_g = 0.0
	c_b = 0.5
	d_r = 0.1
	d_g = 0.64
	d_b = 0.48

# returns RGBA value for Numpy array
def color_pixel(t, p):
	red = 255.* (p.a_r + p.b_r * math.cos(6.2832 * (p.c_r * t + p.d_r)))
	grn = 255.* (p.a_g + p.b_g * math.cos(6.2832 * (p.c_g * t + p.d_g)))
	blu = 255.* (p.a_b + p.b_b * math.cos(6.2832 * (p.c_b * t + p.d_b)))
	return 0xff << 24 | int(blu) << 16 | int(grn) << 8 | int(red)

# returns RGBA value for Numpy array
def raw_pixel(t, s):
	return 0xff << 24 | ((int(t * s) & 0x00FFFFFF))

# translate pixel address to Cartesian coordinates
# and calls eval on a string with an equation in terms of x and y
def solve(x0, y0, f):
	x = f.xmax - ( ( float(x0) / float(f.xres) ) * ( f.xmax - f.xmin ) )
	y = f.ymax - ( ( float(y0) / float(f.yres) ) * ( f.ymax - f.ymin ) )
	return eval(f.equation)

if __name__ == "__main__":

	kwargs = {"xres":1500, "yres":1500}

	func = Function(**kwargs)
	pal  = Palette()

	grid = numpy.zeros((func.xres,func.yres), numpy.uint32)
	grid.shape = func.xres, func.yres

	canvas = numpy.zeros(grid.shape, numpy.float32)
	canvas.shape = grid.shape

	max_val = 0.0
	for x in xrange(canvas.shape[0]):
		for y in xrange(canvas.shape[1]):
			canvas[x][y] = solve(x, y, func)
			max_val = max(max_val, canvas[x][y])

	if max_val == 0.0 or not func.normalize:
		max_val = 1.0

	for x in xrange(grid.shape[0]):
		for y in xrange(grid.shape[1]):
			grid[x][y] = ( color_pixel(canvas[x][y] / max_val, pal),
						   raw_pixel(  canvas[x][y] / max_val, func.scaler) )[func.raw]

	image = Image.frombuffer('RGBA', grid.shape, numpy.uint32(grid), 'raw', 'RGBA', 0, 1)
	image.save("function.png")



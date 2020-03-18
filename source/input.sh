resetCanvas 900 900
setColor 0 255 0
# drawEllipse ecp 50 100 250 200
# drawPolygon DDsA 200 200 300 200 250 100 Bresenham
drawCurve line1 200 500 300 100 700 100 400 500 600 700 800 400 700 200 B-spline
# drawLine line1 100 60 500 210 DDA
# drawLine ecp 100 50 500 200 Bresenham
# drawLine line19 100 40 500 190 Naive
# drawLine line12 100 50 100 200 Bresenham
# drawLine line13 100 50 500 500 Bresenham
# drawLine line14 100 200 500 500 Bresenham
saveCanvas 1
# setColor 255 0 0
# drawLine line2 400 0 400 500 DDA
# drawLine line3 0 200 500 200 DDA
# clip line1 200 0 500 200 Liang-Barsky
# translate ecp 0 -100
# rotate ecp 300 300 45
# scale ecp 150 150 2
# setColor 255 0 0
# drawLine 666 200 300 400 150 Naive
# saveCanvas 2

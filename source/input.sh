# resetCanvas 900 900
# setColor 0 255 0
# drawEllipse ecp 50 100 250 200
# drawPolygon DDsA 200 200 300 200 250 100 Bresenham
# drawCurve line1 200 500 300 100 700 100 400 500 600 700 800 400 700 200 B-spline
# drawLine line1 100 60 500 210 DDA
# drawLine Line0 104 143 279 337 Naive
# drawLine ecp 100 50 500 200 Bresenham
# drawLine line19 100 40 500 190 Naive
# drawLine line12 100 50 100 200 Bresenham
# drawLine line13 100 50 500 500 Bresenham
# drawLine line14 100 200 500 500 Bresenham
# saveCanvas 1
# setColor 255 0 0
# drawLine line2 400 0 400 500 DDA
# drawLine line3 0 200 500 200 DDA
# clip line1 200 0 500 200 Liang-Barsky
# translate ecp 0 -100
# rotate ecp 300 300 45
# scale ecp 150 150 2
# setColor 255 0 0
# drawLine 666 200 300 400 150 Naive
# translate line1 150 150
# saveCanvas 2
resetCanvas 400 600
drawCurve c1 50 50 75 75 100 125 125 200 150 275 175 375 200 500 B-spline
drawCurve c2 50 100 75 125 100 175 125 250 150 325 175 425 200 550 Bezier
setColor 205 0 50
drawLine l1 50 50 200 50 DDA
drawLine l2 50 100 200 100 DDA
drawLine l3 50 150 200 150 DDA
drawLine l4 50 200 200 200 DDA
drawLine l5 50 250 200 250 DDA
drawLine l6 50 300 200 300 DDA
drawLine l7 50 350 200 350 DDA
drawLine l8 50 400 200 400 DDA
drawLine l9 50 450 200 450 DDA
drawLine l0 50 500 200 500 DDA
saveCanvas yls1
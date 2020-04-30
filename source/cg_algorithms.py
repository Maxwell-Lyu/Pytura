#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 本文件只允许依赖math库
import math

def sign(num):
    if num > 0:
        return 1
    if num < 0:
        return -1
    return 0

def draw_line(p_list, algorithm):
    """绘制线段

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'，此处的'Naive'仅作为示例，测试时不会出现
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    result = []
    if algorithm == 'Naive':
        if x0 == x1:
            for y in range(min(y0, y1), max(y0, y1) + 1):
                result.append((x0, y))
        else:
            if x0 > x1:
                x0, y0, x1, y1 = x1, y1, x0, y0
            k = (y1 - y0) / (x1 - x0)
            for x in range(min(x0, x1), max(x0, x1) + 1):
                result.append((x, round(y0 + k * (x - x0))))
    elif algorithm == 'DDA':
        length = max(abs(y1 - y0), abs(x1 - x0))
        if length == 0: 
            result.append((x0, y0))
        else:
            dx = (x1 - x0) / length
            dy = (y1 - y0) / length
            i = 1
            x, y = x0, y0
            while i <= length:
                result.append((round(x), round(y)))
                x += dx
                y += dy
                i += 1
    elif algorithm == 'Bresenham':
        x = x0
        y = y0
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        s1 = sign(x1 - x0)
        s2 = sign(y1 - y0)
        interchange = (dy > dx)
        if interchange:
            dx, dy = dy, dx
        e = 2 * dy - dx
        for i in range(dx):
            result.append((x, y))
            if e > 0:
                if interchange:
                    x += s1
                else:
                    y += s2
                e = e - 2 * dx
            if interchange:
                y = y + s2
            else:
                x = x + s1
            e = e + 2 * dy
        result.append((x1, y1))
    return result


def draw_polygon(p_list, algorithm):
    """绘制多边形

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 多边形的顶点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    if len(p_list) == 2:
        return draw_line([p_list[0], p_list[1]], algorithm)
    result = []
    for i in range(len(p_list)):
        line = draw_line([p_list[i - 1], p_list[i]], algorithm)
        result += line
    return result


def draw_ellipse(p_list):
    """绘制椭圆（采用中点圆生成算法）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 椭圆的矩形包围框左上角和右下角顶点坐标
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    a = abs(x1 - x0) / 2
    b = abs(y1 - y0) / 2
    center = [round((x0 + x1)/2), round((y0 + y1)/2)]

    result = []
    x = round(a)
    y = round(0)
    taa = a * a
    t2aa = 2 * taa
    t4aa = 2 * t2aa
    tbb = b * b
    t2bb = 2 * tbb
    t4bb = 2 * t2bb
    t2abb = a * t2bb
    t2bbx = t2bb * x
    tx = x

    d1 = t2bbx *  (x-1) + tbb/2 + t2aa * (1-tbb)
    while t2bb * tx > t2aa * y:
        result.append((x, y))
        if d1 < 0:
            y = y + 1
            d1 = d1 + t4aa * y + t2aa
            tx = x - 1
        else:
            x =  x - 1
            y =  y + 1
            d1 = d1 - t4bb * x + t4aa * y + t2aa
            tx = x
    
    d2 = t2bb * (x*x +1) - t4bb*x+t2aa*(y*y+y-tbb) + taa/2
    while x>=0:
        result.append((x, y))
        if d2 < 0:
            x = x - 1
            y = y + 1
            d2 = d2 + t4aa * y - t4bb*x + t2bb
        else:
            x =  x - 1
            d2 = d2 - t4bb * x + t2bb
    result += list(map(lambda x :(x[0],-x[1]), result))
    result += list(map(lambda x :(-x[0],x[1]), result))
    result = list(map(lambda x: (x[0] + center[0], x[1] + center[1]), result))
    return result


def addPoint(p1, p2, u): 
    return ((1 - u) * p1[0] + u * p2[0], (1 - u) * p1[1] + u * p2[1])

def bezier(p_list, r, i, u):
    if r == 0:
        return p_list[i]
    else:
        return addPoint(bezier(p_list, r - 1, i, u), bezier(p_list, r - 1, i + 1, u), u)
    pass

def bSpline(p, t):
    n = p.__len__() - 1
    m = 3 + n + 1
    step = 1 / (m - 2 * 3)
    u = [0, 0, 0] + [_u * step for _u in range(0, m - 2 * 3 + 1)] + [1, 1, 1]
    for i in range(3, m - 3):
        if u[i] <= t and t < u[i + 1]:
            break
    _t = (t - u[i]) / (u[i + 1] - u[i])
    A1 = (1 - _t) * (1 - _t) * (1 - _t) / 6.0
    A2 = (3 * _t * _t * _t - 6 * _t * _t + 4) / 6.0
    A3 = (-3 * _t * _t * _t + 3 * _t * _t + 3 * _t + 1) / 6.0
    A4 = _t * _t * _t / 6.0
    return (A1 * p[i-3][0] + A2 * p[i-2][0] + A3 * p[i-1][0] + A4 * p[i][0],
            A1 * p[i-3][1] + A2 * p[i-2][1] + A3 * p[i-1][1] + A4 * p[i][1])


def draw_curve(p_list: list, algorithm, isQuick = False):
    """绘制曲线

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 曲线的控制点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'Bezier'和'B-spline'（三次均匀B样条曲线，曲线不必经过首末控制点）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    nPoints = 0
    for i in range(len(p_list) - 1):
        nPoints += max(abs(p_list[i][0] - p_list[i+1][0]), abs(p_list[i][1] - p_list[i+1][1]))
    if isQuick: nPoints = int(nPoints / 10)
    else: nPoints *= 2
    # nPoints = len(p_list) * 20
    # print(nPoints)
    # if not isQuick: nPoints *= 20
    if algorithm == 'Bezier':
        n = p_list.__len__() - 1
        result = [p_list[0]]
        for i in range(1, nPoints):
            result.append(bezier(p_list, n, 0, float(i) / (nPoints - 1)))
        return list(set(map(lambda p: (round(p[0]), round(p[1])), result)))
    elif algorithm == 'B-spline':
        result = []
        for i in range(0, nPoints):
            t = i / nPoints
            result.append(bSpline(p_list, t))
        return list(set(map(lambda p: (round(p[0]), round(p[1])), result)))
        pass
    pass


def translate(p_list, dx, dy):
    """平移变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param dx: (int) 水平方向平移量
    :param dy: (int) 垂直方向平移量
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    return list(map(lambda p: (p[0] + dx, p[1] - dy), p_list))


def rotate(p_list, x, y, r):
    """旋转变换（除椭圆外）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 旋转中心x坐标
    :param y: (int) 旋转中心y坐标
    :param r: (int) 顺时针旋转角度（°）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    rad = math.radians(-r)
    sin, cos = math.sin(rad), math.cos(rad)
    return list(map(lambda p: (round(x + (p[0] - x)*cos -(p[1]-y)*sin), round(y + (p[0] - x)*sin +(p[1]-y)*cos)), p_list))


def scale(p_list, x, y, s):
    """缩放变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 缩放中心x坐标
    :param y: (int) 缩放中心y坐标
    :param s: (float) 缩放倍数
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    return list(map(lambda p: (round(p[0] * s + x * (1 - s)), round(p[1] * s + y * (1 - s))), p_list))

def getPCode(x, y, window):
    pCodeList = []
    pCodeList.append(x < window[0])
    pCodeList.append(x > window[1])
    pCodeList.append(y < window[2])
    pCodeList.append(y > window[3])
    p = 0
    for i in pCodeList:
        p = (p << 1) | i
    return p
def getJoint(x1, y1, x2, y2, x = None, y = None):
    if x != None:
        if x1 == x2: 
            return None
        else:
            return x, y1 + (x - x1)/(x2 - x1)*(y2 - y1)
    if y != None:
        if y1 == y2:
            return None
        else:
            return x1 + (y - y1)/(y2 - y1)*(x2 - x1), y
    return None
def getFlag(pCode1, pCode2):
    return ((pCode1 == 0) & (pCode2 == 0)) + (pCode1 & pCode2 == 0)

def clipt(d, q, t_list): 
    visible = True
    if d == 0 and q < 0:
        visible = False
    elif d < 0:
        t = float(q) / d
        if t > t_list[1]:
            visible = False
        elif t > t_list[0]:
            t_list[0] = t
    elif d > 0:
        t = float(q) / d
        if t < t_list[0]:
            visible = False
        elif t < t_list[1]:
            t_list[1] = t
    return visible

def clip(p_list, x_min, y_min, x_max, y_max, algorithm):
    """线段裁剪

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param x_min: 裁剪窗口左上角x坐标
    :param y_min: 裁剪窗口左上角y坐标
    :param x_max: 裁剪窗口右下角x坐标
    :param y_max: 裁剪窗口右下角y坐标
    :param algorithm: (string) 使用的裁剪算法，包括'Cohen-Sutherland'和'Liang-Barsky'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1]]) 裁剪后线段的起点和终点坐标
    """
    x1, y1 = p_list[0]
    x2, y2 = p_list[1]
    if algorithm == 'Cohen-Sutherland':
        window = (x_min, x_max, y_min, y_max)
        pCode1 = getPCode(x1, y1, window)
        pCode2 = getPCode(x2, y2, window)
        vFlag = getFlag(pCode1, pCode2)
        if vFlag == 2: 
            return [(x1, y1), (x2, y2)]
        elif vFlag == 1:
            iFlag = 1
            if x1 == x2:
                iFlag = -1
            elif y1 == y2:
                iFlag = 0
            while(vFlag == 1):
                for i in range(1,5):
                    if (pCode1 >> (4 - i)) != (pCode2 >> (4 - i)):
                        if (pCode1 >> (4 - i)) == 0:
                            x1, y1, x2, y2 = x2, y2, x1, y1
                            pCode1, pCode2 = pCode2, pCode1
                        if iFlag != -1 and i <= 2:
                            y1 = (y2 - y1) / (x2 - x1) * (window[i - 1] - x1) + y1
                            x1 = window[i - 1]
                            pCode1 = getPCode(x1, y1, window)
                        if iFlag != 0 and i > 2:
                            if iFlag != -1:
                                x1 = (x2 - x1) / (y2 - y1) * (window[i - 1] - y1) + x1
                            y1 = window[i - 1]
                            pCode1 = getPCode(x1, y1, window)
                        vFlag = getFlag(pCode1, pCode2)
                        if vFlag == 2:             
                            return [(round(x1), round(y1)), (round(x2), round(y2))]
                        elif vFlag == 0: 
                            return []
        else:
            return []
    elif algorithm == 'Liang-Barsky':
        t = [float(0), float(1)]
        deltax = float(x2 - x1)
        if clipt(-deltax, x1 - x_min, t):
            if clipt(deltax, x_max - x1, t):
                deltay = float(y2 - y1)
                if clipt(-deltay, y1 - y_min, t):
                    if clipt(deltay, y_max - y1, t):
                        if t[1] < 1:
                            x2 = x1 + t[1] * deltax
                            y2 = y1 + t[1] * deltay
                        if t[0] > 0:
                            x1 = x1 + t[0] * deltax
                            y1 = y1 + t[0] * deltay
                        return [(round(x1), round(y1)), (round(x2), round(y2))]
        pass
    return []

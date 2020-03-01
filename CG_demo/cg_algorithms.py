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
            for y in range(y0, y1 + 1):
                result.append((x0, y))
        else:
            if x0 > x1:
                x0, y0, x1, y1 = x1, y1, x0, y0
            k = (y1 - y0) / (x1 - x0)
            for x in range(x0, x1 + 1):
                result.append((x, int(y0 + k * (x - x0))))
        pass
    elif algorithm == 'DDA':
        if abs(y1 - y0) <= abs(x1 - x0):
            if x0 > x1:
                x0, y0, x1, y1 = x1, y1, x0, y0
            k = (y1 - y0) / (x1 - x0)
            for x in range(x0, x1 + 1):
                result.append((x, int(y0 + k * (x - x0))))
        else:
            if y0 > y1:
                x0, y0, x1, y1 = x1, y1, x0, y0
            k = (x1 - x0) / (y1 - y0)
            for y in range(y0, y1 + 1):
                result.append((int(x0 + k * (y - y0)), y))
        pass
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
        for i in range(1, dx + 1):
            result.append((x, y))
            while(e > 0):
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
        pass
    return result


def draw_polygon(p_list, algorithm):
    """绘制多边形

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 多边形的顶点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
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
    x0, y0, x1, y1 = min(x0,x1), min(y0,y1), max(x0,x1), max(y0,y1)
    a = abs(x1 - x0) / 2
    b = abs(y1 - y0) / 2
    center = [int((x0 + x1)/2), int((y0 + y1)/2)]

    result = []
    # x = int(a + 1/2)
    # y = 0
    # while b*b*(x-1/2) > a * a * (y+1):
    #     result.append((x, y))
    #     d1 = b*b*(2*x*x-2*x+1/2) + a*a*(2*y*y+4*y+2)-2*a*a*b*b
    #     if d1 < 0:
    #         y += 1
    #     else:
    #         x -= 1
    #         y += 1
    # d2 = b*b*(2*x*x-4*x+2)+a*a*(2*y*y+2*y+1/2)-2*a*a*b*b
    # while x>=0:
    #     result.append((x, y))
    #     if d2 < 0:
    #         x -= 1
    #         y+=1
    #     else:
    #         x-=1
    #     d2 = b*b*(2*x*x-4*x+2)+a*a*(2*y*y+2*y+1/2)-2*a*a*b*b
        
    x = int(a + 1/2)
    y = int(0)
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
    pass


def draw_curve(p_list, algorithm):
    """绘制曲线

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 曲线的控制点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'Bezier'和'B-spline'（三次均匀B样条曲线，曲线不必经过首末控制点）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    pass


def translate(p_list, dx, dy):
    """平移变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param dx: (int) 水平方向平移量
    :param dy: (int) 垂直方向平移量
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    return list(map(lambda p: (p[0] + dx, p[1] + dy), p_list))


def rotate(p_list, x, y, r):
    """旋转变换（除椭圆外）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 旋转中心x坐标
    :param y: (int) 旋转中心y坐标
    :param r: (int) 顺时针旋转角度（°）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    rad = r / math.pi / 2
    sin, cos = math.sin(rad), math.cos(rad)
    return list(map(lambda p: (round(x + (p[0] - x)*cos -(p[1]-y)*sin), round(y + (p[0] - x)*sin +(p[1]-y)*cos)), p_list))
    pass


def scale(p_list, x, y, s):
    """缩放变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 缩放中心x坐标
    :param y: (int) 缩放中心y坐标
    :param s: (float) 缩放倍数
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    return list(map(lambda p: (round(p[0] * s + x * (1 - s)), round(p[1] * s + y * (1 - s))), p_list))
    pass


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
    pass

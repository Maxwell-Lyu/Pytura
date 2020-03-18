#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import math
import cg_algorithms as alg
from typing import Optional
from PyQt5.QtWidgets import (
    QColorDialog, 
    QApplication,
    QMainWindow,
    qApp,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsItem,
    QListWidget,
    QHBoxLayout,
    QWidget,
    QStyleOptionGraphicsItem)
from PyQt5.QtGui import QPainter, QMouseEvent, QColor
from PyQt5.QtCore import QRectF


class MyCanvas(QGraphicsView):
    """
    画布窗体类，继承自QGraphicsView，采用QGraphicsView、QGraphicsScene、QGraphicsItem的绘图框架
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.setMouseTracking(True)
        self.main_window = None
        self.list_widget = None
        self.item_dict = {}
        self.selected_id = ''

        self.status = ''
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None
        self.temp_last_point = 0

        self.edit_data = []
        self.edit_p_list = []

        self.pen_color = QColor(0, 0, 0)

    def start_draw(self, status, algorithm, item_id):
        self.status = status
        self.temp_algorithm = algorithm
        self.temp_id = item_id
        self.temp_last_point = 0

    def start_edit(self, status, algorithm):
        if self.selected_id:
            self.status = status
            self.temp_id = self.selected_id
            self.temp_item.isTemp = True
            self.edit_p_list = self.item_dict[self.temp_id].p_list

    def start_clip(self, status, algorithm):
        if self.selected_id and self.item_dict[self.selected_id].item_type == 'line':
            self.status = status
            self.temp_algorithm = algorithm
            self.temp_id = 'clip-rect'

    def finish_draw(self):
        self.status = ''
        self.temp_last_point = 0
        self.item_dict[self.temp_id] = self.temp_item
        self.list_widget.addItem(self.temp_id)
        self.temp_item.isDirty = True
        self.temp_item.isTemp = False
        self.temp_id = ''
        self.updateScene([self.sceneRect()])

    def finish_edit(self):
        self.status = ''
        self.temp_id = ''
        self.temp_item.isTemp = False
        self.temp_item.isDirty = True
        self.edit_data = []
        self.updateScene([self.sceneRect()])

    def finish_clip(self):
        self.status = ''
        self.temp_id = ''
        self.edit_data = []
        minPoint = min(self.temp_item.p_list)
        maxPoint = max(self.temp_item.p_list)
        new_p_list = alg.clip(self.item_dict[self.selected_id].p_list, minPoint[0], minPoint[1], maxPoint[0], maxPoint[1], self.temp_algorithm)
        self.item_dict[self.selected_id].p_list = new_p_list
        self.item_dict[self.selected_id].isDirty = True
        self.scene().removeItem(self.temp_item)
        self.updateScene([self.sceneRect()])

    def clear_selection(self):
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.selected_id = ''

    def selection_changed(self, selected):
        self.main_window.statusBar().showMessage('图元选择： %s' % selected)
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.item_dict[self.selected_id].update()
        self.selected_id = selected
        self.item_dict[selected].selected = True
        self.item_dict[selected].update()
        self.status = ''
        self.updateScene([self.sceneRect()])

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.status == '':
            return
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'translate' and len(self.edit_data):
            self.edit_data[1] = [x, y]
            dx = self.edit_data[1][0] - self.edit_data[0][0]
            dy = self.edit_data[1][1] - self.edit_data[0][1]
            new_p_list = alg.translate(self.edit_p_list, dx, dy)
            self.item_dict[self.selected_id].p_list = new_p_list
            self.item_dict[self.selected_id].isDirty = True
            pass
        elif self.status == 'rotate' and len(self.edit_data):
            self.edit_data[1] = [x, y]
            dx = self.edit_data[1][0] - self.edit_data[0][0]
            dy = self.edit_data[1][1] - self.edit_data[0][1]
            if dx:
                new_p_list = alg.rotate(self.edit_p_list, self.edit_data[0][0], self.edit_data[0][1], math.degrees(math.atan2(dy, dx)))
                self.item_dict[self.selected_id].p_list = new_p_list
                self.item_dict[self.selected_id].isDirty = True
            pass
        elif self.status == 'scale' and len(self.edit_data):
            self.edit_data[1] = [x, y]
            dx = self.edit_data[1][0] - self.edit_data[0][0]
            dy = self.edit_data[1][1] - self.edit_data[0][1]
            new_p_list = alg.scale(self.edit_p_list, self.edit_data[0][0] + 100, self.edit_data[0][1] + 100, max(dx, dy) / 100)
            self.item_dict[self.selected_id].p_list = new_p_list
            self.item_dict[self.selected_id].isDirty = True
        elif self.status == 'clip' and len(self.temp_item.p_list) == 4:
            self.temp_item.p_list[2] = [x, y]
            self.temp_item.p_list = [self.temp_item.p_list[0], [self.temp_item.p_list[0][0], y], [x, y], [x, self.temp_item.p_list[0][1]]]
            self.temp_item.isDirty = True
        elif self.temp_last_point:
            if self.temp_last_point == len(self.temp_item.p_list):
                self.temp_item.p_list.append([x, y])
            else:
                self.temp_item.p_list[self.temp_last_point] = [x, y]
            self.temp_item.isDirty = True
        self.updateScene([self.sceneRect()])
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if self.status == '':
            return
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'translate' or self.status == 'rotate':
            self.edit_data = [[x, y], [x, y]]
        elif self.status == 'scale':
            self.edit_data = [[x - 100, y - 100], [x, y]]
        elif self.status == 'clip':
            self.temp_item = MyItem(self.temp_id, 'polygon', [[x, y], [x, y], [x, y], [x, y]], 'DDA', QColor(0, 0, 255))
            self.scene().addItem(self.temp_item)
            self.updateScene([self.sceneRect()])
            pass
        elif self.temp_last_point == 0:
            self.temp_last_point += 1
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm, self.pen_color)
            self.temp_item.isDirty = True
            self.scene().addItem(self.temp_item)
            self.updateScene([self.sceneRect()])
        else: 
            self.temp_item.p_list[self.temp_last_point] = [x, y]
            self.temp_item.isDirty = True
            self.temp_last_point += 1
            self.updateScene([self.sceneRect()])
            if self.status == 'line' and len(self.temp_item.p_list) == 2:
                self.finish_draw()
            elif self.status == 'ellipse' and len(self.temp_item.p_list) == 2:
                self.finish_draw()
        super().mouseReleaseEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.status == 'translate' or self.status == 'rotate' or self.status == 'scale':
            self.finish_edit()
        elif self.status == 'clip':
            self.finish_clip()
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if self.status == 'polygon' and len(self.temp_item.p_list) >= 2:
            self.finish_draw()
        elif self.status == 'curve' and len(self.temp_item.p_list) >= 2:
            self.finish_draw()
        super().mouseDoubleClickEvent(event)
        
    """
    def mousePressEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line':
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm)
            self.scene().addItem(self.temp_item)
        self.updateScene([self.sceneRect()])
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line':
            self.temp_item.p_list[1] = [x, y]
        self.updateScene([self.sceneRect()])
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.status == 'line':
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
        super().mouseReleaseEvent(event)
    """


class MyItem(QGraphicsItem):
    """
    自定义图元类，继承自QGraphicsItem
    """
    def __init__(self, item_id: str, item_type: str, p_list: list, algorithm: str = '', color: QColor = None, parent: QGraphicsItem = None):
        """

        :param item_id: 图元ID
        :param item_type: 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        :param p_list: 图元参数
        :param algorithm: 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        :param parent:
        """
        super().__init__(parent)
        self.id = item_id           # 图元ID
        self.item_type = item_type  # 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        self.p_list = p_list        # 图元参数
        self.algorithm = algorithm  # 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        self.item_pixels = []
        self.selected = False
        self.isDirty = True
        self.isTemp = True
        self.color = color

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
        if self.isDirty:
            if self.item_type == 'line':
                self.item_pixels = alg.draw_line(self.p_list, self.algorithm)
            elif self.item_type == 'polygon':
                self.item_pixels = alg.draw_polygon(self.p_list, self.algorithm)
            elif self.item_type == 'ellipse':
                self.item_pixels = alg.draw_ellipse(self.p_list)
            elif self.item_type == 'curve':
                if self.algorithm == 'B-spline' and len(self.p_list) < 4:
                    self.item_pixels = []
                else:
                    self.item_pixels = alg.draw_curve(self.p_list, self.algorithm, self.isTemp)
            self.isDirty = False

        for p in self.item_pixels:
            painter.setPen(self.color)
            painter.drawPoint(*p)
        if self.selected:
            painter.setPen(QColor(255, 0, 0))
            painter.drawRect(self.boundingRect())

    def boundingRect(self) -> QRectF:
        if self.item_type == 'line' or self.item_type == 'ellipse':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
        elif self.item_type == 'polygon' or self.item_type == 'curve':
            x = min(list(map(lambda p: p[0], self.p_list)))
            y = min(list(map(lambda p: p[1], self.p_list)))
            w = max(list(map(lambda p: p[0], self.p_list))) - x
            h = max(list(map(lambda p: p[1], self.p_list))) - y
        return QRectF(x - 1, y - 1, w + 2, h + 2)


class MainWindow(QMainWindow):
    """
    主窗口类
    """
    styleSheet = """
QListWidget{
//  background: red;
}
    """
    def __init__(self):
        super().__init__()
        self.setStyleSheet(self.styleSheet)
        self.item_cnt = 0
        # 使用QListWidget来记录已有的图元，并用于选择图元。注：这是图元选择的简单实现方法，更好的实现是在画布中直接用鼠标选择图元
        self.list_widget = QListWidget(self)
        self.list_widget.setMinimumWidth(200)

        # 使用QGraphicsView作为画布
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, 600, 600)
        self.canvas_widget = MyCanvas(self.scene, self)
        self.canvas_widget.setFixedSize(600, 600)
        self.canvas_widget.main_window = self
        self.canvas_widget.list_widget = self.list_widget

        # 设置菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu('文件')
        set_pen_act = file_menu.addAction('设置画笔')
        reset_canvas_act = file_menu.addAction('重置画布')
        exit_act = file_menu.addAction('退出')
        draw_menu = menubar.addMenu('绘制')
        line_menu = draw_menu.addMenu('线段')
        line_naive_act = line_menu.addAction('Naive')
        line_dda_act = line_menu.addAction('DDA')
        line_bresenham_act = line_menu.addAction('Bresenham')
        polygon_menu = draw_menu.addMenu('多边形')
        polygon_dda_act = polygon_menu.addAction('DDA')
        polygon_bresenham_act = polygon_menu.addAction('Bresenham')
        ellipse_act = draw_menu.addAction('椭圆')
        curve_menu = draw_menu.addMenu('曲线')
        curve_bezier_act = curve_menu.addAction('Bezier')
        curve_b_spline_act = curve_menu.addAction('B-spline')
        edit_menu = menubar.addMenu('编辑')
        translate_act = edit_menu.addAction('平移')
        rotate_act = edit_menu.addAction('旋转')
        scale_act = edit_menu.addAction('缩放')
        clip_menu = edit_menu.addMenu('裁剪')
        clip_cohen_sutherland_act = clip_menu.addAction('Cohen-Sutherland')
        clip_liang_barsky_act = clip_menu.addAction('Liang-Barsky')

        # 连接信号和槽函数
        # Description: file actions
        set_pen_act.triggered.connect(self.set_pen_action)
        reset_canvas_act.triggered.connect(self.reset_canvas_action)
        exit_act.triggered.connect(qApp.quit)
        # Description: line actions
        line_naive_act.triggered.connect(self.line_naive_action)
        line_dda_act.triggered.connect(self.line_dda_action)
        line_bresenham_act.triggered.connect(self.line_bresenham_action)
        # Description: polygon actions
        polygon_dda_act.triggered.connect(self.polygon_dda_action)
        polygon_bresenham_act.triggered.connect(self.polygon_bresenham_action)
        # Description: ellipse actions
        ellipse_act.triggered.connect(self.ellipse_action)
        # Description: curve actions
        curve_bezier_act.triggered.connect(self.curve_bezier_aciion)
        curve_b_spline_act.triggered.connect(self.curve_b_spline_action)
        # Description: edit actions
        translate_act.triggered.connect(self.translate_action)
        rotate_act.triggered.connect(self.rotate_action)
        scale_act.triggered.connect(self.scale_action)
        # Description: clip actions
        clip_cohen_sutherland_act.triggered.connect(self.clip_cohen_sutherland_action)
        clip_liang_barsky_act.triggered.connect(self.clip_liang_barsky_action)

        self.list_widget.currentTextChanged.connect(self.canvas_widget.selection_changed)

        # 设置主窗口的布局
        self.hbox_layout = QHBoxLayout()
        self.hbox_layout.addWidget(self.canvas_widget)
        self.hbox_layout.addWidget(self.list_widget, stretch=1)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.hbox_layout)
        self.setCentralWidget(self.central_widget)
        self.statusBar().showMessage('空闲')
        self.resize(600, 600)
        self.setWindowTitle('CG Demo')

    def get_id(self):
        _id = str(self.item_cnt)
        self.item_cnt += 1
        return _id

    # Description: file actions
    def set_pen_action(self):
        self.canvas_widget.pen_color = QColorDialog.getColor()

    def reset_canvas_action(self):
        self.scene.clear()
        self.list_widget.clear()
        self.canvas_widget.item_dict.clear()
        self.item_cnt = 0

    # Description: line actions
    def line_naive_action(self):
        self.canvas_widget.start_draw('line','Naive', self.get_id())
        self.statusBar().showMessage('Naive算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_dda_action(self):
        self.canvas_widget.start_draw('line','DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_bresenham_action(self):
        self.canvas_widget.start_draw('line','Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    # Description: polygon actions
    def polygon_dda_action(self):
        self.canvas_widget.start_draw('polygon','DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_bresenham_action(self):
        self.canvas_widget.start_draw('polygon','Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    # Description: ellipse actions
    def ellipse_action(self):
        self.canvas_widget.start_draw('ellipse','', self.get_id())
        self.statusBar().showMessage('中点圆生成算法绘制椭圆')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    # Description: curve actions
    def curve_bezier_aciion(self):
        self.canvas_widget.start_draw('curve','Bezier', self.get_id())
        self.statusBar().showMessage('Bezier算法绘制曲线')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_b_spline_action(self):
        self.canvas_widget.start_draw('curve','B-spline', self.get_id())
        self.statusBar().showMessage('B-spline算法绘制曲线')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    # Description: edit actions
    def translate_action(self):
        self.canvas_widget.start_edit('translate','')
        self.statusBar().showMessage('平移')

    def rotate_action(self):
        self.canvas_widget.start_edit('rotate','')
        self.statusBar().showMessage('旋转')

    def scale_action(self):
        self.canvas_widget.start_edit('scale','')
        self.statusBar().showMessage('缩放')

    # Description: clip actions
    def clip_cohen_sutherland_action(self):
        self.canvas_widget.start_clip('clip','Cohen-Sutherland')
        self.statusBar().showMessage('Cohen-Sutherland算法裁剪线段')

    def clip_liang_barsky_action(self):
        self.canvas_widget.start_clip('clip','Liang-Barsky')
        self.statusBar().showMessage('Liang-Barsky算法裁剪线段')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())

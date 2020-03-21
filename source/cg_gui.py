#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys, time
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
    QListWidgetItem,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QLabel,
    QPushButton,
    QToolBox,
    QToolButton,
    QSplitter,
    QFrame,
    QLayout,
    QStyle,
    QSplashScreen,
    QStyleOptionGraphicsItem)
from PyQt5.QtGui import QPainter, QMouseEvent, QColor, QPalette, QIcon, QPixmap, QFontDatabase
from PyQt5.QtCore import QRectF, QLine, Qt, QPoint, QSize, pyqtSignal
import ctypes
class MyCanvas(QGraphicsView):
    """
    画布窗体类，继承自QGraphicsView，采用QGraphicsView、QGraphicsScene、QGraphicsItem的绘图框架
    """
    statusChanged = pyqtSignal(str, str, str)

    def set_status(self, value):
        self.statusChanged.emit(self.status, value, self.temp_algorithm)
        self.status = value

    def addItem(self):
        new_entry = QListWidgetItem(self.temp_item.__icon__(), self.temp_item.item_type.title() + '\t' + self.temp_id)
        new_entry.setToolTip('选中该' + self.temp_item.item_type.title())
        self.list_widget.addItem(new_entry)

    def __init__(self, *args):
        super().__init__(*args)
        self.setMouseTracking(True)
        self.main_window : MainWindow = None
        self.list_widget : QListWidget = None
        self.item_dict = {}
        self.selected_id = ''

        self.status = ''
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item : MyItem = None
        self.temp_last_point = 0

        self.edit_data = []
        self.edit_p_list = []

        self.pen_color = QColor(0, 0, 0)

    def start_draw(self, status, algorithm, item_id):
        self.temp_algorithm = algorithm
        self.set_status(status)
        self.temp_id = item_id
        self.temp_last_point = 0

    def start_edit(self, status, algorithm):
        if self.selected_id:
            self.set_status(status)
            self.temp_id = self.selected_id
            self.item_dict[self.temp_id].isTemp = True
            self.edit_p_list = self.item_dict[self.temp_id].p_list
        else:
            self.set_status('')

    def start_clip(self, status, algorithm):
        if self.selected_id and self.item_dict[self.selected_id].item_type == 'line':
            self.temp_algorithm = algorithm
            self.set_status(status)
            self.temp_id = 'clip-rect'
        else:
            self.set_status('')

    def finish_draw(self):
        self.set_status('')
        self.temp_last_point = 0
        self.item_dict[self.temp_id] = self.temp_item
        # self.list_widget.addItem(self.temp_id)
        self.addItem()
        self.temp_item.isDirty = True
        self.temp_item.isTemp = False
        self.temp_id = ''
        self.updateScene([self.sceneRect()])

    def finish_edit(self):
        self.set_status('')
        self.temp_id = ''
        self.temp_item.isTemp = False
        self.temp_item.isDirty = True
        self.edit_data = []
        self.updateScene([self.sceneRect()])

    def finish_clip(self):
        self.set_status('')
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

    def delete_selection(self):
        if self.selected_id != '':
            item = self.item_dict.pop(self.selected_id)
            self.scene().removeItem(item)
            self.selected_id = ''

    def selection_changed(self, selected: str):
        selected = selected.split('\t', 1)[1]
        self.main_window.statusBar().showMessage('图元选择： %s' % selected)
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.item_dict[self.selected_id].update()
        self.selected_id = selected
        if selected != '':
            self.item_dict[selected].selected = True
            self.item_dict[selected].update()
        self.set_status('')
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
            new_p_list = alg.scale(self.edit_p_list, self.edit_data[0][0] + 100, self.edit_data[0][1] + 100, dx / 100)
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
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == '':
            if self.selected_id: self.item_dict[self.selected_id].selected = False
            if len(self.main_window.canvas_widget.items(QPoint(x, y))):
                self.selected_id = self.main_window.canvas_widget.items(QPoint(x, y))[0].id
                self.item_dict[self.selected_id].selected = True
            else:
                self.selected_id = ''
        elif self.status == 'translate' or self.status == 'rotate':
            self.edit_data = [[x, y], [x, y]]
        elif self.status == 'scale':
            self.edit_data = [[x - 100, y - 100], [x, y]]
        elif self.status == 'clip':
            self.temp_item = MyItem(self.temp_id, 'polygon', [[x, y], [x, y], [x, y], [x, y]], 'DDA', QColor(255, 0, 0))
            self.scene().addItem(self.temp_item)
            pass
        elif self.temp_last_point == 0:
            self.temp_last_point += 1
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm, self.pen_color)
            self.temp_item.isDirty = True
            self.scene().addItem(self.temp_item)
        else: 
            self.temp_item.p_list[self.temp_last_point] = [x, y]
            self.temp_item.isDirty = True
            self.temp_last_point += 1
        self.updateScene([self.sceneRect()])
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.status == 'translate' or self.status == 'rotate' or self.status == 'scale':
            self.finish_edit()
        elif  self.status == 'clip':
            self.finish_clip()
        elif self.status == 'line' or self.status == 'ellipse':
            self.finish_draw()
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if self.status == 'polygon' and self.temp_item and len(self.temp_item.p_list) >= 2:
            self.finish_draw()
        elif self.status == 'curve' and self.temp_item and len(self.temp_item.p_list) >= 2:
            self.finish_draw()
        super().mouseDoubleClickEvent(event)


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
    
    def __icon__(self) -> QIcon:
        if self.item_type == 'line':
            if self.algorithm == 'Naive':
                return QIcon('asset/icon/line_naive.svg')
            elif self.algorithm == 'DDA':
                return QIcon('asset/icon/line_dda.svg')
            elif self.algorithm == 'Bresenham':
                return QIcon('asset/icon/line_bresenham.svg')
        elif self.item_type == 'polygon':
            if self.algorithm == 'DDA':
                return QIcon('asset/icon/polygon_dda.svg')
            elif self.algorithm == 'Bresenham':
                return QIcon('asset/icon/polygon_bresenham.svg')
        elif self.item_type == 'ellipse':
            return QIcon('asset/icon/ellipse.svg')
        elif self.item_type == 'curve':
            if self.algorithm == 'Bezier':
                return QIcon('asset/icon/curve_bezier.svg')
            elif self.algorithm == 'B-spline':
                return QIcon('asset/icon/curve_b_spline.svg')

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
            painter.setPen(QColor(21, 101, 192))
            painter.drawRect(self.boundingRect())
        if self.isTemp or self.selected:
            self.drawControlPoint(painter)
            if self.item_type == 'curve':
                self.drawControlPolygon(painter)

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
    
    def drawControlPoint(self, painter: QPainter):
        painter.setPen(QColor(30, 136, 229))
        for p in self.p_list:
            x, y = p
            painter.drawRect(QRectF(x - 1, y - 1, 2, 2))
            painter.drawRect(QRectF(x - 2, y - 2, 4, 4))    

    def drawControlPolygon(self, painter: QPainter):
        painter.setPen(QColor(114, 202, 246))
        for i in range(len(self.p_list) - 1):
            # painter.drawLine(QLine(self.p_list[i][0], self.p_list[i + 1][1], self.p_list[i][0], self.p_list[i + 1][1]))
            painter.drawLine(QLine(self.p_list[i][0], self.p_list[i][1], self.p_list[i + 1][0], self.p_list[i + 1][1]))


class MainWindow(QMainWindow):
    """
    主窗口类
    """
    centralStyleSheet = """
QPushButton{
    icon-size: 32px;
    max-width:  40px;
    max-height: 40px;
    min-width:  40px;
    min-height: 40px;
    margin: 0px 0px 6px 0px;
	border-width: 4px;
    border-image: url(asset/img/tool_default.png) 4 stretch;

}
QPushButton:pressed{
    border-image: url(asset/img/tool_pressed.png) 4 stretch;
}
QPushButton:hover:!pressed:!checked{
    border-image: url(asset/img/tool_hover.png) 4 stretch;
}
QPushButton:checked {
    border-image: url(asset/img/tool_checked.png) 4 stretch;
}   
QGraphicsView{
    background: #ffffff;
}
QListWidget {
    icon-size: 24px;
}
    """
    styleSheet = """
QWidget{
    background: #212121;
    color: #ffffff;
    border-color: #ffffff;
    padding: 0 0 0 0;
    margin: 0 0 0 0;
	outline: none;
    font-family: 'Sarasa UI SC Semibold'
}
QPushButton{
    min-height: 24px;
    min-width: 96px;
    border-width: 0 8px 0 8px;
    border-image: url(asset/img/btn_default.png) 8 stretch;
}
QPushButton:pressed{
    border-image: url(asset/img/btn_pressed.png) 8 stretch;
}
QPushButton:hover:!pressed:!checked{
    border-image: url(asset/img/btn_hover.png) 8 stretch;
}
    """
# QPushButton:checked:hover {
#     background: green;
# }
# QPushButton:checked:pressed {
#     background: white;
# }
# QPushButton:checked {
#     background: gray;
# }
    def __init__(self):
        super().__init__()
        QFontDatabase.addApplicationFont("asset/font/sarasa-semibold.ttc")
        self.setStyleSheet(self.styleSheet)
        self.item_cnt = 0
        # 使用QListWidget来记录已有的图元，并用于选择图元。注：这是图元选择的简单实现方法，更好的实现是在画布中直接用鼠标选择图元
        self.list_widget = QListWidget(self)
        self.list_widget.setMinimumWidth(200)

        # 使用QGraphicsView作为画布
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, 600, 600)
        self.canvas_widget = MyCanvas(self.scene, self)
        self.canvas_widget.setFixedSize(606, 606)
        self.canvas_widget.main_window = self
        self.canvas_widget.list_widget = self.list_widget


        # Tool Bar
        vbox_layout1 = QVBoxLayout()
        vbox_layout1.setSpacing(0)
        vbox_layout1.setAlignment(Qt.AlignTop)
        vbox_layout2 = QVBoxLayout()
        vbox_layout2.setSpacing(0)
        vbox_layout2.setAlignment(Qt.AlignTop)
        ## Tool Btn
        self.set_pen_btn                    = QPushButton(QIcon('asset/icon/set_pen.svg'), '')
        self.set_pen_btn.setStyleSheet("""  
            max-width:  40px;
            max-height: 40px;
            min-width:  40px;
            min-height: 40px;
            margin: 0px 0px 6px 2px;
            border-width: 2px;
            border-style: outset;
            border-color: white;
            background: black;
            border-image: none;
            """
        )
        self.delete_btn                     = QPushButton(QIcon('asset/icon/delete.svg'), '')
        self.reset_canvas_btn               = QPushButton(QIcon('asset/icon/reset_canvas.svg'), '')
        self.export_btn                     = QPushButton(QIcon('asset/icon/export.svg'), '')
        self.exit_btn                       = QPushButton(QIcon('asset/icon/exit.svg'), '')
        self.line_naive_btn                 = QPushButton(QIcon('asset/icon/line_naive.svg'), '')
        self.line_dda_btn                   = QPushButton(QIcon('asset/icon/line_dda.svg'), '')
        self.line_bresenham_btn             = QPushButton(QIcon('asset/icon/line_bresenham.svg'), '')
        self.polygon_dda_btn                = QPushButton(QIcon('asset/icon/polygon_dda.svg'), '')
        self.polygon_bresenham_btn          = QPushButton(QIcon('asset/icon/polygon_bresenham.svg'), '')
        self.ellipse_btn					= QPushButton(QIcon('asset/icon/ellipse.svg'), '')
        self.curve_bezier_btn				= QPushButton(QIcon('asset/icon/curve_bezier.svg'), '')
        self.curve_b_spline_btn				= QPushButton(QIcon('asset/icon/curve_b_spline.svg'), '')
        self.translate_btn					= QPushButton(QIcon('asset/icon/translate.svg'), '')
        self.rotate_btn						= QPushButton(QIcon('asset/icon/rotate.svg'), '')
        self.scale_btn						= QPushButton(QIcon('asset/icon/scale.svg'), '')
        self.clip_cohen_sutherland_btn      = QPushButton(QIcon('asset/icon/clip_cohen_sutherland.svg'), '')
        self.clip_liang_barsky_btn          = QPushButton(QIcon('asset/icon/clip_liang_barsky.svg'), '')
        self.delete_btn                     .setToolTip('删除选中图元')
        self.reset_canvas_btn               .setToolTip('重置画布')
        self.export_btn                     .setToolTip('导出')
        self.exit_btn                       .setToolTip('退出')
        self.line_naive_btn                 .setToolTip('Naive算法绘制线段')
        self.line_dda_btn                   .setToolTip('DDA算法绘制线段')
        self.line_bresenham_btn             .setToolTip('Bresenham算法绘制线段')
        self.polygon_dda_btn                .setToolTip('DDA算法绘制多边形')
        self.polygon_bresenham_btn          .setToolTip('Bresenham算法绘制多边形')
        self.ellipse_btn					.setToolTip('中点圆算法绘制椭圆')
        self.curve_bezier_btn				.setToolTip('Bezier算法绘制曲线')
        self.curve_b_spline_btn				.setToolTip('B-spline算法绘制曲线')
        self.translate_btn					.setToolTip('平移')
        self.rotate_btn						.setToolTip('旋转')
        self.scale_btn						.setToolTip('缩放')
        self.clip_cohen_sutherland_btn      .setToolTip('Cohen-Sutherland算法裁剪线段')
        self.clip_liang_barsky_btn          .setToolTip('Liang-Barsky算法裁剪线段')
        self.line_naive_btn                 .setCheckable(True)
        self.line_dda_btn                   .setCheckable(True)
        self.line_bresenham_btn             .setCheckable(True)
        self.polygon_dda_btn                .setCheckable(True)
        self.polygon_bresenham_btn          .setCheckable(True)
        self.ellipse_btn					.setCheckable(True)
        self.curve_bezier_btn				.setCheckable(True)
        self.curve_b_spline_btn				.setCheckable(True)
        self.translate_btn					.setCheckable(True)
        self.rotate_btn						.setCheckable(True)
        self.scale_btn						.setCheckable(True)
        self.clip_cohen_sutherland_btn      .setCheckable(True)
        self.clip_liang_barsky_btn          .setCheckable(True)
        ## Add Btn
        vbox_layout2.addWidget(self.line_naive_btn               )
        vbox_layout2.addWidget(self.line_dda_btn                 )
        vbox_layout2.addWidget(self.line_bresenham_btn           )
        # line  = QFrame(); line.setFrameShape(QFrame.HLine); vbox_layout2.addWidget(line)
        vbox_layout2.addWidget(self.polygon_dda_btn              )
        vbox_layout2.addWidget(self.polygon_bresenham_btn        )
        # line  = QFrame(); line.setFrameShape(QFrame.HLine); vbox_layout2.addWidget(line)
        vbox_layout2.addWidget(self.ellipse_btn			        )
        # line  = QFrame(); line.setFrameShape(QFrame.HLine); vbox_layout2.addWidget(line)
        vbox_layout2.addWidget(self.curve_bezier_btn		        )
        vbox_layout2.addWidget(self.curve_b_spline_btn		    )
        vbox_layout2.addWidget(self.set_pen_btn                 )
        # line  = QFrame(); line.setFrameShape(QFrame.HLine); vbox_layout.addWidget(linme)
        vbox_layout1.addWidget(self.translate_btn			    )
        vbox_layout1.addWidget(self.rotate_btn				    )
        vbox_layout1.addWidget(self.scale_btn				    )
        vbox_layout1.addWidget(self.clip_cohen_sutherland_btn    )
        vbox_layout1.addWidget(self.clip_liang_barsky_btn        )
        # line  = QFrame(); line.setFrameShape(QFrame.HLine); vbox_layout1.addWidget(line)
        vbox_layout1.addWidget(self.delete_btn                   )
        vbox_layout1.addWidget(self.reset_canvas_btn             )
        vbox_layout1.addWidget(self.export_btn                   )
        vbox_layout1.addWidget(self.exit_btn                     )
        ## Slots
        self.set_pen_btn                    .clicked.connect(self.set_pen_action              )
        self.delete_btn                     .clicked.connect(self.delete_action               )
        self.reset_canvas_btn               .clicked.connect(self.reset_canvas_action         )
        self.exit_btn                       .clicked.connect(qApp.quit                        )
        self.export_btn                     .clicked.connect(self.export_action               )
        self.line_naive_btn                 .clicked.connect(self.line_naive_action           )
        self.line_dda_btn                   .clicked.connect(self.line_dda_action             )
        self.line_bresenham_btn             .clicked.connect(self.line_bresenham_action       )
        self.polygon_dda_btn                .clicked.connect(self.polygon_dda_action          )
        self.polygon_bresenham_btn          .clicked.connect(self.polygon_bresenham_action    )
        self.ellipse_btn			        .clicked.connect(self.ellipse_action			  )
        self.curve_bezier_btn		        .clicked.connect(self.curve_bezier_action		  )
        self.curve_b_spline_btn		        .clicked.connect(self.curve_b_spline_action		  )
        self.translate_btn			        .clicked.connect(self.translate_action			  )
        self.rotate_btn				        .clicked.connect(self.rotate_action				  )
        self.scale_btn				        .clicked.connect(self.scale_action				  )
        self.clip_cohen_sutherland_btn      .clicked.connect(self.clip_cohen_sutherland_action)
        self.clip_liang_barsky_btn          .clicked.connect(self.clip_liang_barsky_action    )

        self.list_widget.currentTextChanged.connect(self.canvas_widget.selection_changed)
        self.canvas_widget.statusChanged.connect(self.updateUI)

        # 设置主窗口的布局
        self.hbox_layout = QHBoxLayout()
        # self.hbox_layout.addWidget(toolBar)
        self.hbox_layout.addLayout(vbox_layout2)
        self.hbox_layout.addWidget(self.canvas_widget)
        self.hbox_layout.addLayout(vbox_layout1)
        self.hbox_layout.addWidget(self.list_widget, stretch=1)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.hbox_layout)
        self.central_widget.setStyleSheet(self.centralStyleSheet)
        self.setCentralWidget(self.central_widget)
        self.statusBar().showMessage('空闲')
        self.resize(600, 600)
        self.setWindowTitle('Pytura')
        self.setWindowIcon(QIcon('asset/icon/pytura.ico'))
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")
        self.list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def get_id(self):
        _id = str(self.item_cnt)
        self.item_cnt += 1
        return _id

    # Description: file actions
    def set_pen_action(self):
        color = QColorDialog.getColor(self.canvas_widget.pen_color, self, '选择绘图颜色')
        self.canvas_widget.pen_color = color
        self.set_pen_btn.setStyleSheet('background: rgb(%d,%d,%d); \n %s' % (color.red(), color.green(), color.blue(), 
        """  
            max-width:  40px;
            max-height: 40px;
            min-width:  40px;
            min-height: 40px;
            margin: 0px 0px 6px 2px;
            border-width: 2px;
            border-style: outset;
            border-color: white;
            border-image: none;
            """)
        )

    def reset_canvas_action(self):
        self.scene.clear()
        self.list_widget.clear()
        self.canvas_widget.item_dict.clear()
        self.item_cnt = 0

    def delete_action(self):
        self.canvas_widget.delete_selection()
        self.list_widget.takeItem(self.list_widget.selectedIndexes()[0].row())

    def export_action(self):
        filename = QFileDialog.getSaveFileName(self,'save file','/home/jm/study')
        print("SHIt")

    # Description: line actions
    def line_naive_action(self):
        self.canvas_widget.start_draw('line','Naive', self.get_id())
        # self.statusBar().showMessage('Naive算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_dda_action(self):
        self.canvas_widget.start_draw('line','DDA', self.get_id())
        # self.statusBar().showMessage('DDA算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_bresenham_action(self):
        self.canvas_widget.start_draw('line','Bresenham', self.get_id())
        # self.statusBar().showMessage('Bresenham算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    # Description: polygon actions
    def polygon_dda_action(self):
        self.canvas_widget.start_draw('polygon','DDA', self.get_id())
        # self.statusBar().showMessage('DDA算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_bresenham_action(self):
        self.canvas_widget.start_draw('polygon','Bresenham', self.get_id())
        # self.statusBar().showMessage('Bresenham算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    # Description: ellipse actions
    def ellipse_action(self):
        self.canvas_widget.start_draw('ellipse','', self.get_id())
        # self.statusBar().showMessage('中点圆生成算法绘制椭圆')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    # Description: curve actions
    def curve_bezier_action(self):
        self.canvas_widget.start_draw('curve','Bezier', self.get_id())
        # self.statusBar().showMessage('Bezier算法绘制曲线')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_b_spline_action(self):
        self.canvas_widget.start_draw('curve','B-spline', self.get_id())
        # self.statusBar().showMessage('B-spline算法绘制曲线')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    # Description: edit actions
    def translate_action(self):
        self.canvas_widget.start_edit('translate','')
        # self.statusBar().showMessage('平移')

    def rotate_action(self):
        self.canvas_widget.start_edit('rotate','')
        # self.statusBar().showMessage('旋转')

    def scale_action(self):
        self.canvas_widget.start_edit('scale','')
        # self.statusBar().showMessage('缩放')

    # Description: clip actions
    def clip_cohen_sutherland_action(self):
        self.canvas_widget.start_clip('clip','Cohen-Sutherland')
        # self.statusBar().showMessage('Cohen-Sutherland算法裁剪线段')

    def clip_liang_barsky_action(self):
        self.canvas_widget.start_clip('clip','Liang-Barsky')
        # self.statusBar().showMessage('Liang-Barsky算法裁剪线段')


    def updateUI(self, old, new, algorithm):
        self.line_naive_btn                 .setChecked(False)
        self.line_dda_btn                   .setChecked(False)
        self.line_bresenham_btn             .setChecked(False)
        self.polygon_dda_btn                .setChecked(False)
        self.polygon_bresenham_btn          .setChecked(False)
        self.ellipse_btn					.setChecked(False)
        self.curve_bezier_btn				.setChecked(False)
        self.curve_b_spline_btn				.setChecked(False)
        self.translate_btn					.setChecked(False)
        self.rotate_btn						.setChecked(False)
        self.scale_btn						.setChecked(False)
        self.clip_cohen_sutherland_btn      .setChecked(False)
        self.clip_liang_barsky_btn          .setChecked(False)
        
        if new == '':
            message = '空闲'
        elif new == 'line':
            message = algorithm + '算法绘制线段'
            if algorithm == 'Naive':
                self.line_naive_btn                 .setChecked(True)
            elif algorithm == 'DDA':
                self.line_dda_btn                   .setChecked(True)
            elif algorithm == 'Bresenham':
                self.line_bresenham_btn             .setChecked(True)
        elif new == 'polygon':
            message = algorithm + '算法绘制多边形'
            if algorithm == 'DDA':
                self.polygon_dda_btn                   .setChecked(True)
            elif algorithm == 'Bresenham':
                self.polygon_bresenham_btn             .setChecked(True)
        elif new == 'ellipse':
            message = '中点圆算法绘制椭圆'
            self.ellipse_btn					.setChecked(True)
        elif new == 'curve':
            message = algorithm + '算法绘制曲线'
            if algorithm == 'Bezier':
                self.curve_bezier_btn				.setChecked(True)
            elif algorithm == 'B-spline':
                self.curve_b_spline_btn				.setChecked(True)
        elif new == 'translate':
            message = '平移'
            self.translate_btn					.setChecked(True)
        elif new == 'rotate':
            message = '旋转'
            self.rotate_btn						.setChecked(True)
        elif new == 'scale':
            message = '缩放'
            self.scale_btn						.setChecked(True)
        elif new == 'clip':
            message = algorithm + '算法裁剪线段'
            if algorithm == 'Cohen-Sutherland':
                self.clip_cohen_sutherland_btn      .setChecked(True)
            elif algorithm == 'Liang-Barsky':
                self.clip_liang_barsky_btn          .setChecked(True)
        self.statusBar().showMessage(message)
        


class SplashScreen(QSplashScreen):
    def __init__(self):
        super(SplashScreen, self).__init__(QPixmap("asset/img/splash.png"))
        self.steps = 20.0
    def effect(self):
        self.setWindowOpacity(0)
        t = 0
        while t <= self.steps:
            newOpacity = self.windowOpacity() + 1/self.steps
            if newOpacity > 1: break
            self.setWindowOpacity(newOpacity)
            self.show()
            t -= 1
            time.sleep(0.01)

        time.sleep(1)
        t = 0
        while t <= self.steps:
            newOpacity = self.windowOpacity() - 1/self.steps
            if newOpacity < 0: break
            self.setWindowOpacity(newOpacity)
            t += 1
            time.sleep(0.01)
        self.setWindowOpacity(0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    splash = SplashScreen()
    splash.effect()
    app.processEvents()
    mw = MainWindow()
    mw.show()
    splash.finish(mw)
    sys.exit(app.exec_())

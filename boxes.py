from PySide import QtCore, QtGui

import ConfigParser
import keybinder

import signal
import sys
import os

from windows import WindowHelper

CONFIG = os.path.expanduser('~/.boxes')
DEFAULTS = {
        'grid_columns': 8,
        'grid_rows': 4,
        'hotkey': 'Alt+R',
        'background_color': 'rgba(75, 77, 81, 255)',
        'box_background_color': 'rgba(100, 106, 116, 204)',
        'selected_box_background_color': 'rgba(50, 53, 58, 204)'
}

class SelectionGrid(QtGui.QFrame):


    reset_grid = QtCore.Signal()
    highlight_selection = QtCore.Signal()

    def __init__(self, desktop):
        super(SelectionGrid, self).__init__()

        dimensions = desktop.availableGeometry()
        self.screen_width = dimensions.width()
        self.screen_height = dimensions.height()

        self.windows = WindowHelper()

        self.load_config()
        keybinder.bind(self.settings['hotkey'], self.toggle)
        self.construct_grid()
        self.init_grid_ui()

    def construct_grid(self):
        self.grid = QtGui.QGridLayout(self)

        for i in range(1, self.settings['grid_rows'] + 1):
            for j in range(1, self.settings['grid_columns'] + 1):
                grid_box = GridBox(self, i, j)
                self.grid.addWidget(grid_box, i, j)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            grid_box = self.childAt(event.x(), event.y())
            color = self.settings['selected_box_background_color']
            grid_box.setStyleSheet('background-color: {color};border:none;'.format(color=color))
            row, col = self.get_box_position(grid_box)

            self.current_selection = {
                    'start_row': row,
                    'start_col': col
            }

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.windows.resize_window(*self.calculate_resize())
            self.hide()
            self.reset_grid.emit()

    def mouseMoveEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            grid_box = self.childAt(event.x(), event.y())
            if grid_box:
                row, col = self.get_box_position(grid_box)

                self.current_selection['outer_x'] = col
                self.current_selection['outer_y'] = row

                self.highlight_selection.emit()

    def calculate_resize(self):
        y1 = self.current_selection['start_row']
        y2 = self.current_selection['outer_y']
        x1 = self.current_selection['start_col']
        x2 = self.current_selection['outer_x']

        start_x, end_x = sorted((x1, x2))
        start_y, end_y = sorted((y1, y2))

        box_size_x = self.screen_width / self.settings['grid_columns']
        box_size_y = self.screen_height / self.settings['grid_rows']

        x_pos = (start_x - 1) * box_size_x
        y_pos = (start_y - 1) * box_size_y
        size_x = box_size_x * (end_x - start_x + 1)
        size_y = box_size_y * (end_y - start_y + 1)

        return (self.active_window_id, x_pos, y_pos, size_x, size_y)

    def get_box_position(self, grid_box):
        index = self.grid.indexOf(grid_box)
        row, col, __, __ = self.grid.getItemPosition(index)

        return (row, col)

    def init_grid_ui(self):
        w = self.settings['grid_window_width']
        h = self.settings['grid_window_height']

        x = (self.screen_width - w) / 2
        y = (self.screen_height - h) / 2

        self.setGeometry(x, y, w, h)
        self.setWindowTitle('boxes')
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        color = self.settings['background_color']
        self.setStyleSheet(
                'background-color: {color};'
                'border-radius: 5px;'
                .format(color=color)
        )

    def show_grid(self):
        self.active_window_id = self.windows.get_active_window()
        self.show()

    def toggle(self):
        if self.isVisible():
            self.hide()
        else:
            self.show_grid()

    def load_config(self):
        self.settings = DEFAULTS

        self.settings['grid_window_width'] = self.screen_width / 3.5
        self.settings['grid_window_height'] = self.screen_height / 3.5

        if os.path.isfile(CONFIG):
            cfg = ConfigParser.ConfigParser()

            with open(CONFIG) as f:
                cfg.readfp(f)

            for option in self.settings:
                method = 'getint' if type(self.settings[option]) == int else 'get'

                try:
                    self.settings[option] = getattr(cfg, method)('Grid', option)
                except:
                    continue


class GridBox(QtGui.QFrame):


    def __init__(self, parent, row, col):
        super(GridBox, self).__init__(parent)
        parent.reset_grid.connect(self.reset_defaults)
        parent.highlight_selection.connect(self.on_selection_update)

        self.row = row
        self.col = col
        self.bg_color = parent.settings['box_background_color']
        self.selected_bg_color = parent.settings['selected_box_background_color']
        self.parent = parent

        self.setFrameShape(QtGui.QFrame.StyledPanel)
        self.setStyleSheet('background-color: {color};border:none;'.format(color=self.bg_color))

    def reset_defaults(self):
        self.setStyleSheet('background-color: {color};border:none;'.format(color=self.bg_color))

    def on_selection_update(self):
        start_x = self.parent.current_selection['start_col']
        start_y = self.parent.current_selection['start_row']
        outer_x = self.parent.current_selection['outer_x']
        outer_y = self.parent.current_selection['outer_y']

        x_bounds = sorted((start_x, outer_x))
        y_bounds = sorted((start_y, outer_y))

        selected_x = x_bounds[0] <= self.col <= x_bounds[1]
        selected_y = y_bounds[0] <= self.row <= y_bounds[1]
        if selected_x and selected_y:
            self.setStyleSheet('background-color: {color};border:none;'.format(color=self.selected_bg_color))
        else:
            self.reset_defaults()


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QtGui.QApplication([])
    desktop = app.desktop()
    grid = SelectionGrid(desktop)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

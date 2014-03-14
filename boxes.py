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
        'selected_box_background_color': 'rgba(50, 53, 58, 0.8)'
}

class SelectionGrid(QtGui.QFrame):


    reset_grid = QtCore.Signal()

    def __init__(self, desktop):
        super(SelectionGrid, self).__init__()

        dimensions = desktop.availableGeometry()
        self.screen_width = dimensions.width()
        self.screen_height = dimensions.height()

        self.windows = WindowHelper()

        self.load_config()
        keybinder.bind(self.settings['hotkey'], self.toggle)
        self.construct_grid()

    def construct_grid(self):
        self.grid = QtGui.QGridLayout(self)

        for i in range(1, self.settings['grid_rows'] + 1):
            for j in range(1, self.settings['grid_columns'] + 1):
                grid_box = GridBox(self)
                self.grid.addWidget(grid_box, i, j)

    def mousePressEvent(self, event):
        grid_box = self.childAt(event.x(), event.y())
        color = self.settings['selected_box_background_color']
        grid_box.setStyleSheet('background-color: {color};'.format(color=color))
        row, col = self.get_box_position(grid_box)

        self.current_selection = {
                'start_row': row,
                'start_col': col
        }

    def mouseReleaseEvent(self, event):
        grid_box = self.childAt(event.x(), event.y())
        row, col = self.get_box_position(grid_box)

        self.current_selection['end_row'] = row
        self.current_selection['end_col'] = col

        self.calculate_resize()

    def calculate_resize(self):
        y1 = self.current_selection['start_row']
        y2 = self.current_selection['end_row']
        x1 = self.current_selection['start_col']
        x2 = self.current_selection['end_col']

        start_x, end_x = sorted((x1, x2))
        start_y, end_y = sorted((y1, y2))

        box_size_x = self.screen_width / self.settings['grid_columns']
        box_size_y = self.screen_height / self.settings['grid_rows']

        x_pos = (start_x - 1) * box_size_x
        y_pos = (start_y - 1) * box_size_y
        size_x = box_size_x * (end_x - start_x + 1)
        size_y = box_size_y * (end_y - start_y + 1)

        self.windows.resize_window(self.active_window_id, x_pos, y_pos, size_x, size_y)
        self.hide()
        self.reset_grid.emit()

    def get_box_position(self, grid_box):
        index = self.grid.indexOf(grid_box)
        row, col, __, __ = self.grid.getItemPosition(index)

        return (row, col)

    def show_grid(self):
        w = self.settings['grid_window_width']
        h = self.settings['grid_window_height']

        x = (self.screen_width - w) / 2
        y = (self.screen_height - h) / 2

        self.setGeometry(x, y, w, h)
        self.setWindowTitle('boxes')
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        color = self.settings['background_color']
        self.setStyleSheet('background-color: {color};'.format(color=color))

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


    def __init__(self, parent):
        super(GridBox, self).__init__(parent)
        parent.reset_grid.connect(self.reset_defaults)

        self.setFrameShape(QtGui.QFrame.StyledPanel)
        self.bg_color = parent.settings['box_background_color']
        self.setStyleSheet('background-color: {color};'.format(color=self.bg_color))

    def reset_defaults(self):
        self.setStyleSheet('background-color: {color};'.format(color=self.bg_color))


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QtGui.QApplication([])
    desktop = app.desktop()
    grid = SelectionGrid(desktop)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

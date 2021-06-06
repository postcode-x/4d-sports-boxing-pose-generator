import struct
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
import matplotlib.figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import sys
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import copy
import matplotlib
import os
from movetest import *

moves = carlton


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.pose_index = 0
        self.point_index = 0
        self.size = 0
        self.current_full_filename = ''
        self.current_filename = ''
        self.limits = 96

        self.x_ = []
        self.y_ = []
        self.z_ = []
        self.body_data = ()
        self.body_data_copy = ()

        self.setFixedSize(500, 600)
        self.setWindowTitle('PoseEditor')
        self.center()

        main_layout = QtWidgets.QVBoxLayout()
        layout_left = QtWidgets.QVBoxLayout()

        self.figure = matplotlib.figure.Figure()  # Plot
        self.canvas = FigureCanvas(self.figure)
        self.axes = Axes3D(self.figure)

        group_box = QtWidgets.QGroupBox("Editing:")

        self.expression_slider = QtWidgets.QSlider(Qt.Horizontal)
        self.expression_slider.valueChanged.connect(self.expression_slider_change)
        self.expression_slider.setValue(0)
        self.expression_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.expression_slider.setTickInterval(2)
        self.expression_slider.setEnabled(False)

        self.load_button = QtWidgets.QPushButton('Load', self)
        self.load_button.clicked.connect(self.load_data)

        self.save_button = QtWidgets.QPushButton('Save', self)
        self.save_button.clicked.connect(self.save_data)

        self.delete_button = QtWidgets.QPushButton('Delete', self)
        self.delete_button.clicked.connect(self.delete_pose)

        self.exp_slider_label = QtWidgets.QLabel("Pose : 1")

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.load_button)
        hbox.addWidget(self.save_button)
        hbox.addWidget(self.delete_button)

        allitems = QtWidgets.QVBoxLayout()
        allitems.addLayout(hbox)

        group_box.setLayout(allitems)

        layout_left.addWidget(self.canvas)
        layout_left.addWidget(self.expression_slider)

        main_layout.addLayout(layout_left)
        main_layout.addWidget(group_box)
        self.setLayout(main_layout)

        self.axes.view_init(20, 60)
        self.plot_3d()

    def expression_slider_change(self):
        self.pose_index = self.expression_slider.value()
        self.setWindowTitle('PoseEditor - Pose: ' + str(self.expression_slider.value() + 1))
        self.load_pose()
        self.plot_3d()

    def load_data(self):

        points = []
        filename = 'TRAIN-ORIGINAL.DAT'

        if filename != '':

            f = open(filename, 'rb')

            try:

                head, tail = os.path.split(str(filename))
                self.current_full_filename = str(filename)
                self.current_filename = tail

                with f:
                    while 1:
                        input_stream = f.read(2)
                        if not input_stream:
                            f.close()
                            break
                        points.append(struct.unpack('<h', input_stream)[0])

            finally:
                f.close()

                points_x = []
                points_y = []
                points_z = []

                # ORIGINAL TRAIN.DAT LOADING

                '''for n in range(0, int(len(points) / 3)):
                    points_x.append(points[3 * n])
                    points_y.append(points[3 * n + 1])
                    points_z.append(points[3 * n + 2])'''

                # CARLTON

                carl_translate = [640, 680]
                tmp = []
                for u in range(0, 23):
                    tmp.append(points[3 * u + 2] - 20)

                for n in range(0, len(moves)):
                    for k in range(0, 23):
                        points_x.append(-moves[n][3 * k] + carl_translate[0])
                        points_y.append(-(round((moves[n][3 * k + 1]))) + carl_translate[1])
                        if k < 12:
                            points_z.append(moves[n][3 * k + 2])
                        else:
                            points_z.append(tmp[k])

                # END CARLTON

                self.body_data = (copy.copy(points_x), copy.copy(points_y), copy.copy(points_z))
                self.body_data_copy = copy.deepcopy(self.body_data)

                self.expression_slider.setMinimum(0)
                self.expression_slider.setMaximum(int(len(self.body_data[0])/23) - 1)
                self.expression_slider.setValue(0)
                self.expression_slider.setEnabled(True)

                self.load_pose()
                self.plot_3d()

        else:

            self.show_dialog()

    def delete_pose(self):

        points_per_body = 23
        start = self.pose_index * points_per_body
        stop = start + points_per_body

        del self.body_data[0][start:stop]
        del self.body_data[1][start:stop]
        del self.body_data[2][start:stop]

        if self.pose_index == 0:
            self.expression_slider.setValue(1)
            self.pose_index += 1
        elif self.pose_index == self.expression_slider.maximum():
            self.expression_slider.setValue(self.expression_slider.maximum()-1)
            self.pose_index -= 1
        else:
            self.expression_slider.setValue(self.expression_slider.value()-1)
            self.pose_index += 1

        self.expression_slider.setMaximum(self.expression_slider.maximum()-1)

        self.load_pose()

    def load_pose(self):

        points_per_body = 23
        start = self.pose_index * points_per_body
        stop = start + points_per_body

        self.x_ = copy.copy(self.body_data[0][start:stop])
        self.y_ = copy.copy(self.body_data[1][start:stop])
        self.z_ = copy.copy(self.body_data[2][start:stop])

    def save_data(self):

        output_list = []
        current_data = copy.copy(self.body_data)
        for k in range(0, len(current_data[0])):
            output_list.append(current_data[0][k])
            output_list.append(current_data[1][k])
            output_list.append(current_data[2][k])
        with open('OUTPUTCARLTON.DAT', 'wb') as f:
            for n in range(0, len(output_list)):
                f.write(struct.pack('<h', output_list[n]))
        f.close()

    def plot_3d(self):

        self.axes.clear()

        lim = 320

        self.axes.set_facecolor('#C0C0C0')
        self.axes.grid(False)
        self.axes.set_xlim(-lim, lim)

        self.axes.xaxis.set_ticks(np.arange(-lim, lim + 1, lim / 4))
        self.axes.set_ylim(-lim, lim)
        self.axes.yaxis.set_ticks(np.arange(-lim, lim + 1, lim / 4))
        self.axes.set_zlim(0, 2*lim)
        self.axes.zaxis.set_ticks(np.arange(0, 2*lim + 1, lim / 4))

        self.axes.set_xticks([])
        self.axes.set_yticks([])
        self.axes.set_zticks([])

        self.axes.set_axis_off()
        '''self.axes.set_xlabel('x', fontsize=6, color='white')
        self.axes.set_ylabel('z', fontsize=6, color='white')
        self.axes.set_zlabel('y', fontsize=6, color='white')'''

        self.axes.tick_params(axis='x', colors='white', labelsize=6)
        self.axes.tick_params(axis='z', colors='white', labelsize=6)
        self.axes.tick_params(axis='y', colors='white', labelsize=6)

        self.axes.w_xaxis.set_pane_color((1, 1, 1, 0))
        self.axes.w_yaxis.set_pane_color((1, 1, 1, 0))
        self.axes.w_zaxis.set_pane_color((1, 1, 1, 0))

        # MAIN ROUTINE

        if self.current_filename != '':

            # LEGS

            legs = ([], [], [])

            for i in range(0, 11):
                legs[0].append(self.x_[i])
                legs[1].append(self.y_[i])
                legs[2].append(self.z_[i])

            index_torso = [13, 12, 11, 5]
            head_torso = ([], [], [])

            for i in range(0, len(index_torso)):
                head_torso[0].append(self.x_[index_torso[i]])
                head_torso[1].append(self.y_[index_torso[i]])
                head_torso[2].append(self.z_[index_torso[i]])

            index_right_arm = [12, 14, 15, 16, 17]
            index_left_arm = [12, 18, 19, 20, 21]
            right_arm = ([], [], [])
            left_arm = ([], [], [])

            for i in range(0, len(index_right_arm)):
                right_arm[0].append(self.x_[index_right_arm[i]])
                right_arm[1].append(self.y_[index_right_arm[i]])
                right_arm[2].append(self.z_[index_right_arm[i]])
                left_arm[0].append(self.x_[index_left_arm[i]])
                left_arm[1].append(self.y_[index_left_arm[i]])
                left_arm[2].append(self.z_[index_left_arm[i]])

            self.axes.plot(legs[0], legs[2], legs[1], color='purple')
            self.axes.plot(head_torso[0], head_torso[2], head_torso[1], color='green')
            self.axes.plot(right_arm[0], right_arm[2], right_arm[1], color='blue')
            self.axes.plot(left_arm[0], left_arm[2], left_arm[1], color='blue')

            self.axes.scatter(self.x_, self.z_, self.y_, color='black', s=2)

            for k in range(0, len(self.x_)):
                self.axes.text3D(self.x_[k], self.z_[k], self.y_[k], str(k), color='black', fontsize=6, alpha=0.75,
                                 zorder=50)

        self.canvas.draw_idle()

    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

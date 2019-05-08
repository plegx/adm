#!/usr/bin/env python3
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *
import sys


class MainUI(QMainWindow):
    def __init__(self):
        super(MainUI, self).__init__()
        self.master_layout = QGridLayout(self)

        self.recording = RecordingSettings()
        self.measure = MeasureSettings()
        self.file =  FileSettings()
        self.audio_settings = AudioSettings()

        self.master_layout.addLayout(self.audio_settings, 0, 0)
        self.master_layout.addLayout(self.file, 2, 0)
        self.master_layout.addLayout(self.measure, 3, 0)
        self.master_layout.addLayout(self.recording, 4, 0)

        self.apply_audio_settings = QPushButton('Apply Settings', self)
        self.master_layout.addWidget(self.apply_audio_settings, 1, 0)
        self.setCentralWidget(self.master_layout)
        self.show()


class AudioSettings(QWidget):

    def __init__(self):
        super(AudioSettings, self).__init__()
        self.audio_layout = QGridLayout(self)
        self.add_audio_settings()
        self.setLayout(self.audio_layout)

    def add_audio_settings(self):
        self.settings = QLabel(self)
        self.settings.setText('Audio Settings')
        self.audio_layout.addWidget(self.settings, 0, 0)

        self.get_input_device = QComboBox(self)
        self.get_input_device.addItem('Select Input Device')
        self.audio_layout.addWidget(self.get_input_device, 1, 0)

        self.get_channels_number = QComboBox(self)
        self.get_channels_number.addItem('Number of Channels')
        self.audio_layout.addWidget(self.get_channels_number, 1, 1)

        self.set_recording_length = QLineEdit(self)
        self.set_recording_length.setText('Recording Duration (seconds)')
        self.set_recording_length.setValidator(QtGui.QDoubleValidator())
        self.audio_layout.addWidget(self.set_recording_length, 1, 2)

        self.get_output_device = QComboBox(self)
        self.get_output_device.addItem('Select Output Device')
        self.audio_layout.addWidget(self.get_output_device, 2, 0)

        self.get_excitation_signal = QComboBox(self)
        self.get_excitation_signal.addItem('Select excitation signal (None)')
        self.get_excitation_signal.addItem('Sine')
        self.get_excitation_signal.addItem('Linear Sweep')
        self.get_excitation_signal.addItem('Exponential Sweep')
        self.audio_layout.addWidget(self.get_excitation_signal, 2, 1)

        self.silence_size = QLabel(self)
        self.silence_size.setText('Silent time frame duration :')
        self.audio_layout.addWidget(self.silence_size, 2, 2)

        self.set_excitation_fmin = QLineEdit(self)
        self.set_excitation_fmin.setText('20')
        self.set_excitation_fmin.setValidator(QtGui.QDoubleValidator())
        self.set_excitation_fmin.setEnabled(False)
        self.audio_layout.addWidget(self.set_excitation_fmin, 3, 0)

        self.set_excitation_fmax = QLineEdit(self)
        self.set_excitation_fmax.setText('20000')
        self.set_excitation_fmax.setValidator(QtGui.QDoubleValidator())
        self.set_excitation_fmax.setEnabled(False)
        self.audio_layout.addWidget(self.set_excitation_fmax, 3, 1)

        self.set_silence_size = QLineEdit(self)
        self.set_silence_size.setText('0.5')
        self.set_silence_size.setValidator(QtGui.QDoubleValidator())
        self.audio_layout.addWidget(self.set_silence_size, 3, 2)


class FileSettings(QWidget):

    def __init__(self):
        super(FileSettings, self).__init__()
        self.file_layout = QGridLayout(self)
        self.add_file_settings()
        self.setLayout(self.file_layout)

    def add_file_settings(self):
        self.settings = QLabel(self)
        self.settings.setText('File Management Settings')
        self.file_layout.addWidget(self.settings, 0, 0)

        self.set_directory = QLineEdit(self)
        self.set_directory.setText('/Users/Tom/Desktop/') # '/Path/to/directory/'
        self.file_layout.addWidget(self.set_directory, 1, 0)

        self.apply_directory = QPushButton('Set Path', self)
        self.file_layout.addWidget(self.apply_directory, 1, 2)

        self.set_directory.setEnabled(False)
        self.apply_directory.setEnabled(False)


class MeasureSettings(QWidget):

    def __init__(self):
        super(MeasureSettings, self).__init__()
        self.measure_layout = QGridLayout(self)
        self.add_measure_settings()
        self.setLayout(self.measure_layout)

    def add_measure_settings(self):
        self.settings = QLabel(self)
        self.settings.setText('Measurement Settings')
        self.measure_layout.addWidget(self.settings, 0, 0)

        self.name = QLabel(self)
        self.name.setText('Measurement Name :')
        self.measure_layout.addWidget(self.name, 1, 0)

        self.set_name = QLineEdit(self)
        self.set_name.setText('Name')
        self.set_name.resize(80, 40)
        self.measure_layout.addWidget(self.set_name, 1, 1)

        self.angle_step = QLabel(self)
        self.angle_step.setText('Angle Step :')
        self.measure_layout.addWidget(self.angle_step, 1, 2)

        self.set_angle_step = QLineEdit(self)
        self.set_angle_step.setText('180')
        self.set_angle_step.setValidator(QtGui.QIntValidator())
        self.measure_layout.addWidget(self.set_angle_step, 1, 3)

        self.set_name.setEnabled(False)
        self.set_angle_step.setEnabled(False)


class RecordingSettings(QWidget):

    def __init__(self):
        super(RecordingSettings, self).__init__()
        self.recording_layout = QGridLayout(self)
        self.add_recording_settings()
        self.setLayout(self.recording_layout)

    def add_recording_settings(self):
        self.apply_recording = QPushButton('Start Measurement', self)
        self.recording_layout.addWidget(self.apply_recording, 0, 0)

        self.measure_info = QLabel(self)
        self.measure_info.setText('Waiting Record')
        self.recording_layout.addWidget(self.measure_info, 1, 0)

        self.progress = QProgressBar(self)
        self.recording_layout.addWidget(self.progress, 2, 0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    screenSize = app.primaryScreen().size()
    mainUI = MainUI()
    sys.exit(app.exec_())

#!/usr/bin/env python3
from PyQt5 import QtCore, QtGui
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import raw_ui as raw
import numpy as np
import pyaudio
import serial
import time
import wave
import sys
import os


class MainUI(QMainWindow):
    STREAM_DTYPE = pyaudio.paInt16
    DTYPE = np.int16
    CHUNK_SIZE = 4096
    FS = 44100

    def __init__(self):
        super().__init__()
        self.winSize = (900, 300)
        self.setGeometry(screenSize.width() // 2 - self.winSize[0] / 2, 500, self.winSize[0], self.winSize[1])
        self.setWindowTitle('Directivity Measurement Helper')

        self.measurementAngle = 0
        self.turnTableConnected = False
        self.parentDirectoryPath = '/Path/to/directory/'

        self.pAudio = pyaudio.PyAudio()
        hostInfo = self.pAudio.get_host_api_info_by_index(0)
        self.DEVICE_COUNT = hostInfo.get('deviceCount')

        self.audioAcquisition = AudioAcquisition()
        self.audioExcitation = AudioExcitation()
        self.inputSet = False
        self.outputSet = False
        self.inputDeviceIndexes = []
        self.outputDeviceIndexes = []
        self.audioAcquisition.recordingDone.connect(self.handleRecording)
        self.uiElements()
        self.connect_uiElements()

        self.quit = QAction("Quit", self)
        self.quit.triggered.connect(self.closeEvent)
        self.show()
        self.turnTableInit()

    def uiElements(self):
        self.plotWin = PlotWindow()

        self.master = QWidget(self)
        self.master_layout = QGridLayout(self)
        self.recording = raw.RecordingSettings()
        self.measure = raw.MeasureSettings()
        self.file =  raw.FileSettings()
        self.audio_settings = raw.AudioSettings()

        self.master_layout.addWidget(self.audio_settings, 0, 0)
        self.master_layout.addWidget(self.file, 2, 0)
        self.master_layout.addWidget(self.measure, 3, 0)
        self.master_layout.addWidget(self.recording, 4, 0)

        self.apply_audio_settings = QPushButton('Apply Settings', self)
        self.apply_audio_settings.clicked.connect(self.applyAudioSettings)
        self.master_layout.addWidget(self.apply_audio_settings, 1, 0)
        self.master.setLayout(self.master_layout)
        self.setCentralWidget(self.master)

        self.initMeasurement()

    def closeEvent(self, event):
        closeMessage = QMessageBox()
        closeMessage.setText('Quit Application?')
        closeMessage.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        closeMessage = closeMessage.exec()
        if closeMessage == QMessageBox.Yes:
            self.audioAcquisition.clean()
            self.audioExcitation.clean()
            self.pAudio.terminate()
            app.closeAllWindows()
            event.accept()
        else:
            event.ignore()

    def turnTableInit(self):
        try:
            self.arduSer = serial.Serial('/dev/tty.wchusbserial141230', 9600, timeout=2) # Specify the correct path to the arduino serial port
            self.turnTableConnected = True
            self.arduSer.close()
            QMessageBox.information(self, 'Info', 'Turn Table Connected!', QMessageBox.Ok, QMessageBox.Ok)
        except:
            QMessageBox.information(self, 'Info', 'No Turn Table connected...', QMessageBox.Ok, QMessageBox.Ok)

    def connect_uiElements(self):
        self.file.apply_directory.clicked.connect(self.setDirectoryPath)
        for deviceIndex in range(0, self.DEVICE_COUNT):
            device = self.pAudio.get_device_info_by_host_api_device_index(0, deviceIndex)
            if device['maxInputChannels'] > 0:
                self.inputDeviceIndexes.append(deviceIndex)
                self.audio_settings.get_input_device.addItem('{} ({} Channels)'.format(device['name'], device['maxInputChannels']))
        self.audio_settings.get_input_device.activated.connect(self.setInputDevice)

        for deviceIndex in range(0, self.DEVICE_COUNT):
            device = self.pAudio.get_device_info_by_host_api_device_index(0, deviceIndex)
            if device['maxOutputChannels'] > 0:
                self.outputDeviceIndexes.append(deviceIndex)
                self.audio_settings.get_output_device.addItem('{} ({} Channels)'.format(device['name'], device['maxOutputChannels']))
        self.audio_settings.get_output_device.activated.connect(self.setOutputDevice)

        self.audio_settings.get_excitation_signal.activated.connect(self.set_layout_excitation_signal)


    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.abortMeasurement()

    def abortMeasurement(self):
        self.audioAcquisition.terminate()
        self.audioAcquisition.clean()
        self.audioExcitation.terminate()
        self.audioExcitation.clean()
        self.pAudio.terminate()

    def setInputDevice(self, selectorIndex):
        if selectorIndex != 0:
            self.inputDeviceIndex = self.inputDeviceIndexes[selectorIndex-1]
            self.inputDevice = self.pAudio.get_device_info_by_host_api_device_index(0, self.inputDeviceIndex)
            # Update Channels Selector
            self.audio_settings.get_channels_number.clear()
            for channelIndex in range(1, self.inputDevice['maxInputChannels']+1):
                self.audio_settings.get_channels_number.addItem('{} Channels'.format(channelIndex))
            self.audio_settings.get_channels_number.activated.connect(self.setNbOfChannels)
            self.nbOfInputChannels = 1 # Set 1 as default
            self.inputSet = True
        else:
            self.inputSet = False

    def setOutputDevice(self, selectorIndex):
        if selectorIndex != 0:
            self.outputDeviceIndex = self.outputDeviceIndexes[selectorIndex-1]
            self.outputDevice = self.pAudio.get_device_info_by_host_api_device_index(0, self.outputDeviceIndex)
            self.nbOfOutputChannels = self.outputDevice['maxOutputChannels']
            self.outputSet = True
        else:
            self.outputSet = False

    def setNbOfChannels(self, inputNbOfChannels):
        self.nbOfInputChannels = inputNbOfChannels+1

    def applyAudioSettings(self):
        if self.inputSet & self.outputSet:
            try:
                self.recordingLength = float(self.audio_settings.set_recording_length.text().replace(',', '.'))
                self.audio_settings.set_recording_length.setText('{:.2f} seconds'.format(self.recordingLength))
                if self.audio_settings.get_excitation_signal.currentIndex() != 0:
                    self.audioExcitation.outputExcitationSignal = True
                    self.audioExcitation.get_excitation(self.audio_settings.get_excitation_signal.currentText(), float(self.audio_settings.set_silence_size.text()))
                self.set_layout_apply_audio()
                self.plotWin.addPlotPerCannels()
            except:
                QMessageBox.information(self, 'Error', 'Invalid Settings', QMessageBox.Ok, QMessageBox.Ok)
        elif not self.inputSet:
            QMessageBox.information(self, 'Info', 'No Input Selected...', QMessageBox.Ok, QMessageBox.Ok)
        elif not self.outputSet:
            QMessageBox.information(self, 'Info', 'No Output Selected...', QMessageBox.Ok, QMessageBox.Ok)

    def setDirectoryPath(self):
        if os.path.exists(self.file.set_directory.text()):
            self.parentDirectoryPath = os.path.join(self.file.set_directory.text())
            self.set_layout_apply_file()
        else:
            QMessageBox.question(self, 'Error', 'Invalid Path', QMessageBox.Ok, QMessageBox.Ok)

    def fileManagement(self):
        self.measurementDirPath = os.path.join(self.parentDirectoryPath, self.file.set_directory.text())
        if not os.path.exists(self.measurementDirPath):
            os.mkdir(self.measurementDirPath)

    def initMeasurement(self):
        self.measurementAngle = 0
        self.recording.progress.setValue(0)
        self.recording.apply_recording.clicked.connect(self.startMeasurement)
        self.recording.apply_recording.setText('Start Measurement')
        self.update()

    def startMeasurement(self):
        self.recording.apply_recording.setText('Abort')
        self.recording.apply_recording.clicked.connect(self.abortMeasurement)
        self.update()
        QApplication.processEvents()
        self.fileManagement()
        # self.audio.waveFileExportExcitationSignal()
        self.audioAcquisition.initStream()
        self.audioExcitation.initStream()
        self.audioAcquisition.start()
        self.audioExcitation.start()
        self.recording.measure_info.setText('Recording {}deg_{}.wav ...'.format(self.measurementAngle, self.measure.set_name.text()))
        QApplication.processEvents()

    def handlePlot(self):
        audioData = np.array([])
        for frame in self.audioAcquisition.pAudioFrames:
            audioData = np.append(audioData, np.frombuffer(frame, dtype=MainUI.DTYPE)) # int16
        audioData = audioData.reshape((len(self.audioAcquisition.pAudioFrames) * self.CHUNK_SIZE, self.nbOfInputChannels)).T
        self.plotWin.update(audioData)

    def handleRecording(self):
        self.handlePlot()
        self.audioAcquisition.waveFileExport()
        if self.turnTableConnected:
            self.rotateTurnTable()
        self.measurementAngle += int(self.measure.set_angle_step.text())
        self.recording.progress.setValue(self.measurementAngle / 360 * 100) # Progress bar update
        QApplication.processEvents()
        self.update()
        if self.measurementAngle < 360:
            self.audioAcquisition.initStream()
            self.audioExcitation.initStream()
            self.audioAcquisition.start()
            self.audioExcitation.start()
            self.recording.measure_info.setText('Recording {}deg_{}.wav ...'.format(self.measurementAngle, self.measure.set_name.text()))
            QApplication.processEvents()
        else:
            QMessageBox.information(self, 'Info', 'Measurement Completed!', QMessageBox.Ok, QMessageBox.Ok)
            self.audioAcquisition.clean()
            self.audioExcitation.clean()
            mainUI.pAudio.terminate()
            self.recording.apply_recording.setEnabled(False)

    def rotateTurnTable(self):
        self.arduSer.open()
        time.sleep(1)
        self.arduSer.write(10)
        if int(self.arduSer.readline()) == 1:
            self.recording.measure_info.setText('Turn Table Rotating...')
        else:
            self.recording.measure_info.setText('No signal recieved from the turn table...')
        QApplication.processEvents()
        time.sleep(4)
        if int(self.arduSer.readline()) == 2:
            self.recording.measure_info.setText('Rotation Done!')
        else:
            self.recording.measure_info.setText('No signal recieved from the turn table...')
        QApplication.processEvents()
        self.arduSer.close()

    def set_layout_excitation_signal(self):
        if self.audio_settings.get_excitation_signal.currentIndex() == 0:
            self.audio_settings.set_excitation_fmin.setEnabled(False)
            self.audio_settings.set_excitation_fmax.setEnabled(False)
        elif self.audio_settings.get_excitation_signal.currentIndex() == 1:
            self.audio_settings.set_excitation_fmin.setEnabled(True)
        else:
            self.audio_settings.set_excitation_fmin.setEnabled(True)
            self.audio_settings.set_excitation_fmax.setEnabled(True)

    def set_layout_apply_audio(self):
        self.apply_audio_settings.setEnabled(False)
        self.audio_settings.get_channels_number.setEnabled(False)
        self.audio_settings.get_input_device.setEnabled(False)
        self.audio_settings.get_output_device.setEnabled(False)
        self.audio_settings.set_recording_length.setEnabled(False)
        self.audio_settings.set_silence_size.setEnabled(False)
        self.audio_settings.get_excitation_signal.setEnabled(False)
        self.audio_settings.set_excitation_fmin.setEnabled(False)
        self.audio_settings.set_excitation_fmax.setEnabled(False)
        self.file.set_directory.setEnabled(True)
        self.file.apply_directory.setEnabled(True)

    def set_layout_apply_file(self):
        self.file.apply_directory.setEnabled(False)
        self.file.set_directory.setEnabled(False)
        self.measure.set_name.setEnabled(True)
        self.measure.set_angle_step.setEnabled(True)
        self.recording.apply_recording.setEnabled(True)
        self.measure.settings.setEnabled(True)

class PlotWindow(): # QtCore.QThread
    def __init__(self):
        super().__init__()

        self.winSize = (1200, 400)
        self.win = pg.GraphicsWindow()
        self.win.setGeometry(screenSize.width() // 2 - self.winSize[0] / 2, 60, self.winSize[0], self.winSize[1])
        self.win.setWindowTitle('Control Window')
        pg.setConfigOptions(antialias=True)
        pg.setConfigOptions(useOpenGL=True)
        self.win.show()

        self.canvas = []
        self.curves = []
        self.canvas.append(self.win.addPlot(col=0, row=0))
        self.curves.append(self.canvas[0].plot(pen=pg.mkPen(color=self.getColor(0))))

    def getColor(self, index):
        colorTheme = [(255, 153.0, 7.65),
                      (255, 89.25, 7.65),
                      (255, 0, 0),
                      (191.25, 0, 94.35),
                      (91.8, 0, 153.0)]
        return colorTheme[index % len(colorTheme)]

    def addPlotPerCannels(self):
        for index in range(1, mainUI.nbOfInputChannels):
            self.canvas.append(self.win.addPlot(col=0, row=index))
            self.curves.append(self.canvas[index].plot(pen=pg.mkPen(color=self.getColor(index))))

    def update(self, data):
        for index in range(mainUI.nbOfInputChannels):
            self.curves[index].setData(data[index])


class AudioAcquisition(QtCore.QThread):
    recordingDone = QtCore.pyqtSignal(bool)
    def __init__(self):
        super(AudioAcquisition, self).__init__()

    def initStream(self):
        self.pAudioFrames = []
        self.inputStream = mainUI.pAudio.open(format = MainUI.STREAM_DTYPE,
                        rate = MainUI.FS,
                        frames_per_buffer = MainUI.CHUNK_SIZE,
                        input = True,
                        input_device_index = mainUI.inputDeviceIndex,
                        channels = mainUI.nbOfInputChannels)

    def closeStream(self):
        self.inputStream.stop_stream()
        self.inputStream.close()

    def run(self):
        for i in range(int(MainUI.FS / MainUI.CHUNK_SIZE * mainUI.recordingLength)):
            data = self.inputStream.read(MainUI.CHUNK_SIZE)
            self.pAudioFrames.append(data)
        self.recordingDone.emit(True)

    def waveFileExport(self):
        waveFile = wave.open(os.path.join(mainUI.measurementDirPath, '{}deg_{}.wav'.format(mainUI.measurementAngle, mainUI.measure.set_name.text())), 'wb')
        waveFile.setnchannels(mainUI.nbOfInputChannels)
        waveFile.setsampwidth(mainUI.pAudio.get_sample_size(MainUI.STREAM_DTYPE))
        waveFile.setframerate(MainUI.FS)
        waveFile.writeframes(b''.join(self.pAudioFrames))
        waveFile.close()

    def clean(self):
        if self.isRunning():
            self.closeStream()


class AudioExcitation(QtCore.QThread):

    def _init_(self):
        super(AudioExcitation, self)._init_()

    @staticmethod
    def set_excitation(SIGNAL_TYPE, A, t, *F):
        if SIGNAL_TYPE == 'Sine':
            signal = np.sin(2 * np.pi * F[0]* t)
        elif SIGNAL_TYPE == 'Linear Sweep':
            alpha = (F[1] - F[0])/t[-1]
            signal = np.cos(np.pi * alpha * t**2 + 2 * np.pi * F[0] * t)
        elif SIGNAL_TYPE == 'Exponential Sweep':
            beta = (np.log(F[1]) - np.log(F[0])) / t[-1]
            signal = np.cos(2 * np.pi * (F[0] * np.exp(beta * t) - F[0]) / beta)
        return  A*signal

    def get_excitation(self, SIGNAL_TYPE, SILENCE_SIZE):
        self.AMP = np.iinfo(MainUI.DTYPE).max * 0.5
        self.F_MIN = float(mainUI.audio_settings.set_excitation_fmin.text())
        self.F_MAX = float(mainUI.audio_settings.set_excitation_fmax.text())

        EXCITATION_SIZE = int((mainUI.recordingLength - 2*SILENCE_SIZE) * MainUI.FS)
        SILENCE_SIZE = int(SILENCE_SIZE * MainUI.FS)

        t = np.arange(EXCITATION_SIZE) / MainUI.FS
        self.excitationSignal = np.zeros(int(mainUI.recordingLength * MainUI.FS))

        n_min, n_max = SILENCE_SIZE,  SILENCE_SIZE + EXCITATION_SIZE
        excitation_temp = AudioExcitation.set_excitation(SIGNAL_TYPE, self.AMP, t, self.F_MIN, self.F_MAX)

        self.excitationSignal[n_min:n_max] = excitation_temp
        self.excitationSignal = np.repeat(self.excitationSignal, mainUI.nbOfOutputChannels, axis=0)
        self.excitationSignal = self.excitationSignal.astype(MainUI.DTYPE).tostring()

    def initStream(self):
        self.outputStream = mainUI.pAudio.open(format = MainUI.STREAM_DTYPE,
                        rate = MainUI.FS,
                        frames_per_buffer = MainUI.CHUNK_SIZE,
                        input = False,
                        output = True,
                        output_device_index = mainUI.outputDeviceIndex,
                        channels = mainUI.nbOfOutputChannels)

    def closeStream(self):
        self.outputStream.stop_stream()
        self.outputStream.close()

    def run(self):
        for i in range(int(MainUI.FS / MainUI.CHUNK_SIZE * mainUI.recordingLength)):
            self.outputStream.write(self.excitationSignal[MainUI.CHUNK_SIZE*2*mainUI.nbOfOutputChannels*i:MainUI.CHUNK_SIZE*2*mainUI.nbOfOutputChannels*(i+1)])

    def clean(self):
        if self.isRunning():
            self.closeStream()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    screenSize = app.primaryScreen().size()
    mainUI = MainUI()
    sys.exit(app.exec_())

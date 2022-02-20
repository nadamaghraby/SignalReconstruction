# libraries needed for main python file
# the file we run for the app to work
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication
import sys
import numpy as np
import os
from gui import Ui_MainWindow
import pathlib
import pyqtgraph as pg
import pandas as pd
import pyqtgraph as pg
from pyqtgraph import *
from UliEngineering.SignalProcessing.Simulation import sine_wave
from scipy.interpolate import make_interp_spline

# class definition for application window components like the ui

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.showButton.clicked.connect(self.showOrHide)
        self.ui.okButton.clicked.connect(self.constructSinusoidal)
        self.ui.addButton.clicked.connect(self.addSinusoidal)
        self.ui.deleteButton.clicked.connect(self.deleteSinusoidal)
        self.ui.addToMainGraphButton.clicked.connect(self.addSyntheticSignalToMainGraph)
        self.ui.SaveButton.clicked.connect(self.saveSyntheticSignal)
        self.ui.openButton.clicked.connect(self.open)
        self.ui.freqSlider.setMinimum(1)
        self.ui.freqSlider.valueChanged.connect(self.sliderValueChanged)
        self.ui.secondaryGraph.setVisible(False)

        self.signalMaxFrequency = 0
        self.signalSamplingFrequency = 0
        self.signalDuration = []
        self.signalAmplitude = []
        self.sinTime = np.linspace(0, 2, 1000)  
        self.syntheticSignal = [0]*self.sinTime
        self.signalSamples = 0
        self.sinFrequency = 0
        self.sinMagnitude = 0
        self.sinPhaseShift = 0
        self.sinusoidal = 0
        self.sinName = ""
        self.sampleTime = []
        self.sampleAmplitude = []
        self.sinusoidals = []
        self.sinNames = []
        self.showOrHide = False


    def plotResampledSignal(self):
        self.reconstructedTime = np.linspace(min(self.sampleTime), max(self.sampleTime), 1000)
        spl = make_interp_spline(self.sampleTime, self.sampleAmplitude, 3)
        self.reconstructedValue = spl(self.reconstructedTime)
        self.ui.secondaryGraph.clear()
        self.ui.secondaryGraph.plot(self.reconstructedTime, self.reconstructedValue, pen=pg.mkPen(color=(0, 255, 0)))


    def plotOriginalSignal(self):
        self.signalMaxFrequency = self.getmaxFrequency(self.signalDuration, self.signalAmplitude)
        print("Max Frequency = {}".format(self.signalMaxFrequency))
        self.ui.freqSlider.setMaximum(3*self.signalMaxFrequency)
        self.signalSamplingFrequency = self.ui.freqSlider.value()
        print("Sampling Frequency = {}".format(self.signalSamplingFrequency))
        signalDuration = self.signalDuration[-1] - self.signalDuration[0]
        signalLength = len(self.signalDuration)
        samplingIndexPeriod = max(np.floor(signalLength / (signalDuration * self.signalSamplingFrequency)).astype(int),1)
        sampledDataIndex = np.arange(0, signalLength+1, samplingIndexPeriod, dtype=int)
        sampledDataIndex[len(sampledDataIndex)-1] -= 1
        self.sampleTime = np.array(self.signalDuration)[sampledDataIndex]
        self.sampleAmplitude = np.array(self.signalAmplitude)[sampledDataIndex]
        self.ui.mainGraph.clear()
        self.ui.mainGraph.plot(self.signalDuration,self.signalAmplitude, pen=pg.mkPen(color=(255, 0, 0)))
        self.ui.mainGraph.plot(self.sampleTime,self.sampleAmplitude, pen=None, symbol='o')



    def hideSecondaryGraph(self):
        self.ui.secondaryGraph.setVisible(False)
        self.plotOriginalSignal()

    def sliderValueChanged(self):
        self.plotGraph()


    def plotGraph(self):
        if self.showOrHide:
            self.ui.secondaryGraph.setVisible(True)
            self.plotOriginalSignal()
            self.plotResampledSignal()
        else:
            self.hideSecondaryGraph()

    def showOrHide(self):
        self.showOrHide = not(self.showOrHide)
        self.plotGraph()
        

    def getmaxFrequency(self,duration,amplitude):
        self.y_fft = np.fft.fft(amplitude)             
        # First half ( pos freqs )
        self.y_fft = self.y_fft[:round(len(duration)/2)]
        # Absolute value of magnitudes
        self.y_fft = np.abs(self.y_fft)
        peak = 0
        fs = 1000
        t = np.arange(0, 1, 1 /fs)
        n = np.size(t)
        fr = (fs / 2) * np.linspace(0, 2, n) # frequencies of x axis
        for value in self.y_fft:
            if (value > 1):
                peak = value

        w = np.where(self.y_fft == peak)
        maxFrequency = int(np.floor(max(fr[w])))
        return maxFrequency




    def open(self):
        files_name = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Open only CSV', os.getenv('HOME'), "csv(*.csv)")
        path = files_name[0]

        if pathlib.Path(path).suffix == ".csv":
            data = pd.read_csv(path)
            self.signalDuration = list(data.values[:, 0])
            self.signalAmplitude = list(data.values[:, 1])
            self.plotGraph()

    def constructSinusoidal(self):
        self.sinFrequency = float(self.ui.EditFrequency.text())
        self.sinMagnitude = float(self.ui.EditMagnitude.text())
        self.sinPhaseShift = float(self.ui.EditPhaseShift.text())
        self.sinusoidal = sine_wave(frequency=self.sinFrequency, samplerate=len(
            self.sinTime), amplitude=self.sinMagnitude, phaseshift=self.sinPhaseShift)
        print("frequency = {} , Magnitude = {} , Phase shift = {} , time = {}"
              .format(self.sinFrequency, self.sinMagnitude, self.sinPhaseShift, len(self.sinTime)))
        self.ui.sinGraph.clear()
        self.ui.sinGraph.plot(self.sinTime, self.sinusoidal,pen=pg.mkPen(color=(255, 0, 0)))

    def drawSyntheticSignal(self):
        self.syntheticSignal = [0]*self.sinTime
        for sinusoidal in self.sinusoidals:
            self.syntheticSignal += sinusoidal
        
        self.ui.synSignalGraph.clear()
        self.ui.synSignalGraph.plot(self.sinTime, self.syntheticSignal, pen=pg.mkPen(color=(255, 0, 0)))

    def addSinusoidal(self):
        self.sinusoidals.append(self.sinusoidal)
        self.sinName = "sin_freq {} _mag {} _phaseshift {}".format(
            self.sinFrequency, self.sinMagnitude, self.sinPhaseShift)
        self.sinNames.append(self.sinName)
        self.ui.comboBoxChooseSignal.addItem(self.sinName)
        self.drawSyntheticSignal()

    def deleteSinusoidal(self):
        self.sinusoidals.pop(self.ui.comboBoxChooseSignal.currentIndex())
        self.sinNames.pop(self.ui.comboBoxChooseSignal.currentIndex())
        # reconstruct combobox
        self.ui.comboBoxChooseSignal.clear()
        self.ui.comboBoxChooseSignal.addItems(self.sinNames)
        self.drawSyntheticSignal()

    def saveSyntheticSignal(self):
        syntheticSignaldf = pd.DataFrame(list(zip(self.sinTime, self.syntheticSignal)))
        syntheticSignaldf.to_csv('SyntheticSignal.csv', index=False)

    def addSyntheticSignalToMainGraph(self):
        self.signalAmplitude = self.syntheticSignal
        self.signalDuration = self.sinTime
        self.plotGraph()

# function for launching a QApplication and running the ui and main window


def window():
    app = QApplication(sys.argv)
    win = ApplicationWindow()
    win.show()
    sys.exit(app.exec_())


# main code
if __name__ == "__main__":
    window()


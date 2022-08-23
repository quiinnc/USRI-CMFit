from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
import os
from numpy import exp
from numpy import loadtxt
from lmfit import Model, minimize, Parameters, report_fit, Minimizer, conf_interval
from lmfit.printfuncs import report_ci
from lmfit.models import LorentzianModel, LinearModel, GaussianModel, VoigtModel
from PyQt5 import QtCore, QtWidgets
from PyQt6.QtWidgets import QDialog
import sys
import pyqtgraph as pg
from heapq import nsmallest
import math

def closest(lst, K):
    """ Finds the value in lst closest to K """
    return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-K))]

## CREATE UI WINDOW ##
class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
    

        MainWindow.setObjectName("MainWindow")
        ## WINDOW SIZING ##
        MainWindow.resize(1100, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        ## STATIC FIGURE WINDOW SPACE ##
        self.graphWidget = pg.PlotWidget(self.centralwidget)
        self.graphWidget.setGeometry(QtCore.QRect(350, 75, 650, 400))
        self.graphWidget.setBackground('w')
        self.graphWidget.showGrid(x=True, y=True)

        ## OPEN FILE BUTTON ##
        self.openfile = QtWidgets.QPushButton(self.centralwidget)
        self.openfile.setGeometry(QtCore.QRect(50, 35, 70, 30))
        self.openfile.setObjectName("file")
        self.openfile.setStyleSheet(
            "background-color:rgb(111,180,219)"
            "QPushButton{background-color:rgb(211,211,211)}"  
            "QPushButton:hover{color:blue}"  
            "QPushButton{border-radius:10px}"  
            "QPushButton:pressed{background-color:rgb(100,100,100);border: None;}"  
        )
        ## OPEN FILE ##
        self.openfiletxt = QtWidgets.QLabel(self.centralwidget)
        self.openfiletxt.setGeometry(QtCore.QRect(300, 100, 50, 35))
        self.openfiletxt.setObjectName("Open File")
        self.openfiletxt.setStyleSheet("background-color:rgb(240, 240, 240)")

        ## TRIM DATA BUTTON ##
        self.trimData = QtWidgets.QPushButton(self.centralwidget)
        self.trimData.setGeometry(QtCore.QRect(540, 20, 40, 30))
        self.trimData.setObjectName("Trim Data")
        self.trimData.setStyleSheet(
            "background-color:rgb(111,180,219)"
            "QPushButton{background-color:rgb(211,211,211)}"  
            "QPushButton:hover{color:blue}"  
            "QPushButton{border-radius:10px}"  
            "QPushButton:pressed{background-color:rgb(100,100,100);border: None;}" 
        )
        ## TRIM DATA TXT ##
        self.trimDatatxt = QtWidgets.QLabel(self.centralwidget)
        self.trimDatatxt.setGeometry(QtCore.QRect(240, 100, 50, 35))
        self.trimDatatxt.setObjectName("Trim Data")
        self.trimDatatxt.setStyleSheet("background-color:rgb(240, 240, 240)")
        ## X LOW INPUT ##
        self.xlowinput = QtWidgets.QLineEdit(self.centralwidget)
        self.xlowinput.setGeometry(QtCore.QRect(350, 10, 60, 25))
        self.xlowinput.setObjectName("X Low Input")
        ## X High Input ##
        self.xhighinput = QtWidgets.QLineEdit(self.centralwidget)
        self.xhighinput.setGeometry(QtCore.QRect(456, 10, 60, 25))
        self.xhighinput.setObjectName("X High Input")
        ## X Label for Trimming ##
        self.xtrimlabel = QtWidgets.QLabel(self.centralwidget)
        self.xtrimlabel.setGeometry(QtCore.QRect(430, 0, 20, 45))
        self.xtrimlabel.setObjectName("x")
        ## UNDO TRIM BUTTON ##
        self.undotrim = QtWidgets.QPushButton(self.centralwidget)
        self.undotrim.setGeometry(QtCore.QRect(590, 20, 40, 30))
        self.undotrim.setObjectName("Undo Trim")
        self.undotrim.setStyleSheet(
            "background-color:rgb(111,180,219)"
            "QPushButton{background-color:rgb(211,211,211)}"  
            "QPushButton:hover{color:blue}"  
            "QPushButton{border-radius:10px}"  
            "QPushButton:pressed{background-color:rgb(100,100,100);border: None;}" 
        )
        ## UNDO TRIM TXT ##
        self.undotrimtxt = QtWidgets.QLabel(self.centralwidget)
        self.undotrimtxt.setGeometry(QtCore.QRect(300, 100, 50, 35))
        self.undotrimtxt.setObjectName("Undo Trim")
        self.undotrimtxt.setStyleSheet("background-color:rgb(240, 240, 240)")

        ## BASE LINE SUBTRACTION LABEL ##
        self.basetxt = QtWidgets.QLabel(self.centralwidget)
        self.basetxt.setGeometry(QtCore.QRect(20, 70, 200, 45))
        self.basetxt.setObjectName("Base Line Subtraction")

        ## BASE POLYNOMIAL DEGREE INPUT ##
        self.polyDeg = QtWidgets.QLineEdit(self.centralwidget)
        self.polyDeg.setGeometry(QtCore.QRect(80, 120, 30, 25))
        self.polyDeg.setObjectName("Polynomial Degree Input")
        ## BASE POLYNOMIAL DEGREE LABEL ##
        self.polyDegLabel = QtWidgets.QLabel(self.centralwidget)
        self.polyDegLabel.setGeometry(QtCore.QRect(25, 109, 50, 45))
        self.polyDegLabel.setObjectName("Polynomial Degree Label")

        ## CURVE CLICK BUTTON ##
        self.curveClicker = QtWidgets.QPushButton(self.centralwidget)
        self.curveClicker.setGeometry(QtCore.QRect(140, 119, 80, 30))
        self.curveClicker.setObjectName("Curve Click")
        self.curveClicker.setStyleSheet(
            "background-color:rgb(111,180,219)"
            "QPushButton{background-color:rgb(211,211,211)}"  
            "QPushButton:hover{color:blue}"  
            "QPushButton{border-radius:10px}"  
            "QPushButton:pressed{background-color:rgb(100,100,100);border: None;}" 
        )
        ## UNDO CURVE CLICK BUTTON ##
        self.curveUndo = QtWidgets.QPushButton(self.centralwidget)
        self.curveUndo.setGeometry(QtCore.QRect(20, 170, 50, 30))
        self.curveUndo.setObjectName("Undo Curve Click")
        self.curveUndo.setStyleSheet(
            "background-color:rgb(111,180,219)"
            "QPushButton{background-color:rgb(211,211,211)}"  
            "QPushButton:hover{color:blue}"  
            "QPushButton{border-radius:10px}"  
            "QPushButton:pressed{background-color:rgb(100,100,100);border: None;}" 
        )
        ## ACCEPT CURVE CLICK BUTTON ##
        self.curveAccept = QtWidgets.QPushButton(self.centralwidget)
        self.curveAccept.setGeometry(QtCore.QRect(75, 170, 65, 30))
        self.curveAccept.setObjectName("Accept Curve Click")
        self.curveAccept.setStyleSheet(
            "background-color:rgb(111,180,219)"
            "QPushButton{background-color:rgb(211,211,211)}"  
            "QPushButton:hover{color:blue}"  
            "QPushButton{border-radius:10px}"  
            "QPushButton:pressed{background-color:rgb(100,100,100);border: None;}" 
        )
        ## SUBTRACT CURVE CLICK BUTTON ##
        self.curveSubtract = QtWidgets.QPushButton(self.centralwidget)
        self.curveSubtract.setGeometry(QtCore.QRect(145, 170, 60, 30))
        self.curveSubtract.setObjectName("Subtract Curve Click")
        self.curveSubtract.setStyleSheet(
            "background-color:rgb(111,180,219)"
            "QPushButton{background-color:rgb(211,211,211)}"  
            "QPushButton:hover{color:blue}"  
            "QPushButton{border-radius:10px}"  
            "QPushButton:pressed{background-color:rgb(100,100,100);border: None;}" 
        )

        ## STEP COUNTER LABEL ##
        self.stepLabel = QtWidgets.QLabel(self.centralwidget)
        self.stepLabel.setGeometry(QtCore.QRect(10, 225, 480, 45))
        self.stepLabel.setObjectName("Step")

        ## STEP BUTTONS ##
        self.step100 = QtWidgets.QPushButton(self.centralwidget)
        self.step100.setGeometry(QtCore.QRect(40, 235, 40, 30))
        self.step100.setObjectName("100")
        self.step100.setStyleSheet(
            "background-color:rgb(111,180,219)"
            "QPushButton{background-color:rgb(211,211,211)}"  
            "QPushButton:hover{color:blue}"  
            "QPushButton{border-radius:10px}"  
            "QPushButton:pressed{background-color:rgb(100,100,100);border: None;}" 
        )
        self.step50 = QtWidgets.QPushButton(self.centralwidget)
        self.step50.setGeometry(QtCore.QRect(92, 235, 30, 30))
        self.step50.setObjectName("50")
        self.step50.setStyleSheet(
            "background-color:rgb(111,180,219)"
            "QPushButton{background-color:rgb(211,211,211)}"  
            "QPushButton:hover{color:blue}"  
            "QPushButton{border-radius:10px}"  
            "QPushButton:pressed{background-color:rgb(100,100,100);border: None;}" 
        )
        self.step25 = QtWidgets.QPushButton(self.centralwidget)
        self.step25.setGeometry(QtCore.QRect(133, 235, 30, 30))
        self.step25.setObjectName("25")
        self.step25.setStyleSheet(
            "background-color:rgb(111,180,219)"
            "QPushButton{background-color:rgb(211,211,211)}"  
            "QPushButton:hover{color:blue}"  
            "QPushButton{border-radius:10px}"  
            "QPushButton:pressed{background-color:rgb(100,100,100);border: None;}" 
        )
        self.step10 = QtWidgets.QPushButton(self.centralwidget)
        self.step10.setGeometry(QtCore.QRect(175, 235, 30, 30))
        self.step10.setObjectName("10")
        self.step10.setStyleSheet(
            "background-color:rgb(111,180,219)"
            "QPushButton{background-color:rgb(211,211,211)}"  
            "QPushButton:hover{color:blue}"  
            "QPushButton{border-radius:10px}"  
            "QPushButton:pressed{background-color:rgb(100,100,100);border: None;}" 
        )
        self.step1 = QtWidgets.QPushButton(self.centralwidget)
        self.step1.setGeometry(QtCore.QRect(216, 235, 30, 30))
        self.step1.setObjectName("1")
        self.step1.setStyleSheet(
            "background-color:rgb(111,180,219)"
            "QPushButton{background-color:rgb(211,211,211)}"  
            "QPushButton:hover{color:blue}"  
            "QPushButton{border-radius:10px}"  
            "QPushButton:pressed{background-color:rgb(100,100,100);border: None;}" 
        )
        self.step01 = QtWidgets.QPushButton(self.centralwidget)
        self.step01.setGeometry(QtCore.QRect(258, 235, 30, 30))
        self.step01.setObjectName("0.1")
        self.step01.setStyleSheet(
            "background-color:rgb(111,180,219)"
            "QPushButton{background-color:rgb(211,211,211)}"  
            "QPushButton:hover{color:blue}"  
            "QPushButton{border-radius:10px}"  
            "QPushButton:pressed{background-color:rgb(100,100,100);border: None;}" 
        )
        self.step001 = QtWidgets.QPushButton(self.centralwidget)
        self.step001.setGeometry(QtCore.QRect(300, 235, 40, 30))
        self.step001.setObjectName("0.01")
        self.step001.setStyleSheet(
            "background-color:rgb(111,180,219)"
            "QPushButton{background-color:rgb(211,211,211)}"  
            "QPushButton:hover{color:blue}"  
            "QPushButton{border-radius:10px}"  
            "QPushButton:pressed{background-color:rgb(100,100,100);border: None;}" 
        )
        ## MANUAL FIT BUTTON ##
        self.manualFit = QtWidgets.QPushButton(self.centralwidget)
        self.manualFit.setGeometry(QtCore.QRect(800, 20, 100, 30))
        self.manualFit.setObjectName("Manual Fit")
        self.manualFit.setStyleSheet(
            "background-color:rgb(111,180,219)"
            "QPushButton{background-color:rgb(211,211,211)}"  
            "QPushButton:hover{color:blue}"  
            "QPushButton{border-radius:10px}"  
            "QPushButton:pressed{background-color:rgb(100,100,100);border: None;}" 
        )
        ## UNDO MANUAL FIT BUTTON ##
        self.manualUndo = QtWidgets.QPushButton(self.centralwidget)
        self.manualUndo.setGeometry(QtCore.QRect(920, 20, 50, 30))
        self.manualUndo.setObjectName("Manual Undo")
        self.manualUndo.setStyleSheet(
            "background-color:rgb(111,180,219)"
            "QPushButton{background-color:rgb(211,211,211)}"  
            "QPushButton:hover{color:blue}"  
            "QPushButton{border-radius:10px}"  
            "QPushButton:pressed{background-color:rgb(100,100,100);border: None;}" 
        )
        ## ACCEPT MANUAL FIT BUTTON ##
        self.manualAccept = QtWidgets.QPushButton(self.centralwidget)
        self.manualAccept.setGeometry(QtCore.QRect(990, 20, 65, 30))
        self.manualAccept.setObjectName("Manual Accept")
        self.manualAccept.setStyleSheet(
            "background-color:rgb(111,180,219)"
            "QPushButton{background-color:rgb(211,211,211)}"  
            "QPushButton:hover{color:blue}"  
            "QPushButton{border-radius:10px}"  
            "QPushButton:pressed{background-color:rgb(100,100,100);border: None;}" 
        )
        ## MANUAL FIT FUNCTION TYPE ##
        self.manualType = QtWidgets.QComboBox(self.centralwidget)
        self.manualType.setGeometry(QtCore.QRect(680, 40, 100, 30))
        self.manualType.addItems(['Lorentzian','Gaussian','Voigt'])

        ## PEAK NUM INPUT ##
        self.peakNumInput = QtWidgets.QLineEdit(self.centralwidget)
        self.peakNumInput.setGeometry(QtCore.QRect(750, 10, 30, 25))
        self.peakNumInput.setObjectName("Peak Num Input")
        ## PEAK NUM LABEL ##
        self.peakNumLabel = QtWidgets.QLabel(self.centralwidget)
        self.peakNumLabel.setGeometry(QtCore.QRect(675, 12, 80, 20))
        self.peakNumLabel.setObjectName("Peak Num")

        ## SAVE FILE BUTTON ##
        self.saveFileButton = QtWidgets.QPushButton(self.centralwidget)
        self.saveFileButton.setGeometry(QtCore.QRect(1025, 400, 50, 30))
        self.saveFileButton.setObjectName("Save File Button")
        self.saveFileButton.setStyleSheet(
            "background-color:rgb(111,180,219)"
            "QPushButton{background-color:rgb(211,211,211)}"  
            "QPushButton:hover{color:blue}"  
            "QPushButton{border-radius:10px}"  
            "QPushButton:pressed{background-color:rgb(100,100,100);border: None;}" 
        )

        ## MAIN FIT FUNCTION TYPE ##
        self.fitType = QtWidgets.QComboBox(self.centralwidget)
        self.fitType.setGeometry(QtCore.QRect(10, 410, 100, 30))
        self.fitType.addItems(['Lorentzian','Gaussian','Voigt'])

        ## HEIGHT LABEL ##
        self.height_label = QtWidgets.QLabel(self.centralwidget)
        self.height_label.setGeometry(QtCore.QRect(10, 299, 50, 45))
        self.height_label.setObjectName("Height Label")
        ## D1 LABEL ##
        self.D1_label = QtWidgets.QLabel(self.centralwidget)
        self.D1_label.setGeometry(QtCore.QRect(130, 270, 20, 45))
        self.D1_label.setObjectName("D1 Label")
        ## D2 LABEL ##
        self.D2_label = QtWidgets.QLabel(self.centralwidget)
        self.D2_label.setGeometry(QtCore.QRect(305, 270, 20, 45))
        self.D2_label.setObjectName("D2 Label")
        ## D3 LABEL ##
        self.D3_label = QtWidgets.QLabel(self.centralwidget)
        self.D3_label.setGeometry(QtCore.QRect(190, 270, 20, 45))
        self.D3_label.setObjectName("D3 Label")
        ## D4 LABEL ##
        self.D4_label = QtWidgets.QLabel(self.centralwidget)
        self.D4_label.setGeometry(QtCore.QRect(70, 270, 20, 45))
        self.D4_label.setObjectName("D4 Label")
        ## G LABEL ##
        self.G_label = QtWidgets.QLabel(self.centralwidget)
        self.G_label.setGeometry(QtCore.QRect(250, 270, 20, 45))
        self.G_label.setObjectName("G Label")
        ## HEIGHT VALUE INPUTS ##
        self.D4_height = QtWidgets.QSpinBox(self.centralwidget)
        self.D4_height.setRange(-999999999, 999999999)
        self.D4_height.setGeometry(QtCore.QRect(55, 310, 55, 25))
        self.D4_height.setObjectName("D4 Height Input")
        self.D1_height = QtWidgets.QSpinBox(self.centralwidget)
        self.D1_height.setRange(-999999999, 999999999)
        self.D1_height.setGeometry(QtCore.QRect(114, 310, 55, 25))
        self.D1_height.setObjectName("D1 Height Input")
        self.D3_height = QtWidgets.QSpinBox(self.centralwidget)
        self.D3_height.setRange(-999999999, 999999999)
        self.D3_height.setGeometry(QtCore.QRect(173, 310, 55, 25))
        self.D3_height.setObjectName("D3 Height Input")
        self.G_height = QtWidgets.QSpinBox(self.centralwidget)
        self.G_height.setRange(-999999999, 999999999)
        self.G_height.setGeometry(QtCore.QRect(232, 310, 55, 25))
        self.G_height.setObjectName("G Height Input")
        self.D2_height = QtWidgets.QSpinBox(self.centralwidget)
        self.D2_height.setRange(-999999999, 999999999)
        self.D2_height.setGeometry(QtCore.QRect(290, 310, 55, 25))
        self.D2_height.setObjectName("G Height Input")

        ## CENTER LABEL ##
        self.center_label = QtWidgets.QLabel(self.centralwidget)
        self.center_label.setGeometry(QtCore.QRect(10, 329, 50, 45))
        self.center_label.setObjectName("Center Label") 
        ## CENTER INPUTS ##
        self.D4_center = QtWidgets.QSpinBox(self.centralwidget)
        self.D4_center.setRange(-999999999, 999999999)
        self.D4_center.setGeometry(QtCore.QRect(55, 340, 55, 25))
        self.D4_center.setObjectName("D4 Center Input")
        self.D1_center = QtWidgets.QSpinBox(self.centralwidget)
        self.D1_center.setRange(-999999999, 999999999)
        self.D1_center.setGeometry(QtCore.QRect(114, 340, 55, 25))
        self.D1_center.setObjectName("D1 Center Input")
        self.D3_center = QtWidgets.QSpinBox(self.centralwidget)
        self.D3_center.setRange(-999999999, 999999999)
        self.D3_center.setGeometry(QtCore.QRect(173, 340, 55, 25))
        self.D3_center.setObjectName("D3 Center Input")
        self.G_center = QtWidgets.QSpinBox(self.centralwidget)
        self.G_center.setRange(-999999999, 999999999)
        self.G_center.setGeometry(QtCore.QRect(232, 340, 55, 25))
        self.G_center.setObjectName("G Center Input")
        self.D2_center = QtWidgets.QSpinBox(self.centralwidget)
        self.D2_center.setRange(-999999999, 999999999)
        self.D2_center.setGeometry(QtCore.QRect(290, 340, 55, 25))
        self.D2_center.setObjectName("D2 Center Input")

        ## SIGMA LABEL ##
        self.sigma_label = QtWidgets.QLabel(self.centralwidget)
        self.sigma_label.setGeometry(QtCore.QRect(10, 359, 50, 45))
        self.sigma_label.setObjectName("HWHM Label")
        ## SIGMA INPUTS ##
        self.D4_sigma = QtWidgets.QSpinBox(self.centralwidget)
        self.D4_sigma.setRange(-999999999, 999999999)
        self.D4_sigma.setGeometry(QtCore.QRect(55, 370, 55, 25))
        self.D4_sigma.setObjectName("D4 HWHM Input")
        self.D1_sigma = QtWidgets.QSpinBox(self.centralwidget)
        self.D1_sigma.setRange(-999999999, 999999999)
        self.D1_sigma.setGeometry(QtCore.QRect(114, 370, 55, 25))
        self.D1_sigma.setObjectName("D1 HWHM Input")
        self.D3_sigma = QtWidgets.QSpinBox(self.centralwidget)
        self.D3_sigma.setRange(-999999999, 999999999)
        self.D3_sigma.setGeometry(QtCore.QRect(173, 370, 55, 25))
        self.D3_sigma.setObjectName("D3 HWHM Input")
        self.G_sigma = QtWidgets.QSpinBox(self.centralwidget)
        self.G_sigma.setRange(-999999999, 999999999)
        self.G_sigma.setGeometry(QtCore.QRect(232, 370, 55, 25))
        self.G_sigma.setObjectName("G HWHM Input")
        self.D2_sigma = QtWidgets.QSpinBox(self.centralwidget)
        self.D2_sigma.setRange(-999999999, 999999999)
        self.D2_sigma.setGeometry(QtCore.QRect(290, 370, 55, 25))
        self.D2_sigma.setObjectName("D2 HWHM Input")

        ## MAIN FIT GUESS BUTTON ##
        self.fitGuess = QtWidgets.QPushButton(self.centralwidget)
        self.fitGuess.setGeometry(QtCore.QRect(125, 410, 50, 30))
        self.fitGuess.setObjectName("Fit Guess Button")
        self.fitGuess.setStyleSheet(
            "background-color:rgb(111,180,219)"
            "QPushButton{background-color:rgb(211,211,211)}"  
            "QPushButton:hover{color:blue}"  
            "QPushButton{border-radius:10px}"  
            "QPushButton:pressed{background-color:rgb(100,100,100);border: None;}" 
        )
        ## MAIN FIT CRUDE PLOT BUTTON ##
        self.fitCrude = QtWidgets.QPushButton(self.centralwidget)
        self.fitCrude.setGeometry(QtCore.QRect(183, 410, 50, 30))
        self.fitCrude.setObjectName("Crude Plot Button")
        self.fitCrude.setStyleSheet(
            "background-color:rgb(111,180,219)"
            "QPushButton{background-color:rgb(211,211,211)}"  
            "QPushButton:hover{color:blue}"  
            "QPushButton{border-radius:10px}"  
            "QPushButton:pressed{background-color:rgb(100,100,100);border: None;}" 
        )
        ## MAIN FIT INITIAL PLOT BUTTON ##
        self.fitInitial = QtWidgets.QPushButton(self.centralwidget)
        self.fitInitial.setGeometry(QtCore.QRect(240, 410, 60, 30))
        self.fitInitial.setObjectName("Initial Plot Button")
        self.fitInitial.setStyleSheet(
            "background-color:rgb(111,180,219)"
            "QPushButton{background-color:rgb(211,211,211)}"  
            "QPushButton:hover{color:blue}"  
            "QPushButton{border-radius:10px}"  
            "QPushButton:pressed{background-color:rgb(100,100,100);border: None;}" 
        )
        ## MAIN FIT BUTTON ##
        self.fitPlot = QtWidgets.QPushButton(self.centralwidget)
        self.fitPlot.setGeometry(QtCore.QRect(310, 410, 35, 30))
        self.fitPlot.setObjectName("Fit Plot Button")
        self.fitPlot.setStyleSheet(
            "background-color:rgb(111,180,219)"
            "QPushButton{background-color:rgb(211,211,211)}"  
            "QPushButton:hover{color:blue}"  
            "QPushButton{border-radius:10px}"  
            "QPushButton:pressed{background-color:rgb(100,100,100);border: None;}" 
        )
        ## MAIN EXTERNAL PLOT / IMAGE BUTTON ##
        self.fitImage = QtWidgets.QPushButton(self.centralwidget)
        self.fitImage.setGeometry(QtCore.QRect(300, 450, 45, 30))
        self.fitImage.setObjectName("Fit Image Button")
        self.fitImage.setStyleSheet(
            "background-color:rgb(111,180,219)"
            "QPushButton{background-color:rgb(211,211,211)}"  
            "QPushButton:hover{color:blue}"  
            "QPushButton{border-radius:10px}"  
            "QPushButton:pressed{background-color:rgb(100,100,100);border: None;}" 
        )
        ## AUTO FIT BUTTON ##
        self.autoFitButton = QtWidgets.QPushButton(self.centralwidget)
        self.autoFitButton.setGeometry(QtCore.QRect(160, 450, 60, 30))
        self.autoFitButton.setObjectName("Auto Fit Button")
        self.autoFitButton.setStyleSheet(
            "background-color:rgb(111,180,219)"
            "QPushButton{background-color:rgb(211,211,211)}"  
            "QPushButton:hover{color:blue}"  
            "QPushButton{border-radius:10px}"  
            "QPushButton:pressed{background-color:rgb(100,100,100);border: None;}" 
        )

        ## MAXIMA AND MINIMA / FIT LIMITS ##
        self.maximaLabel = QtWidgets.QLabel(self.centralwidget)
        self.maximaLabel.setGeometry(QtCore.QRect(10, 490, 60, 20))
        self.minimaLabel = QtWidgets.QLabel(self.centralwidget)
        self.minimaLabel.setGeometry(QtCore.QRect(10, 550, 60, 20))
        ## D4 LABELS ##
        self.D4_height_label = QtWidgets.QLabel(self.centralwidget)
        self.D4_height_label.setGeometry(QtCore.QRect(78, 520, 60, 20))
        self.D4_center_label = QtWidgets.QLabel(self.centralwidget)
        self.D4_center_label.setGeometry(QtCore.QRect(141, 520, 60, 20))
        self.D4_sigma_label = QtWidgets.QLabel(self.centralwidget)
        self.D4_sigma_label.setGeometry(QtCore.QRect(204, 520, 60, 20))
        ## D4 LIMS ##
        self.D4_height_lim = QtWidgets.QSpinBox(self.centralwidget)
        self.D4_height_lim.setRange(-999999999, 999999999)
        self.D4_height_lim.setGeometry(QtCore.QRect(78, 490, 55, 25))
        self.D4_height_lim.setObjectName("D4 Height Limit")
        self.D4_height_lim_low = QtWidgets.QSpinBox(self.centralwidget)
        self.D4_height_lim_low.setRange(-999999999, 999999999)
        self.D4_height_lim_low.setGeometry(QtCore.QRect(78, 550, 55, 25))
        self.D4_height_lim_low.setObjectName("D4 Height Low Limit")
        self.D4_center_lim = QtWidgets.QSpinBox(self.centralwidget)
        self.D4_center_lim.setRange(-999999999, 999999999)
        self.D4_center_lim.setGeometry(QtCore.QRect(141, 490, 55, 25))
        self.D4_center_lim.setObjectName("D4 Center Limit")
        self.D4_center_lim_low = QtWidgets.QSpinBox(self.centralwidget)
        self.D4_center_lim_low.setRange(-999999999, 999999999)
        self.D4_center_lim_low.setGeometry(QtCore.QRect(141, 550, 55, 25))
        self.D4_center_lim_low.setObjectName("D4 Center Low Limit")
        self.D4_sigma_lim = QtWidgets.QSpinBox(self.centralwidget)
        self.D4_sigma_lim.setRange(-999999999, 999999999)
        self.D4_sigma_lim.setGeometry(QtCore.QRect(204, 490, 55, 25))
        self.D4_sigma_lim.setObjectName("D4 Sigma Limit")
        self.D4_sigma_lim_low = QtWidgets.QSpinBox(self.centralwidget)
        self.D4_sigma_lim_low.setRange(-999999999, 999999999)
        self.D4_sigma_lim_low.setGeometry(QtCore.QRect(204, 550, 55, 25))
        self.D4_sigma_lim_low.setObjectName("D4 Sigma Limit")
        ## D1 LABELS ##
        self.D1_height_label = QtWidgets.QLabel(self.centralwidget)
        self.D1_height_label.setGeometry(QtCore.QRect(287, 520, 60, 20))
        self.D1_center_label = QtWidgets.QLabel(self.centralwidget)
        self.D1_center_label.setGeometry(QtCore.QRect(350, 520, 60, 20))
        self.D1_sigma_label = QtWidgets.QLabel(self.centralwidget)
        self.D1_sigma_label.setGeometry(QtCore.QRect(413, 520, 60, 20))
        ## D1 LIMS ##
        self.D1_height_lim = QtWidgets.QSpinBox(self.centralwidget)
        self.D1_height_lim.setRange(-999999999, 999999999)
        self.D1_height_lim.setGeometry(QtCore.QRect(287, 490, 55, 25))
        self.D1_height_lim.setObjectName("D1 Height Limit")
        self.D1_height_lim_low = QtWidgets.QSpinBox(self.centralwidget)
        self.D1_height_lim_low.setRange(-999999999, 999999999)
        self.D1_height_lim_low.setGeometry(QtCore.QRect(287, 550, 55, 25))
        self.D1_height_lim_low.setObjectName("D1 Height Low Limit")
        self.D1_center_lim = QtWidgets.QSpinBox(self.centralwidget)
        self.D1_center_lim.setRange(-999999999, 999999999)
        self.D1_center_lim.setGeometry(QtCore.QRect(350, 490, 55, 25))
        self.D1_center_lim.setObjectName("D1 Center Limit")
        self.D1_center_lim_low = QtWidgets.QSpinBox(self.centralwidget)
        self.D1_center_lim_low.setRange(-999999999, 999999999)
        self.D1_center_lim_low.setGeometry(QtCore.QRect(350, 550, 55, 25))
        self.D1_center_lim_low.setObjectName("D1 Center Low Limit")
        self.D1_sigma_lim = QtWidgets.QSpinBox(self.centralwidget)
        self.D1_sigma_lim.setRange(-999999999, 999999999)
        self.D1_sigma_lim.setGeometry(QtCore.QRect(413, 490, 55, 25))
        self.D1_sigma_lim.setObjectName("D1 Sigma Limit")
        self.D1_sigma_lim_low = QtWidgets.QSpinBox(self.centralwidget)
        self.D1_sigma_lim_low.setRange(-999999999, 999999999)
        self.D1_sigma_lim_low.setGeometry(QtCore.QRect(413, 550, 55, 25))
        self.D1_sigma_lim_low.setObjectName("D1 Sigma Low Limit")
        ## D3 LABELS ##
        self.D3_height_label = QtWidgets.QLabel(self.centralwidget)
        self.D3_height_label.setGeometry(QtCore.QRect(496, 520, 60, 20))
        self.D3_center_label = QtWidgets.QLabel(self.centralwidget)
        self.D3_center_label.setGeometry(QtCore.QRect(559, 520, 60, 20))
        self.D3_sigma_label = QtWidgets.QLabel(self.centralwidget)
        self.D3_sigma_label.setGeometry(QtCore.QRect(622, 520, 60, 20))
        ## D3 LIMS ##
        self.D3_height_lim = QtWidgets.QSpinBox(self.centralwidget)
        self.D3_height_lim.setRange(-999999999, 999999999)
        self.D3_height_lim.setGeometry(QtCore.QRect(496, 490, 55, 25))
        self.D3_height_lim.setObjectName("D3 Height Limit")
        self.D3_height_lim_low = QtWidgets.QSpinBox(self.centralwidget)
        self.D3_height_lim_low.setRange(-999999999, 999999999)
        self.D3_height_lim_low.setGeometry(QtCore.QRect(496, 550, 55, 25))
        self.D3_height_lim_low.setObjectName("D3 Height Low Limit")
        self.D3_center_lim = QtWidgets.QSpinBox(self.centralwidget)
        self.D3_center_lim.setRange(-999999999, 999999999)
        self.D3_center_lim.setGeometry(QtCore.QRect(559, 490, 55, 25))
        self.D3_center_lim.setObjectName("D3 Center Limit")
        self.D3_center_lim_low = QtWidgets.QSpinBox(self.centralwidget)
        self.D3_center_lim_low.setRange(-999999999, 999999999)
        self.D3_center_lim_low.setGeometry(QtCore.QRect(559, 550, 55, 25))
        self.D3_center_lim_low.setObjectName("D3 Center Limit")
        self.D3_sigma_lim = QtWidgets.QSpinBox(self.centralwidget)
        self.D3_sigma_lim.setRange(-999999999, 999999999)
        self.D3_sigma_lim.setGeometry(QtCore.QRect(622, 490, 55, 25))
        self.D3_sigma_lim.setObjectName("D3 Sigma Limit")
        self.D3_sigma_lim_low = QtWidgets.QSpinBox(self.centralwidget)
        self.D3_sigma_lim_low.setRange(-999999999, 999999999)
        self.D3_sigma_lim_low.setGeometry(QtCore.QRect(622, 550, 55, 25))
        self.D3_sigma_lim_low.setObjectName("D3 Sigma Low Limit")
        ## G LABELS ##
        self.G_height_label = QtWidgets.QLabel(self.centralwidget)
        self.G_height_label.setGeometry(QtCore.QRect(705, 520, 60, 20))
        self.G_center_label = QtWidgets.QLabel(self.centralwidget)
        self.G_center_label.setGeometry(QtCore.QRect(768, 520, 60, 20))
        self.G_sigma_label = QtWidgets.QLabel(self.centralwidget)
        self.G_sigma_label.setGeometry(QtCore.QRect(831, 520, 60, 20))
        ## G LIMS ##
        self.G_height_lim = QtWidgets.QSpinBox(self.centralwidget)
        self.G_height_lim.setRange(-999999999, 999999999)
        self.G_height_lim.setGeometry(QtCore.QRect(705, 490, 55, 25))
        self.G_height_lim.setObjectName("D1 Height Limit")
        self.G_height_lim_low = QtWidgets.QSpinBox(self.centralwidget)
        self.G_height_lim_low.setRange(-999999999, 999999999)
        self.G_height_lim_low.setGeometry(QtCore.QRect(705, 550, 55, 25))
        self.G_height_lim_low.setObjectName("D1 Height Limit")
        self.G_center_lim = QtWidgets.QSpinBox(self.centralwidget)
        self.G_center_lim.setRange(-999999999, 999999999)
        self.G_center_lim.setGeometry(QtCore.QRect(768, 490, 55, 25))
        self.G_center_lim.setObjectName("D1 Center Limit")
        self.G_center_lim_low = QtWidgets.QSpinBox(self.centralwidget)
        self.G_center_lim_low.setRange(-999999999, 999999999)
        self.G_center_lim_low.setGeometry(QtCore.QRect(768, 550, 55, 25))
        self.G_center_lim_low.setObjectName("D1 Center Low Limit")
        self.G_sigma_lim = QtWidgets.QSpinBox(self.centralwidget)
        self.G_sigma_lim.setRange(-999999999, 999999999)
        self.G_sigma_lim.setGeometry(QtCore.QRect(831, 490, 55, 25))
        self.G_sigma_lim.setObjectName("D1 Sigma Limit")
        self.G_sigma_lim_low = QtWidgets.QSpinBox(self.centralwidget)
        self.G_sigma_lim_low.setRange(-999999999, 999999999)
        self.G_sigma_lim_low.setGeometry(QtCore.QRect(831, 550, 55, 25))
        self.G_sigma_lim_low.setObjectName("D1 Sigma Low Limit")
        ## D2 LABELS ##
        self.D2_height_label = QtWidgets.QLabel(self.centralwidget)
        self.D2_height_label.setGeometry(QtCore.QRect(914, 520, 60, 20))
        self.D2_center_label = QtWidgets.QLabel(self.centralwidget)
        self.D2_center_label.setGeometry(QtCore.QRect(977, 520, 60, 20))
        self.D2_sigma_label = QtWidgets.QLabel(self.centralwidget)
        self.D2_sigma_label.setGeometry(QtCore.QRect(1040, 520, 60, 20))
        ## D2 LIMS ##
        self.D2_height_lim = QtWidgets.QSpinBox(self.centralwidget)
        self.D2_height_lim.setRange(-999999999, 999999999)
        self.D2_height_lim.setGeometry(QtCore.QRect(914, 490, 55, 25))
        self.D2_height_lim.setObjectName("D1 Height Limit")
        self.D2_height_lim_low = QtWidgets.QSpinBox(self.centralwidget)
        self.D2_height_lim_low.setRange(-999999999, 999999999)
        self.D2_height_lim_low.setGeometry(QtCore.QRect(914, 550, 55, 25))
        self.D2_height_lim_low.setObjectName("D1 Height Low Limit")
        self.D2_center_lim = QtWidgets.QSpinBox(self.centralwidget)
        self.D2_center_lim.setRange(-999999999, 999999999)
        self.D2_center_lim.setGeometry(QtCore.QRect(977, 490, 55, 25))
        self.D2_center_lim.setObjectName("D1 Center Limit")
        self.D2_center_lim_low = QtWidgets.QSpinBox(self.centralwidget)
        self.D2_center_lim_low.setRange(-999999999, 999999999)
        self.D2_center_lim_low.setGeometry(QtCore.QRect(977, 550, 55, 25))
        self.D2_center_lim_low.setObjectName("D1 Center Limit")
        self.D2_sigma_lim = QtWidgets.QSpinBox(self.centralwidget)
        self.D2_sigma_lim.setRange(-999999999, 999999999)
        self.D2_sigma_lim.setGeometry(QtCore.QRect(1040, 490, 55, 25))
        self.D2_sigma_lim.setObjectName("D1 Sigma Limit")
        self.D2_sigma_lim_low = QtWidgets.QSpinBox(self.centralwidget)
        self.D2_sigma_lim_low.setRange(-999999999, 999999999)
        self.D2_sigma_lim_low.setGeometry(QtCore.QRect(1040, 550, 55, 25))
        self.D2_sigma_lim_low.setObjectName("D1 Sigma Low Limit")

        ## APPEND INFO BUTTON ##
        self.appendInfo = QtWidgets.QPushButton(self.centralwidget)
        self.appendInfo.setGeometry(QtCore.QRect(1020, 100, 60, 30))
        self.appendInfo.setObjectName("Append Info Button")
        self.appendInfo.setStyleSheet(
            "background-color:rgb(111,180,219)"
            "QPushButton{background-color:rgb(211,211,211)}"  
            "QPushButton:hover{color:blue}"  
            "QPushButton{border-radius:10px}"  
            "QPushButton:pressed{background-color:rgb(100,100,100);border: None;}" 
        )

        ## CHECK BOX FOR G PEAK CHOICE ##
        self.withGcheck = QtWidgets.QCheckBox(self.centralwidget)
        self.withGcheck.setGeometry(QtCore.QRect(100, 445, 60, 60))
        self.withGcheck.setObjectName("With G Check Box")
        self.withGcheckLabel = QtWidgets.QLabel(self.centralwidget)
        self.withGcheck.setGeometry(QtCore.QRect(25, 445, 100, 30))
        self.withGcheck.setObjectName("With G Check Label")

        ## MENU AND STATUS BARS ##
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 848, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        ## BUTTON CLICK FUNCTION CONNECTIONS ##
        self.openfile.clicked.connect(self.openfilo)
        self.trimData.clicked.connect(self.trimmer)
        self.undotrim.clicked.connect(self.trimUndo)
        self.step100.clicked.connect(lambda: self.stepUpdate(100))
        self.step50.clicked.connect(lambda: self.stepUpdate(50))
        self.step25.clicked.connect(lambda: self.stepUpdate(25))
        self.step10.clicked.connect(lambda: self.stepUpdate(10))
        self.step1.clicked.connect(lambda: self.stepUpdate(1))
        self.step01.clicked.connect(lambda: self.stepUpdate(0.1))
        self.step001.clicked.connect(lambda: self.stepUpdate(0.01))
        self.manualFit.clicked.connect(self.manualFitter)
        self.manualUndo.clicked.connect(lambda: self.manualFitter(cancel = True))
        self.curveClicker.clicked.connect(lambda: self.manualFitter(base_custom = True))
        self.curveUndo.clicked.connect(lambda: self.manualFitter(base_custom = True, base_undo = True))
        self.curveAccept.clicked.connect(self.custom_base_fit)
        self.curveSubtract.clicked.connect(lambda: self.custom_base_fit(subtract = True))
        self.saveFileButton.clicked.connect(self.saveFile)
        self.fitGuess.clicked.connect(lambda: self.manualFitter(main = True))

        self.fitCrude.clicked.connect(lambda: self.mainFitter(crude = True))
        self.fitInitial.clicked.connect(lambda: self.mainFitter(initial = True))
        self.fitPlot.clicked.connect(self.mainFitter)
        self.fitImage.clicked.connect(lambda: self.mainFitter(image = True))
        self.appendInfo.clicked.connect(lambda: self.mainFitter(append = True))
        self.autoFitButton.clicked.connect(self.autoFit)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "USRI PyFit1-0"))

        self.openfile.setText(_translate("MainWindow", "Open File"))
        self.openfiletxt.setText(_translate("MainWindow", ""))

        self.trimData.setText(_translate("MainWindow", "Trim"))
        self.trimDatatxt.setText(_translate("MainWindow", ""))
        self.xtrimlabel.setText(_translate("MainWindow", "x"))
        self.undotrim.setText(_translate("MainWindow", "Undo"))
        self.undotrimtxt.setText(_translate("MainWindow", ""))

        self.basetxt.setText(_translate("MainWindow", "Base Polynomial Subtraction"))

        self.stepLabel.setText(_translate("MainWindow","Step"))
        self.step100.setText(_translate("MainWindow","100"))
        self.step50.setText(_translate("MainWindow","50"))
        self.step25.setText(_translate("MainWindow","25"))
        self.step10.setText(_translate("MainWindow","10"))
        self.step1.setText(_translate("MainWindow","1"))
        self.step01.setText(_translate("MainWindow","0.1"))
        self.step001.setText(_translate("MainWindow","0.01"))

        self.manualFit.setText(_translate("MainWindow","Manual Fit"))
        self.manualUndo.setText(_translate("MainWindow","Undo"))
        self.manualAccept.setText(_translate("MainWindow","Accept"))
        self.peakNumLabel.setText(_translate("MainWindow","Peak Num"))

        self.curveClicker.setText(_translate("MainWindow","Curve Click"))
        self.curveUndo.setText(_translate("MainWindow","Undo"))
        self.curveAccept.setText(_translate("MainWindow","Accept"))
        self.polyDegLabel.setText(_translate("MainWindow","Degree"))
        self.curveSubtract.setText(_translate("MainWindow","Subtract"))

        self.saveFileButton.setText(_translate("MainWindow","Save"))

        self.height_label.setText(_translate("MainWindow","Height"))
        self.D1_label.setText(_translate("MainWindow","D1"))
        self.D2_label.setText(_translate("MainWindow","D2"))
        self.D3_label.setText(_translate("MainWindow","D3"))
        self.D4_label.setText(_translate("MainWindow","D4"))
        self.G_label.setText(_translate("MainWindow","G"))
        self.center_label.setText(_translate("MainWindow","Center"))
        self.sigma_label.setText(_translate("MainWindow","HWHM"))
        self.fitGuess.setText(_translate("MainWindow","Guess"))
        self.fitCrude.setText(_translate("MainWindow","Crude"))
        self.fitInitial.setText(_translate("MainWindow","Initial"))
        self.fitPlot.setText(_translate("MainWindow","Fit"))
        self.fitImage.setText(_translate("MainWindow","Image"))
        self.autoFitButton.setText(_translate("MainWindow","Auto Fit"))

        self.maximaLabel.setText(_translate("MainWindow","Maxima"))
        self.minimaLabel.setText(_translate("MainWindow","Minima"))
        self.D4_height_label.setText(_translate("MainWindow","D4_height"))
        self.D4_center_label.setText(_translate("MainWindow","D4_center"))
        self.D4_sigma_label.setText(_translate("MainWindow","D4_sigma"))
        self.D1_height_label.setText(_translate("MainWindow","D1_height"))
        self.D1_center_label.setText(_translate("MainWindow","D1_center"))
        self.D1_sigma_label.setText(_translate("MainWindow","D1_sigma"))
        self.D3_height_label.setText(_translate("MainWindow","D3_height"))
        self.D3_center_label.setText(_translate("MainWindow","D3_center"))
        self.D3_sigma_label.setText(_translate("MainWindow","D3_sigma"))
        self.G_height_label.setText(_translate("MainWindow","G_height"))
        self.G_center_label.setText(_translate("MainWindow","G_center"))
        self.G_sigma_label.setText(_translate("MainWindow","G_sigma"))
        self.D2_height_label.setText(_translate("MainWindow","D2_height"))
        self.D2_center_label.setText(_translate("MainWindow","D2_center"))
        self.D2_sigma_label.setText(_translate("MainWindow","D2_sigma"))

        self.appendInfo.setText(_translate("MainWindow","Append"))

        self.withGcheck.setText(_translate("MainWindow","Use G Peak"))

    def fileToArr(self, name):
        ## MAKE SURE USER OPENED FILE ##
        with open(name, 'r') as f:
            lines = f.readlines()
            f.seek(0)
            assert f.readline() != '.', "ERROR: No file has been selected. Please use the 'Open File' Button to choose data"
        
        ## CONVERT FILE TO NUMPY ARRAYS ##
        xdata = []
        ydata = []
        with open(name, 'r') as fp:
            lines = fp.readlines()
            fp.seek(0)
            with open(fp.readline(), 'r+') as file:
                lines_new = file.readlines()
                file.seek(0)
                if len(lines_new) > 1:
                    if lines_new[0][1] == '#':
                        file.seek(0)
                        file.truncate()
                        file.writelines(lines_new[1:])
                for line in file:
                    grade_data = line.strip().split(',')
                    xdata.append(float(grade_data[0]))
                    ydata.append(float(grade_data[1]))
        
        return [xdata, ydata]

    def openfilo(self, Filepath):
        f = open('tmp1','r')
        Stmp = f.read()
        f.close()
        fileN,_filter = QtWidgets.QFileDialog.getOpenFileName(None,"Open File",Stmp)  
        self.openfiletxt.setText(fileN)
        f = open('tmp1','w')
        f.write(fileN)
        f.close()

        ## PLOT INITIAL FILE ##
        self.plotrawo()
    
    def plotrawo(self):

        ## READ DATA ##
        x = self.fileToArr(name = 'tmp1')[0]
        y = self.fileToArr(name = 'tmp1')[1]

        ## REMOVE LOWER DATA ##
        if min(y) > 0:
            y_new = np.zeros(len(x))
            for i in range(len(x)):
                y_new[i] = y[i] - min(y)
            filename = self.nameGet() + 'initial_subtraction.txt'
            file = open(filename, "w")
            for index in range(len(x)):
                file.write(str(x[index]) + "," + str(y_new[index]) + '\n')
            file.close()
            ## CHANGE tmp1 ##
            path = os.getcwd()
            new_path = path + '\\' + filename
            f = open('tmp1','w')
            f.write(new_path)
            f.close()

        ## READ DATA AGAIN ##
        x = self.fileToArr(name = 'tmp1')[0]
        y = self.fileToArr(name = 'tmp1')[1]

        ## CLEAR OLD ##
        self.graphWidget.clear()

        ## PLOT RAW DATA ##
        pen = pg.mkPen(color=(0, 0, 139))
        self.graphWidget.plot(x, y, pen = pen)

    def stepUpdate(self, value):

        self.D1_height.setSingleStep(int(value))
        self.D2_height.setSingleStep(int(value))
        self.D3_height.setSingleStep(int(value))
        self.D4_height.setSingleStep(int(value))
        self.G_height.setSingleStep(int(value))
        self.D1_center.setSingleStep(int(value))
        self.D2_center.setSingleStep(int(value))
        self.D3_center.setSingleStep(int(value))
        self.D4_center.setSingleStep(int(value))
        self.G_center.setSingleStep(int(value))
        self.D1_sigma.setSingleStep(int(value))
        self.D2_sigma.setSingleStep(int(value))
        self.D3_sigma.setSingleStep(int(value))
        self.D4_sigma.setSingleStep(int(value))
        self.G_sigma.setSingleStep(int(value))
        self.D1_center_lim.setSingleStep(int(value))
        self.D1_center_lim_low.setSingleStep(int(value))
        self.D1_height_lim.setSingleStep(int(value))
        self.D1_height_lim_low.setSingleStep(int(value))
        self.D1_sigma_lim.setSingleStep(int(value))
        self.D1_sigma_lim_low.setSingleStep(int(value))
        self.D2_center_lim.setSingleStep(int(value))
        self.D2_center_lim_low.setSingleStep(int(value))
        self.D2_height_lim.setSingleStep(int(value))
        self.D2_height_lim_low.setSingleStep(int(value))
        self.D2_sigma_lim.setSingleStep(int(value))
        self.D2_sigma_lim_low.setSingleStep(int(value))
        self.D3_center_lim.setSingleStep(int(value))
        self.D3_center_lim_low.setSingleStep(int(value))
        self.D3_height_lim.setSingleStep(int(value))
        self.D3_height_lim_low.setSingleStep(int(value))
        self.D3_sigma_lim.setSingleStep(int(value))
        self.D3_sigma_lim_low.setSingleStep(int(value))
        self.D4_center_lim.setSingleStep(int(value))
        self.D4_center_lim_low.setSingleStep(int(value))
        self.D4_height_lim.setSingleStep(int(value))
        self.D4_height_lim_low.setSingleStep(int(value))
        self.D4_sigma_lim.setSingleStep(int(value))
        self.D4_sigma_lim_low.setSingleStep(int(value))
        self.G_center_lim.setSingleStep(int(value))
        self.G_center_lim_low.setSingleStep(int(value))
        self.G_height_lim.setSingleStep(int(value))
        self.G_height_lim_low.setSingleStep(int(value))
        self.G_sigma_lim.setSingleStep(int(value))
        self.G_sigma_lim_low.setSingleStep(int(value))

        

    def nameGet(self, path = False):

        filepath = self.openfiletxt.text()
        counter = {}
        for letter in filepath:
            if letter not in counter:
                counter[letter] = 0
            counter[letter] += 1
        idx_slash = []
        idx_per = []
        for i in range(len(filepath)):
            if filepath[i] == '/':
                idx_slash.append(i)
            if filepath[i] == '.':
                idx_per.append(i)
        if len(idx_per) > 1:
            idx_last = idx_per[-1]
        elif len(idx_per) == 1:
            idx_last = idx_per[0]
        prenamelst = []
        new_tmp1_lst = []
        for i in range(len(filepath)):
            if i > idx_slash[-1] and i < idx_last:
                prenamelst.append(filepath[i])
            if i < ( idx_slash[-1] + 1 ):
                new_tmp1_lst.append(filepath[i])
        prename = ''.join(prenamelst)
        new_tmp1 = ''.join(new_tmp1_lst)

        if path == True:
            return new_tmp1

        return prename
        
    def trimmer(self):
        ## MAKE SURE USER OPENED FILE ##
        with open('tmp1', 'r') as f:
            lines = f.readlines()
            f.seek(0)
            assert f.readline() != '.', "ERROR: No file has been selected. Please use the 'Open File' Button to choose data"

        ## READ DATA ##
        x = self.fileToArr(name = 'tmp1')[0]
        y = self.fileToArr(name = 'tmp1')[1]

        ## GET USER INPUT ##
        if self.xlowinput.text() == '':
            xlow = float(x[0])
        else:
            xlow = float(self.xlowinput.text())
        if self.xhighinput.text() == '':
            xhigh = float(x[-1])
        else:
            xhigh = float(self.xhighinput.text())

        ## REMOVE VALUES ##
        x_new = []
        y_new = []
        for i in range(len(x)):
            if x[i] >= xlow and x[i] <= xhigh:
                x_new.append(x[i])
                y_new.append(y[i])

        ## GET tmp1 PATH ##
        trimName = self.nameGet() + '-trimmed.txt'

        ## WRITE TRIMMED DATA TO A NEW TXT FILE ##
        file = open(trimName, "w")
        for index in range(len(x_new)):
            file.write(str(x_new[index]) + "," + str(y_new[index]) + '\n')
        file.close()

        ## TRANSFER OLD tmp1 TO tmp2 ##
        f = open('tmp1','r')
        lines = f.readlines()
        f.seek(0)
        old_path = lines[0]
        f.close()
        f = open('tmp2','w')
        f.write(old_path)
        f.close()

        ## CHANGE tmp1 ##
        path = os.getcwd()
        new_path = path + '\\' + trimName
        f = open('tmp1','w')
        f.write(new_path)
        f.close()

        ## UPDATE PLOT ##
        self.graphWidget.clear()
        pen = pg.mkPen(color=(0, 0, 139))
        self.graphWidget.plot(x_new, y_new, pen = pen)
    
    def trimUndo(self):

        ## CHECK TRIM WAS USED ##
        with open('tmp2', 'r') as f:
            lines = f.readlines()
            f.seek(0)
            assert f.readline() != '.', "ERROR: No trim completed. Please hit 'Trim' and try again."

        ## REPLACE tmp1 WITH tmp2 ##
        f = open('tmp2','r')
        lines = f.readlines()
        f.seek(0)
        old_path = lines[0]
        f.close()
        f = open('tmp1','w')
        f.write(old_path)
        f.close()

        ## UPDATE GRAPH ##
        self.plotrawo()

    def manualFitter(self, cancel = False, base_custom = False, base_undo = False, main = False):

        if base_custom == True:

            ## CHANGE tmp6 ##
            path = os.getcwd()
            new_path = path + '\\' + 'base_click_coords.txt'
            f = open('tmp6','w')
            f.write(new_path)
            f.close()

            ## CALL MAIN FUNC ##
            if base_undo == True:
                self.curveClick(base_undo = True)
            else:
                self.curveClick()

            return

        ## CHANGE tmp5 ##
        path = os.getcwd()
        new_path = path + '\\' + 'click_coords.txt'
        f = open('tmp5','w')
        f.write(new_path)
        f.close()

        if main == True:
            f = open('tmp4','w')
            f.write('main')
            f.close()
            self.fitPlotUpdate(main = True)
            return
        if cancel == True:
            self.fitPlotUpdate(cancel = True)
        else:
            self.fitPlotUpdate()

    def fitPlotUpdate(self, cancel = False, main = False):

        ## UNDO BUTTON FUNCTION ##
        if cancel == True:

            ## RESET CLICK COUNT ##
            f = open('tmp4', 'w')
            f.write('.')
            f.close()

            ## CLEAR CLICK COORDS ##
            f = open('click_coords.txt', 'w')
            f.truncate()
            f.close()

            ## CLEAR CENTER VALUES ##
            f = open('centers', 'w')
            f.truncate()
            f.close()

            ## CLEAR HEIGHT VALUES ##
            f = open('heights', 'w')
            f.truncate()
            f.close()

            ## CLEAR SIGMA VALUES ##
            f = open('sigmas', 'w')
            f.truncate()
            f.close()

            ## CLEAR half max VALUES ##
            f = open('halfmax', 'w')
            f.truncate()
            f.close()

            return

        ## GET NUMBER OF PEAKS AND NUMBER OF CLICKS NEEDED ##
        if main == False:
            if self.peakNumInput.text() == '':
                peak_num = 2  
            elif self.peakNumInput.text() != '':
                peak_num = int(self.peakNumInput.text())
        elif main == True:
            peak_num = 2
        center_clicks = peak_num * 2

        ## READ CLICK COUNT ##
        f = open('tmp4', 'r')
        lines = f.readlines()
        f.seek(0)
        if lines[0] == '.':
            click_count = 0
        elif lines[0] == 'main':
            print('first go from fitplotupdate line 996, registered as main')
            click_count = 0
        else:
            print('should be looping line 999')
            click_count = int(lines[0])
        f.close()

        ## READ CLICK COORDS ##
        x_clicks = self.fileToArr(name = 'tmp5')[0]
        y_clicks = self.fileToArr(name = 'tmp5')[1]

        ## READ DATA ##
        x = self.fileToArr(name = 'tmp1')[0]
        y = self.fileToArr(name = 'tmp1')[1]

        ## PLOT DATA ##
        plt.close()
        fig = plt.figure(figsize = (10,5))
        ax = fig.add_subplot(111)
        ax.plot(x,y,'b-', alpha = 0.6)
        plt.title('Click Left and Right of Center')

        ## PLOT CENTER LINES IF NEEDED ##
        centers = []
        for i in range(len(x_clicks)):
            if i % 2 == 0 and len(x_clicks) > ( i + 1 ):
                centers.append(x_clicks[i] + ( abs(x_clicks[i] - x_clicks[i+1]) / 2 ))
        for i in range(len(centers)):
            plt.axvline( x = float(centers[i]), ls = '--' )

        ## CONTINUE USER CLICKS ##
        if click_count < center_clicks:

            ## PLOT CLICKS ##
            plt.scatter(x_clicks, y_clicks, color = 'red', s = 20)

            ## PREPARE NEXT CLICK ##
            cid = fig.canvas.mpl_connect('button_press_event', self.onClick)
            plt.show()

        ## FINISH USER CLICKS ##
        if click_count == center_clicks:

            ## RECORD CENTER VALUES ##
            f = open('centers', 'a')
            for i in range(len(centers)):
                f.write(str(centers[i]) + '\n')
            f.close()

            ## RESET CLICK COUNT ##
            if main == False:
                f = open('tmp4', 'w')
                f.write('centers finished')
                f.close()
            elif main == True:
                ## ENSURE CLICKS ARE FOR MAIN FITTING, SEE self.onClick ##
                f = open('tmp4', 'w')
                f.write('main2')
                f.close()

            ## CLEAR CLICK COORDS ##
            f = open('click_coords.txt', 'w')
            f.truncate()
            f.close()

            ## CALL FUNC TO GET DESIRED HEIGHT ##
            if main == False:
                self.manualHeight()
            elif main == True:
                print('made it through fitplotupdate')
                self.manualHeight(main = True)


            return

    def manualHeight(self, main = False):

        """ Need to take cen_vals from fitPlotUpdate and generate new clicks for heights, put that to new variable,
        then pass cen_vals and height_vals to new function to get sigma_vals, then final func
        should be the one to call self.fit() passing all vals needed for fit """

        ## GET NUMBER OF PEAKS AND NUMBER OF CLICKS NEEDED ##
        if main == False:
            if self.peakNumInput.text() == '':
                peak_num = 2  
            elif self.peakNumInput.text() != '':
                peak_num = int(self.peakNumInput.text())
        elif main == True:
            peak_num = 2

        ## READ IN CENTER VALUES ##
        cen_vals = self.fitFile(name = 'centers')

        ## READ CLICK COUNT ##
        f = open('tmp4', 'r')
        lines = f.readlines()
        f.seek(0)
        if lines[0] == 'centers finished':
            click_count = 0
        elif lines[0] == 'main2':
            click_count = 0
        else:
            click_count = int(lines[0])
        f.close()

        ## READ DATA ##
        x = self.fileToArr(name = 'tmp1')[0]
        y = self.fileToArr(name = 'tmp1')[1]

        ## READ CLICK COORDS ##
        x_clicks = self.fileToArr(name = 'tmp5')[0]
        y_clicks = self.fileToArr(name = 'tmp5')[1]

        ## MAKE PLOT ##
        plt.close()
        fig = plt.figure(figsize = (10,5))
        ax = fig.add_subplot(111)
        ax.plot(x,y,'b-', alpha = 0.6)
        if main == False:
            plt.title('Peak number %d : Click desired height' % ( click_count + 1 ) )
        elif main == True:
            plt.title('Peak D%d : Click desired height' % ( click_count + 1 ) )

        ## PLOT CENTER LINES ##
        if len(cen_vals) >= 1:
            for i in range(peak_num):
                plt.axvline(x = float(cen_vals[i]), ls = '--' )

        if click_count < peak_num:

            ## PLOT CLICKS ##
            plt.scatter(x_clicks, y_clicks, color = 'red', s = 20)

            ## PREPARE NEXT CLICK ##
            cid = fig.canvas.mpl_connect('button_press_event', self.onClick)
            plt.show()

        if click_count == peak_num:

            ## PLOT CLICKS ##
            plt.scatter(x_clicks, y_clicks, color = 'red', s = 20)

            ## RECORD CLICKED HEIGHTS ##
            f = open('heights', 'a')
            for i in range(len(y_clicks)):
                f.write(str(y_clicks[i]) + '\n')
            f.close()

            ## CLEAR CLICK COORDS ##
            f = open('click_coords.txt', 'w')
            f.truncate()
            f.close()

            ## RESET CLICK COUNT ##
            if main == False:
                f = open('tmp4', 'w')
                f.write('heights finished')
                f.close()
            elif main == True:
                f = open('tmp4', 'w')
                f.write('main3')
                f.close()

            ## SET PEAK COUNT FOR SIGMA FUNC ##
            f = open('tmp8', 'w')
            f.write('.')
            f.close()
            
            ## CALL SIGMA FUNC ##
            if main == False:
                self.manualSigmas()
            elif main == True:
                self.manualSigmas(main = True)

            return

    def manualSigmas(self, main = False):

        ## GET NUMBER OF PEAKS AND NUMBER OF CLICKS NEEDED ##
        if main == False:
            if self.peakNumInput.text() == '':
                peak_num = 2  
            elif self.peakNumInput.text() != '':
                peak_num = int(self.peakNumInput.text())
        elif main == True:
            peak_num = 2
        clicks_needed = peak_num * 2

        ## READ IN CENTER VALS ##
        cen_vals = self.fitFile(name = 'centers')

        ## READ IN HEIGHT VALS ##
        height_vals = self.fitFile(name = 'heights')

        ## READ CLICK COUNT ##
        f = open('tmp4', 'r')
        lines = f.readlines()
        f.seek(0)
        if lines[0] == 'heights finished':
            click_count = 0
        if lines[0] == 'main3':
            click_count = 0
        else:
            click_count = int(lines[0])
        f.close()

        ## READ PEAK COUNT ##
        f = open('tmp8', 'r')
        lines = f.readlines()
        f.seek(0)
        if lines[0] == '.':
            peak_count = 1
        else:
            peak_count = int(lines[0])
        f.close()

        ## READ DATA ##
        x = self.fileToArr(name = 'tmp1')[0]
        y = self.fileToArr(name = 'tmp1')[1]

        ## READ CLICK COORDS ##
        x_clicks = self.fileToArr(name = 'tmp5')[0]
        y_clicks = self.fileToArr(name = 'tmp5')[1]

        ## MAKE PLOT ##
        plt.close()
        fig = plt.figure(figsize = (10,5))
        ax = fig.add_subplot(111)
        ax.plot(x,y,'b-', alpha = 0.6)
        if click_count % 2 == 0:
            if main == False:
                plt.title('Peak number %d : Click the Half Maximum on the Center Line' % peak_count)
            elif main == True:
                plt.title('Peak D%d : Click the Half Maximum on the Center Line' % peak_count)
        if click_count % 2 != 0:
            plt.title('Click Where the Horizontal Line Meets Your Data')

        ## PLOT CENTER LINES ##
        if len(cen_vals) >= 1:
            for i in range(peak_num):
                plt.axvline(x = float(cen_vals[i]), ls = '--', color = 'green')

        ## PLOT HORIZONTAL LINES ##
        if click_count % 2 == 0:

            ## COMPUTER GUESS FOR HALF MAXIMA ##
            if click_count != clicks_needed:

                height_guess = height_vals[ peak_count - 1 ] / 2

                plt.plot( 
                    (x[0], x[-1]), 
                    (height_guess, 
                    height_guess),
                    ls = '--',
                    color ='gray',
                    alpha = 0.5, 
                    label = 'Computer Guess'
                    )
                plt.legend()

        if click_count % 2 != 0:

            plt.plot(
                (x[0], x[-1]),
                (y_clicks[-1], y_clicks[-1]),
                ls = '--',
                color = 'red'
                )

        if click_count < clicks_needed:

            ## PLOT CLICKS ##
            plt.scatter(x_clicks, y_clicks, color = 'red', s = 20)

            ## ADD TO PEAK COUNTER ##
            if click_count % 2 != 0:
                f = open('tmp8', 'w')
                f.truncate()
                f.write( str( peak_count + 1 ) )
                f.close()

            ## PREPARE NEXT CLICK ##
            cid = fig.canvas.mpl_connect('button_press_event', self.onClick)
            plt.show()

        if click_count == clicks_needed:

            plt.close()

            ## COLLECT SIGMAS ##
            half_max = []
            sigma_end = []
            for i in range(len(x_clicks)):
                if i % 2 == 0:
                    half_max.append(y_clicks[i])
                if i %2 != 0:
                    sigma_end.append(x_clicks[i])
            sigmas = []
            for i in range(peak_num):
                sigmas.append( abs( cen_vals[i] - sigma_end[i] ) )

            ## RECORD SIGMA DATA ##
            f = open('sigmas', 'a')
            for i in range(len(sigmas)):
                f.write(str(sigmas[i]) + '\n')
            f.close()

            ## RECORD HALF MAXIMA DATA ##
            f = open('halfmax', 'a')
            for i in range(len(half_max)):
                f.write(str(half_max[i]) + '\n')
            f.close()
            
            ## CALL THE FIT ##
            if main == False:
                self.fit()
            elif main == True:
                self.mainFitter(guess = True)

            return

    def fit(self):

        ## READ IN USER DESIRED PEAK TYPE ##
        peak_type = self.manualType.currentIndex()

        ## READ DATA ##
        x = self.fileToArr(name = 'tmp1')[0]
        y = self.fileToArr(name = 'tmp1')[1]

        ## CENTERS ##
        cen_vals = self.fitFile(name = 'centers')
        ## HEIGHTS ##
        height_vals = self.fitFile(name = 'heights')
        ## SIGMAS ##
        sigma_vals = self.fitFile(name = 'sigmas')
        ## HALF MAXIMA ##
        half_max_vals = self.fitFile(name = 'halfmax')

        ## GET NUMBER OF DESIRED PEAKS ##
        if self.peakNumInput.text() == '':
            peak_num = 2  
        elif self.peakNumInput.text() != '':
            peak_num = int(self.peakNumInput.text())

        ## GENERATE MIN MAX PARAM VALS ##
        sig_min = np.zeros(peak_num)
        sig_max = np.zeros(peak_num)
        # amp_min = np.zeros(peak_num)
        # amp_max = np.zeros(peak_num)
        amp_guess = np.zeros(peak_num)
        for i in range(int(peak_num)):
            sig_min[i] = sigma_vals[i] - 1
            sig_max[i] = sigma_vals[i] * 1.25
            ## LORENTZIAN ##
            if peak_type == 0:
                amp_guess[i] = height_vals[i] * np.pi * sigma_vals[i]
                print('amplitudes : ', amp_guess[i])
            ## GAUSSIAN ##
            elif peak_type == 1:
                amp_guess[i] = height_vals[i] * np.sqrt( np.pi / np.log(2) ) * sigma_vals[i]
            ## VOIGT ##
            elif peak_type == 2:
                w = np.exp( 1 / np.sqrt(2) ) * math.erfc( 1 / np.sqrt(2) )
                amp_guess[i] = ( 2 * height_vals[i] * sigma_vals[i] * np.sqrt( 2 * np.pi ) ) / ( 3.6013 * w )

        # print('sig min: ', sig_min, 'sig max: ', sig_max)
            # amp_guess[i] = amp_min[i] + (( amp_max[i] - amp_min[i] ) / 2)

        ## GENERATE MODELS ##
        models = []
        prefixes = []
        for i in range(int(peak_num)):
            peak_name = "peak%d_" % i
            if peak_type == 0:
                peak = LorentzianModel(prefix = peak_name)
            elif peak_type == 1:
                peak = GaussianModel(prefix = peak_name)
            elif peak_type == 2:
                peak = VoigtModel(prefix = peak_name)
            prefixes.append(peak_name)
            models.append(peak)

        ## INITIALIZE MODEL AND PARAMETERS ##
        mod = np.sum(models[0:int(peak_num)])
        pars = mod.make_params()

        ## GUESS PARAM VALS ##
        for i, prefix in zip(range(0, int(peak_num)), prefixes[0:int(peak_num)]):
            pars[prefix + 'center'].set(cen_vals[i], vary = False)
            # pars[prefix + 'amplitude'].set(amp_guess[i], max = amp_max[i], min = amp_min[i])
            pars[prefix + 'amplitude'].set(amp_guess[i], vary = False)
            pars[prefix + 'sigma'].set(sigma_vals[i], min = sig_min[i], max = sig_max[i])

        ## GENERATE FIT ##
        # init = mod.eval(pars, x=x)
        out = mod.fit(y, pars, x=x)
        # comps = out.eval_components(x=x)
        
        ## PLOT FIT W/ DATA ##
        ax = plt.subplots(figsize = (10,5))
        plt.plot(x, y, 'b')
        plt.plot(x, out.init_fit, 'k--', label = 'initial')
        # for i in range(int(peak_num)):
        #     plt.plot(x, comps[prefixes[i]], '--', label = prefixes[i])
        plt.plot(x, out.best_fit, 'r-', label = 'best fit')
        plt.legend()
        plt.show()

    def fitFile(self, name):

        """ Reads in info from manual fit process.
            Used for the peak centers, heights, sigmas, and half maximas
            
            Inputs: name (str)
        """
        
        f = open(name, 'r')
        data = []
        for line in f:
            grade_data = line.strip().split('\n')
            data.append(float(grade_data[0]))

        return data


    def onClick(self, event):

        ## READ IN CLICK COUNT ##
        f = open('tmp4', 'r')
        lines = f.readlines()
        f.seek(0)
        if lines[0] == '.':
            click_count = 0
            fp = open('tmp4','w')
            fp.write(str(click_count))
            fp.close()
            f = open('order', 'w')
            f.write('0')
            f.close()
        elif lines[0] == 'centers finished':
            click_count = 0
            fp = open('tmp4','w')
            fp.write(str(click_count))
            fp.close()
            f = open('order', 'w')
            f.write('1')
            f.close()
        elif lines[0] == 'heights finished':
            click_count = 0
            fp = open('tmp4','w')
            fp.write(str(click_count))
            fp.close()
            f = open('order', 'w')
            f.write('2')
            f.close()
        elif lines[0] == 'main':
            click_count = 0
            fp = open('tmp4','w')
            fp.write(str(click_count))
            fp.close()
            f = open('order', 'w')
            f.write('3')
            f.close()
        elif lines[0] == 'main2':
            click_count = 0
            fp = open('tmp4','w')
            fp.write(str(click_count))
            fp.close()
            f = open('order', 'w')
            f.write('4')
            f.close()
        elif lines[0] == 'main3':
            click_count = 0
            fp = open('tmp4','w')
            fp.write(str(click_count))
            fp.close()
            f = open('order', 'w')
            f.write('5')
            f.close()

        else:
            click_count = int(lines[0])
        f.close()

        ## UPDATE CLICK COUNTER ##
        click_count += 1
        f = open('tmp4', 'w')
        f.write(str(click_count))
        f.close()

        ## GET CLICK COORDS ##
        x_coord, y_coord = event.xdata, event.ydata

        ## WRITE CLICK COORDS TO TXT FILE ##
        f = open('click_coords.txt', 'a')
        f.write(str(x_coord) + ',' + str(y_coord) + '\n')
        f.close()

        ## READ ORDER FOR CALL BACK ##
        f = open('order', 'r')
        lines = f.readlines()
        f.seek(0)
        order = lines[0]

        ## CALL BACK ##
        if order == '0':
            self.fitPlotUpdate()
        if order == '1':
            self.manualHeight()
        if order == '2':
            self.manualSigmas()
        if order == '3':
            print('first recall of fitplotupdate with main line 1458')
            self.fitPlotUpdate(main = True)
        if order == '4':
            self.manualHeight(main = True)
        if order == '5':
            self.manualSigmas(main = True)

    def curveClick(self, base_undo = False):

        ## READ CLICK COORDS ##
        x_clicks = self.fileToArr(name = 'tmp6')[0]
        y_clicks = self.fileToArr(name = 'tmp6')[1]

        ## READ DATA ##
        x = self.fileToArr(name = 'tmp1')[0]
        y = self.fileToArr(name = 'tmp1')[1]

        plt.close()

        ## PLOT DATA ##
        fig = plt.figure(figsize = (10,5))
        ax = fig.add_subplot(111)
        ax.plot(x,y,'b-', alpha = 0.6)

        ## UNDO BUTTON FUNCTION ##
        if base_undo == True:

            ## CLEAR CLICK COORDS ##
            f = open('base_click_coords.txt', 'w')
            f.truncate()
            f.close()

            ## CLEAR GRAPH ##
            ax.clear()

            ## REPLACE tmp1 WITH tmp7 ##
            f = open('tmp7','r')
            lines = f.readlines()
            f.seek(0)
            old_path = lines[0]
            f.close()
            f = open('tmp1','w')
            f.write(old_path)
            f.close()

            return

        ## PLOT CLICKS ##
        plt.scatter(x_clicks, y_clicks, color = 'red', s = 20)


        ## PREPARE NEXT CLICK ##
        cid = fig.canvas.mpl_connect('button_press_event', self.base_curve_clicked)
        plt.show()
    
    def base_curve_clicked(self, event):

        ## GET CLICK COORDS ##
        x_coord, y_coord = event.xdata, event.ydata

        ## WRITE CLICK COORDS TO TXT FILE ##
        f = open('base_click_coords.txt', 'a')
        f.write(str(x_coord) + ',' + str(y_coord) + '\n')
        f.close()

        ## CALL BACK ##
        self.curveClick()

    def custom_base_fit(self, subtract = False):

        ## POLYNOMIAL DEGREE FROM USER INPUT ##
        deg = int(self.polyDeg.text())

        ## READ CLICK COORDS ##
        x_clicks = self.fileToArr(name = 'tmp6')[0]
        y_clicks = self.fileToArr(name = 'tmp6')[1]

        ## READ DATA ##
        x = self.fileToArr(name = 'tmp1')[0]
        y = self.fileToArr(name = 'tmp1')[1]

        ## GENERATE POLYNOMIAL ##
        z = np.polyfit(x_clicks, y_clicks, deg)
        p = np.poly1d(z)

        ## GENERATE ARRAY OF POLYNOMIAL VALUES ##
        y_poly = np.zeros(len(x))
        for i in range(len(x)):
            y_poly[i] = p(x[i])

        ## SUBTRACTION FUNC ##
        if subtract == True:

            ## SUBTRACT VALUES ##
            y_subtracted = np.zeros(len(x))
            for i in range(len(x)):
                y_subtracted[i] = y[i] - y_poly[i]
            
            ## BRING UP TO SCALE ##
            lowest = min(y_subtracted)
            if lowest < 0:
                for i in range(len(x)):
                    y_subtracted[i] -= lowest

            ## WRITE SUBTRACTED DATA TO A NEW TXT FILE ##
            subName = self.nameGet() + '-subtracted.txt'
            file = open(subName, "w")
            for index in range(len(x)):
                file.write(str(x[index]) + "," + str(y_subtracted[index]) + '\n')
            file.close()

            ## TRANSFER OLD tmp1 TO tmp7 ##
            f = open('tmp1','r')
            lines = f.readlines()
            f.seek(0)
            old_path = lines[0]
            f.close()
            f = open('tmp7','w')
            f.write(old_path)
            f.close()

            ## CHANGE tmp1 ##
            path = os.getcwd()
            new_path = path + '\\' + subName
            f = open('tmp1','w')
            f.write(new_path)
            f.close()

            ## PLOT SUBTRACTED DATA ##
            self.graphWidget.clear()
            pen = pg.mkPen(color=(0, 0, 139))
            self.graphWidget.plot(x, y_subtracted, pen = pen)
            
            return

        ## PLOT DATA, CLICKED POINTS, AND POLYNOMIAL ##
        fig = plt.figure(figsize = (10,5))
        ax = fig.add_subplot(111)
        ax.plot(x,y,'b-')
        ax.scatter(x_clicks, y_clicks, color = 'red', s = 20)
        ax.plot(x, y_poly, 'r--')
        plt.show()

    def saveFile(self):

        ## READ DATA ##
        x = self.fileToArr(name = 'tmp1')[0]
        y = self.fileToArr(name = 'tmp1')[1]

        ## GET OG FILE NAME ##
        fileName = self.nameGet() + 'NEW'

        f = open(fileName, 'a')
        for i in range(len(x)):
            f.write(str(x[i]) + ',' + str(y[i]) + '\n')
        f.close()

    def mainFitter(
                    self,
                    guess = False,
                    initial = False,
                    image = False,
                    append = False,
                    crude = False,
                    auto = False
    ):

        ## READ DATA ##
        x = self.fileToArr(name = 'tmp1')[0]
        y = self.fileToArr(name = 'tmp1')[1]

        ## CENTERS ##
        cen_vals = self.fitFile(name = 'centers')
        ## HEIGHTS ##
        height_vals = self.fitFile(name = 'heights')
        ## SIGMAS ##
        sigma_vals = self.fitFile(name = 'sigmas')

        ## CHECK GL / D1 RATIO ##
        max_intensity = []
        for i in range(2):
            y_near = []
            for j in range(len(x)):
                if x[j] <= ( cen_vals[i] + 10 ) and x[j] >= ( cen_vals[i] - 10 ):
                    y_near.append(y[j])
            max_intensity.append(max(y_near))
        ratio = max_intensity[1] / max_intensity[0]
        if guess == True:
            print('ratio :', ratio)
            if ratio > 1.5:
                print('ratio > 1.5 : Suggestion : Fit Without G Band')
            elif ratio < 1.5:
                print('ratio < 1.5 : Suggestion : Fit With G Band')

        ## READ IN USER DESIRED PEAK TYPE ##
        fit_style = self.fitType.currentIndex()

        ## FIND IDEAL INITIAL VALUES ##
        variance = 0.3
        for i in range(len(x)):
            # D4 #
            if x[i] == closest(x,1245):
                D4_height_ref = y[i] - ( y[i] * variance )
            # D3 #
            if x[i] == closest(x,1510):
                D3_height_ref = y[i] - ( y[i] * variance )
            # G #
            if x[i] == closest(x,1593):
                    G_height_ref = y[i] * 0.2

        ## GUESS VALUES ##
        if guess == True:
            self.D1_height.setValue(int(height_vals[0]))
            self.D1_center.setValue(int(cen_vals[0]))
            self.D1_sigma.setValue(int(sigma_vals[0]))
            self.D2_height.setValue(int(height_vals[1]))
            self.D2_center.setValue(int(cen_vals[1]))
            self.D2_sigma.setValue(int(sigma_vals[1]))
            self.D3_height.setValue(int(D3_height_ref))
            self.D3_center.setValue(1500)
            self.D3_sigma.setValue(80)
            self.D4_height.setValue(int(D4_height_ref))
            self.D4_center.setValue(1245)
            self.D4_sigma.setValue(50)
            self.G_height.setValue(int(G_height_ref))
            self.G_center.setValue(1580)
            self.G_sigma.setValue(30)

            return

        ## READ INPUTS ##
        D1_height = int(self.D1_height.text())
        D1_center = int(self.D1_center.text())
        D1_sigma = int(self.D1_sigma.text())
        D2_height = int(self.D2_height.text())
        D2_center = int(self.D2_center.text())
        D2_sigma = int(self.D2_sigma.text())
        D3_height = int(self.D3_height.text())
        D3_center = int(self.D3_center.text())
        D3_sigma = int(self.D3_sigma.text())
        D4_height = int(self.D4_height.text())
        D4_center = int(self.D4_center.text())
        D4_sigma = int(self.D4_sigma.text())
        G_height = int(self.G_height.text())
        G_center = int(self.G_center.text())
        G_sigma = int(self.G_sigma.text())

        ## CRUDE INITIAL MODEL ##
        if crude == True:
            if fit_style == 0:
                D3 = LorentzianModel(prefix = 'D3_')
                D3_amplitude = D3_height * np.pi * D3_sigma
                D4 = LorentzianModel(prefix = 'D4_')
                D4_amplitude = D4_height * np.pi * D4_sigma
                if int(self.withGcheck.checkState()) == 2:
                    G = LorentzianModel(prefix = 'G_')
                    G_amplitude = G_height * np.pi * G_sigma
            if fit_style == 1:
                D3 = GaussianModel(prefix = 'D3_')
                D3_amplitude = D3_height * np.sqrt(2*np.pi) * D3_sigma
                D4 = GaussianModel(prefix = 'D4_')
                D4_amplitude = D4_height * np.sqrt(2*np.pi) * D4_sigma
                if int(self.withGcheck.checkState()) == 2:
                    G = LorentzianModel(prefix = 'G_')
                    G_amplitude = G_height * np.pi * G_sigma

            pars = D4.make_params(amplitude = D4_amplitude, center = D4_center, sigma = D4_sigma)
            pars.update(D3.make_params())
            pars['D3_amplitude'].set(D3_amplitude)
            pars['D3_center'].set(D3_center)
            pars['D3_sigma'].set(D3_sigma)
            if int(self.withGcheck.checkState()) == 2:
                pars.update(G.make_params())
                pars['G_amplitude'].set(G_amplitude)
                pars['G_center'].set(G_center)
                pars['G_sigma'].set(G_sigma)

            if int(self.withGcheck.checkState()) == 0:
                crude_mod = D3 + D4
            if int(self.withGcheck.checkState()) == 2:
                crude_mod = D3 + D4 + G

            crude_out = crude_mod.fit(y, pars, x=x)

            ## PLOT CRUDE MODEL ##
            legend = self.graphWidget.addLegend()
            self.graphWidget.clear()
            pen = pg.mkPen(color=(0, 0, 139))
            dataPlot = self.graphWidget.plot(x, y, pen = pen)
            InitColour = pg.mkPen(color=(0, 0, 0))
            InitPlot = self.graphWidget.plot(x, crude_out.init_fit, pen = InitColour)
            legend.addItem(InitPlot, name = 'Initial')

            ## USE CRUDE MODEL FOR D1 and D2 HEIGHTS ##
            for i in range(len(x)):
                # D1 #
                if x[i] == closest(x,D1_center):
                    D1_offset = crude_out.init_fit[i]
                # D2 #
                if x[i] == closest(x,D2_center):
                    D2_offset = crude_out.init_fit[i]

            ## UPDATE D1 and D2 HEIGHTS ##
            self.D1_height.setValue(int( height_vals[0] - D1_offset))
            self.D2_height.setValue(int( height_vals[1] - D2_offset))

            return

        ## GUESS LIMIT VALUES ##
        if initial == True:
            self.D1_height_lim.setValue(int(D1_height + 10))
            self.D1_height_lim_low.setValue(int(D1_height - 100))
            self.D1_center_lim.setValue(int(D1_center + 10))
            self.D1_center_lim_low.setValue(int(D1_center - 10))
            self.D1_sigma_lim.setValue(int(D1_sigma + 5))
            self.D1_sigma_lim_low.setValue(int(D1_sigma - 30))
            #
            self.D2_height_lim.setValue(int(D2_height + 200))
            self.D2_height_lim_low.setValue(int(D2_height - 400))
            self.D2_center_lim.setValue(int(D2_center + 5))
            self.D2_center_lim_low.setValue(int(D2_center - 5))
            self.D2_sigma_lim.setValue(int(D2_sigma + 5))
            self.D2_sigma_lim_low.setValue(int(D2_sigma - 15))
            #
            self.D3_height_lim.setValue(int(D3_height + 20))
            self.D3_height_lim_low.setValue(int(D3_height - 20))
            self.D3_center_lim.setValue(int(D3_center + 50))
            self.D3_center_lim_low.setValue(int(D3_center - 50))
            self.D3_sigma_lim.setValue(int(D3_sigma + 30))
            self.D3_sigma_lim_low.setValue(int(D3_sigma - 20))
            #
            self.D4_height_lim.setValue(int(D4_height + 20))
            self.D4_height_lim_low.setValue(int(D4_height - 20))
            self.D4_center_lim.setValue(int(D4_center + 50))
            self.D4_center_lim_low.setValue(int(D4_center - 50))
            self.D4_sigma_lim.setValue(int(D4_sigma + 30))
            self.D4_sigma_lim_low.setValue(int(D4_sigma - 15))
            #
            self.G_height_lim.setValue(int(G_height + 20))
            self.G_height_lim_low.setValue(int(G_height - 20))
            self.G_center_lim.setValue(int(G_center + 10))
            self.G_center_lim_low.setValue(int(G_center - 10))
            self.G_sigma_lim.setValue(int(G_sigma + 15))
            self.G_sigma_lim_low.setValue(int(G_sigma - 15))

        ## LIMITS ##
        D1_height_lim_high = int(self.D1_height_lim.text())
        D1_height_lim_low = int(self.D1_height_lim_low.text())
        D1_center_lim_high = int(self.D1_center_lim.text())
        D1_center_lim_low = int(self.D1_center_lim_low.text())
        D1_sigma_lim_high = int(self.D1_height_lim.text())
        D1_sigma_lim_low = int(self.D1_height_lim_low.text())
        #
        D2_height_lim_high = int(self.D2_height_lim.text())
        D2_height_lim_low = int(self.D2_height_lim_low.text())
        D2_center_lim_high = int(self.D2_center_lim.text())
        D2_center_lim_low = int(self.D2_center_lim_low.text())
        D2_sigma_lim_high = int(self.D2_height_lim.text())
        D2_sigma_lim_low = int(self.D2_height_lim_low.text())
        #
        D3_height_lim_high = int(self.D3_height_lim.text())
        D3_height_lim_low = int(self.D3_height_lim_low.text())
        D3_center_lim_high = int(self.D3_center_lim.text())
        D3_center_lim_low = int(self.D3_center_lim_low.text())
        D3_sigma_lim_high = int(self.D3_height_lim.text())
        D3_sigma_lim_low = int(self.D3_height_lim_low.text())
        #
        D4_height_lim_high = int(self.D4_height_lim.text())
        D4_height_lim_low = int(self.D4_height_lim_low.text())
        D4_center_lim_high = int(self.D4_center_lim.text())
        D4_center_lim_low = int(self.D4_center_lim_low.text())
        D4_sigma_lim_high = int(self.D4_height_lim.text())
        D4_sigma_lim_low = int(self.D4_height_lim_low.text())
        #
        G_height_lim_high = int(self.G_height_lim.text())
        G_height_lim_low = int(self.G_height_lim_low.text())
        G_center_lim_high = int(self.G_center_lim.text())
        G_center_lim_low = int(self.G_center_lim_low.text())
        G_sigma_lim_high = int(self.G_height_lim.text())
        G_sigma_lim_low = int(self.G_height_lim_low.text())

        ## GENERATE MODELS FOR FIT ##
        if fit_style == 0:
            D1 = LorentzianModel(prefix = 'D1_')
            D2 = LorentzianModel(prefix = 'D2_')
            D3 = LorentzianModel(prefix = 'D3_')
            D4 = LorentzianModel(prefix = 'D4_')
            if int(self.withGcheck.checkState()) == 2:
                G = LorentzianModel(prefix = 'G_')
        if fit_style == 1:
            D1 = GaussianModel(prefix = 'D1_')
            D2 = GaussianModel(prefix = 'D2_')
            D3 = GaussianModel(prefix = 'D3_')
            D4 = GaussianModel(prefix = 'D4_')
            if int(self.withGcheck.checkState()) == 2:
                G = LorentzianModel(prefix = 'G_')

        ## CONVERT HEIGHTS TO AMPLITUDES ##
        if fit_style == 0:
            D1_amplitude = D1_height * np.pi * D1_sigma
            D1_amp_lim_high = D1_height_lim_high * np.pi * D1_sigma
            D1_amp_lim_low = D1_height_lim_low * np.pi * D1_sigma
            D2_amplitude = D2_height * np.pi * D2_sigma
            D2_amp_lim_high = D2_height_lim_high * np.pi * D2_sigma
            D2_amp_lim_low = D2_height_lim_low * np.pi * D2_sigma
            D3_amplitude = D3_height * np.pi * D3_sigma
            D3_amp_lim_high = D3_height_lim_high * np.pi * D3_sigma
            D3_amp_lim_low = D3_height_lim_low * np.pi * D3_sigma
            D4_amplitude = D4_height * np.pi * D4_sigma
            D4_amp_lim_high = D4_height_lim_high * np.pi * D4_sigma
            D4_amp_lim_low = D4_height_lim_low * np.pi * D4_sigma
            G_amplitude = G_height * np.pi * G_sigma
            G_amp_lim_high = G_height_lim_high * np.pi * G_sigma
            G_amp_lim_low = G_height_lim_low * np.pi * G_sigma
        elif fit_style == 1:
            fitStyle1Term = np.sqrt(2*np.pi)
            D1_amplitude = D1_height * fitStyle1Term * D1_sigma
            D1_amp_lim_high = D1_height_lim_high * fitStyle1Term * D1_sigma
            D1_amp_lim_low = D1_height_lim_low * fitStyle1Term * D1_sigma
            D2_amplitude = D2_height * fitStyle1Term * D2_sigma
            D2_amp_lim_high = D2_height_lim_high * fitStyle1Term * D2_sigma
            D2_amp_lim_low = D2_height_lim_low * fitStyle1Term * D2_sigma
            D3_amplitude = D3_height * fitStyle1Term * D3_sigma
            D3_amp_lim_high = D3_height_lim_high * fitStyle1Term * D3_sigma
            D3_amp_lim_low = D3_height_lim_low * fitStyle1Term * D3_sigma
            D4_amplitude = D4_height * fitStyle1Term * D4_sigma
            D4_amp_lim_high = D4_height_lim_high * fitStyle1Term * D4_sigma
            D4_amp_lim_low = D4_height_lim_low * fitStyle1Term * D4_sigma
            G_amplitude = G_height * np.pi * G_sigma
            G_amp_lim_high = G_height_lim_high * fitStyle1Term * G_sigma
            G_amp_lim_low = G_height_lim_low * fitStyle1Term * G_sigma

        ## GENERATE INITIAL MODEL VALUES ##
        pars = D1.make_params(amplitude = D1_amplitude, center = D1_center, sigma = D1_sigma)
        pars.update(D1.make_params())
        pars['D1_amplitude'].set(D1_amplitude, min = D1_amp_lim_low, max = D1_amp_lim_high)
        pars['D1_center'].set(D1_center, min = D1_center_lim_low, max = D1_center_lim_high)
        # pars['D1_center'].set(D1_center, vary = False)
        pars['D1_sigma'].set(D1_sigma, max = D1_sigma_lim_high)
        pars.update(D2.make_params())
        pars['D2_amplitude'].set(D2_amplitude, min = D2_amp_lim_low, max = D2_amp_lim_high)
        # pars['D2_center'].set(D2_center, min = D2_center_lim_low, max = D2_center_lim_high)
        pars['D2_center'].set(D2_center, vary = False)
        # pars['D2_sigma'].set(D2_sigma, min = D2_sigma_lim_low, max = D2_sigma_lim_high)
        pars['D2_sigma'].set(D2_sigma, vary = False)
        pars.update(D3.make_params())
        pars['D3_amplitude'].set(D3_amplitude, min = D3_amp_lim_low, max = D3_amp_lim_high)
        # pars['D3_center'].set(D3_center, min = D3_center_lim_low, max = D3_center_lim_high)
        pars['D3_center'].set(D3_center, vary = False)
        # pars['D3_sigma'].set(D3_sigma, min = D3_sigma_lim_low, max = D3_sigma_lim_high)
        pars['D3_sigma'].set(D3_sigma, vary = False)
        pars.update(D4.make_params())
        pars['D4_amplitude'].set(D4_amplitude, min = D4_amp_lim_low, max = D4_amp_lim_high)
        # pars['D4_center'].set(D4_center, min = D4_center_lim_low, max = D4_center_lim_high)
        pars['D4_center'].set(D4_center, vary = False)
        # pars['D4_sigma'].set(D4_sigma, min = D4_sigma_lim_low, max = D4_sigma_lim_high)
        pars['D4_sigma'].set(D4_sigma, vary = False)
        if int(self.withGcheck.checkState()) == 2:
            pars.update(G.make_params())
            pars['G_amplitude'].set(G_amplitude, min = G_amp_lim_low, max = G_amp_lim_high)
            pars['G_center'].set(G_center, min = G_center_lim_low, max = G_center_lim_high)
            # pars['G_sigma'].set(G_sigma, min = G_sigma_lim_low, max = G_sigma_lim_high)
            pars['G_sigma'].set(G_sigma, vary = False)

        ## MODEL FITTING ##
        if int(self.withGcheck.checkState()) == 0:
            mod = D1 + D2 + D3 + D4
        if int(self.withGcheck.checkState()) == 2:
            mod = D1 + D2 + D3 + D4 + G
        out_1 = mod.fit(y, pars, x=x)
        if initial == False:
            comps = out_1.eval_components(x=np.array(x))
            D1_fwhm = out_1.values.get('D1_fwhm')
            # print('D1_fwhm = ', D1_fwhm)
            # print('Highest Exposed Temp Would Be: ', -2.15 * D1_fwhm + 478)

            ## CALCULATE r2 TERM ##
            numerator_sum = 0
            denominator_sum = 0
            for i in range(len(x)):
                numerator_sum += ( out_1.best_fit[i] - y[i] )**2
                denominator_sum += ( y[i] - np.mean(y) )**2
            r_squared = 1 - ( numerator_sum / denominator_sum )
            print('r squared :', r_squared)

        ## APPEND INFO ##
        if append == True:
            comps = out_1.eval_components(x=np.array(x))
            D1_fwhm = out_1.values.get('D1_fwhm')
            filename = self.nameGet()
            temp = -2.15 * D1_fwhm + 478
            print(str(filename) + ',' + str(D1_fwhm) + ',' + str(temp) + ',' + str(fit_style) + ',' + str(ratio) + ',' + str(r_squared))
            f = open('information.txt', 'a')
            f.write(str(filename) + ',' + str(D1_fwhm) + ',' + str(temp) + ',' + str(fit_style) + ',' + str(ratio) + ',' + str(r_squared) + '\n')
            f.close()

        ## PLOT ##
        if image == True:
            ax = plt.subplots(figsize = (10,5))
            plt.plot(x, y, 'b')
            plt.plot(x, comps['D1_'], '--', label = 'D1')
            plt.plot(x, comps['D2_'], '--', label = 'D2')
            plt.plot(x, comps['D3_'], '--', label = 'D3')
            plt.plot(x, comps['D4_'], '--', label = 'D4')
            if int(self.withGcheck.checkState()) == 2:
                plt.plot(x, comps['G_'], '--', label = 'G')
            plt.plot(x, out_1.best_fit, 'r-', label = 'best fit')
            plt.legend()
            plt.show()
        elif image == False:

            ## ADD LEGEND ##
            legend = self.graphWidget.addLegend()

            ## CLEAR OLD ##
            self.graphWidget.clear()

            ## PLOT DATA ##
            pen = pg.mkPen(color=(0, 0, 139))
            D1_colour = pg.mkPen(color=(0, 128, 255))
            D2_colour = pg.mkPen(color=(255, 153, 51))
            D3_colour = pg.mkPen(color=(0, 255, 0))
            D4_colour = pg.mkPen(color=(255, 51, 51))
            if int(self.withGcheck.checkState()) == 2:
                G_colour = pg.mkPen(color=(178, 102, 255))
            best_fit_colour = pg.mkPen(color=(0, 0, 255))
            dataPlot = self.graphWidget.plot(x, y, pen = pen)
            if initial == False:
                D1Plot = self.graphWidget.plot(x, comps['D1_'], pen = D1_colour)
                D2Plot = self.graphWidget.plot(x, comps['D2_'], pen = D2_colour)
                D3Plot = self.graphWidget.plot(x, comps['D3_'], pen = D3_colour)
                D4Plot = self.graphWidget.plot(x, comps['D4_'], pen = D4_colour)
                if int(self.withGcheck.checkState()) == 2:
                    GPlot = self.graphWidget.plot(x, comps['G_'], pen = G_colour)
                bestPlot = self.graphWidget.plot(x, out_1.best_fit, pen = best_fit_colour)
                legend.addItem(dataPlot, name = 'Data')
                legend.addItem(D1Plot, name = 'D1')
                legend.addItem(D2Plot, name = 'D2')
                legend.addItem(D3Plot, name = 'D3')
                legend.addItem(D4Plot, name = 'D4')
                if int(self.withGcheck.checkState()) == 2:
                    legend.addItem(GPlot, name = 'G')
            if initial == True:
                InitColour = pg.mkPen(color=(0, 0, 0))
                InitPlot = self.graphWidget.plot(x, out_1.init_fit, pen = InitColour)
                legend.addItem(InitPlot, name = 'Initial')
            if auto == True:
                return r_squared

    def peakHeightAdjust(self, peak_type, direction, limit):

        if peak_type == 'D4':
            if limit == 'high':
                D4_height = int(self.D4_height_lim.text())
            if limit == 'low':
                D4_height = int(self.D4_height_lim_low.text())
            if direction == 'up':
                D4_height += 100
            if direction == 'down':
                D4_height -= 100
            if limit == 'high':
                self.D4_height_lim.setValue(D4_height)
            if limit == 'low':
                self.D4_height_lim_low.setValue(D4_height)
        if peak_type == 'D1':
            if limit == 'high':
                D1_height = int(self.D1_height_lim.text())
            if limit == 'low':
                D1_height = int(self.D1_height_lim_low.text())
            if direction == 'up':
                D1_height += 100
            if direction == 'down':
                D1_height -= 100
            if limit == 'high':
                self.D1_height_lim.setValue(D1_height)
            if limit == 'low':
                self.D1_height_lim_low.setValue(D1_height)
        if peak_type == 'D3':
            if limit == 'high':
                D3_height = int(self.D3_height_lim.text())
            if limit == 'low':
                D3_height = int(self.D3_height_lim_low.text())
            if direction == 'up':
                D3_height += 100
            if direction == 'down':
                D3_height -= 100
            if limit == 'high':
                self.D3_height_lim.setValue(D3_height)
            if limit == 'low':
                self.D3_height_lim_low.setValue(D3_height)
        if peak_type == 'G':
            if limit == 'high':
                G_height = int(self.G_height_lim.text())
            if limit == 'low':
                G_height = int(self.G_height_lim_low.text())
            if direction == 'up':
                G_height += 100
            if direction == 'down':
                G_height -= 100
            if limit == 'high':
                self.G_height_lim.setValue(G_height)
            if limit == 'low':
                self.G_height_lim_low.setValue(G_height)
        if peak_type == 'D2':
            if limit == 'high':
                D2_height = int(self.D2_height_lim.text())
            if limit == 'low':
                D2_height = int(self.D2_height_lim_low.text())
            if direction == 'up':
                D2_height += 100
            if direction == 'down':
                D2_height -= 100
            if limit == 'high':
                self.D2_height_lim.setValue(D2_height)
            if limit == 'low':
                self.D2_height_lim_low.setValue(D2_height)

    def sigmaAdjust(self, peak, direction):

        ## READ INIT SIGMA ##
        if peak == 'D4':
            sig_init = int(self.D4_sigma.text())
            ## ALTER SIGMA ##
            if direction == 'up':
                sig_init += 5
            elif direction == 'down':
                sig_init -= 5
            self.D4_sigma.setValue(sig_init)
        if peak == 'D1':
            sig_init = int(self.D1_sigma.text())
            ## ALTER SIGMA ##
            if direction == 'up':
                sig_init += 5
            elif direction == 'down':
                sig_init -= 5
            self.D1_sigma.setValue(sig_init)
        if peak == 'D3':
            sig_init = int(self.D3_sigma.text())
            ## ALTER SIGMA ##
            if direction == 'up':
                sig_init += 5
            elif direction == 'down':
                sig_init -= 5
            self.D3_sigma.setValue(sig_init)
        if peak == 'G':
            sig_init = int(self.G_sigma.text())
            ## ALTER SIGMA ##
            if direction == 'up':
                sig_init += 5
            elif direction == 'down':
                sig_init -= 5
            self.G_sigma.setValue(sig_init)
        if peak == 'D2':
            sig_init = int(self.D2_sigma.text())
            ## ALTER SIGMA ##
            if direction == 'up':
                sig_init += 5
            elif direction == 'down':
                sig_init -= 5
            self.D2_sigma.setValue(sig_init)

    def centerAdjust(self, peak, direction):

        if peak == 'D4':
            center = int(self.D4_center.text())
            if direction == 'up':
                center += 2
            if direction == 'down':
                center -= 2
            self.D4_center.setValue(center)
        if peak == 'D1':
            center = int(self.D1_center.text())
            if direction == 'up':
                center += 2
            if direction == 'down':
                center -= 2
            self.D1_center.setValue(center)
        if peak == 'D3':
            center = int(self.D3_center.text())
            if direction == 'up':
                center += 2
            if direction == 'down':
                center -= 2
            self.D3_center.setValue(center)
        if peak == 'G':
            center = int(self.G_center.text())
            if direction == 'up':
                center += 2
            if direction == 'down':
                center -= 2
            self.G_center.setValue(center)
        if peak == 'D2':
            center = int(self.D2_center.text())
            if direction == 'up':
                center += 2
            if direction == 'down':
                center -= 2
            self.D2_center.setValue(center)

    def autoFit(self):

        if int(self.withGcheck.checkState()) == 0:
            names = ['D4','D1', 'D3', 'D2']
        elif int(self.withGcheck.checkState()) == 2:
            names = ['D4','D1', 'D3', 'G', 'D2']

        for i in range(len(names)):

            ## GET R squared ##
            center_init = self.mainFitter(auto = True)

            ## INCREASE CENTER ##
            self.centerAdjust(peak = names[i], direction = 'up')
            sig_new = self.mainFitter(auto = True)

            ## COMPARE ##
            if center_init > sig_new:
                self.centerAdjust(peak = names[i], direction = 'down')
                self.centerAdjust(peak = names[i], direction = 'down')
                sig_new = self.mainFitter(auto = True)
                if center_init > sig_new:
                    self.centerAdjust(peak = names[i], direction = 'up')
                elif center_init < sig_new:
                    while center_init < sig_new:
                        print('center adjusting :' + names[i])
                        center_init = sig_new
                        self.centerAdjust(peak = names[i], direction = 'down')
                        sig_new = self.mainFitter(auto = True)
                        if center_init > sig_new:
                            self.centerAdjust(peak = names[i], direction = 'up')
            elif center_init < sig_new:
                ## FIND BEST ##
                while center_init < sig_new:
                    print('center adjusting :' + names[i])
                    center_init = sig_new
                    self.centerAdjust(peak = names[i], direction = 'up')
                    sig_new = self.mainFitter(auto = True)
                    if center_init > sig_new:
                        self.centerAdjust(peak = names[i], direction = 'down')

        for i in range(len(names)):
            ## GET R squared ##
            sig_initR = self.mainFitter(auto = True)

            ## INCREASE D4 SIGMA ##
            self.sigmaAdjust(peak = names[i], direction = 'up')
            sig_new = self.mainFitter(auto = True)
        ## COMPARE R SQUARED WITH HIGHER AND LOWER SIGMAS ##
            if sig_initR > sig_new:
                self.sigmaAdjust(peak = names[i], direction = 'down')
                self.sigmaAdjust(peak = names[i], direction = 'down')
                sig_new = self.mainFitter(auto = True)
                if sig_initR > sig_new:
                    self.sigmaAdjust(peak = names[i], direction = 'up')
                elif sig_initR < sig_new:
                    while sig_initR < sig_new:
                        print('sigma adjusting :' + names[i])
                        sig_initR = sig_new
                        self.sigmaAdjust(peak = names[i], direction = 'down')
                        sig_new = self.mainFitter(auto = True)
                        if sig_initR > sig_new:
                            self.sigmaAdjust(peak = names[i], direction = 'up')
            elif sig_initR < sig_new:
                ## FIND BEST ##
                while sig_initR < sig_new:
                    print('sigma adjusting :' + names[i])
                    sig_initR = sig_new
                    self.sigmaAdjust(peak = names[i], direction = 'up')
                    sig_new = self.mainFitter(auto = True)
                    if sig_initR > sig_new:
                        self.sigmaAdjust(peak = names[i], direction = 'down')

        for i in range(len(names)):
        ## READ D4 HEIGHT, SUBTRACT 100, RUN FIT AGAIN ##
            self.peakHeightAdjust(peak_type = names[i], direction = 'down', limit = 'low')
            D4_Rlow = self.mainFitter(auto = True)
            if D4_Rlow < sig_new or D4_Rlow == sig_new:
                self.peakHeightAdjust(peak_type = names[i], direction = 'up', limit = 'low')
            if D4_Rlow > sig_new:
                while D4_Rlow > sig_new:
                    sig_new = D4_Rlow
                    self.peakHeightAdjust(peak_type = names[i], direction = 'down', limit = 'low')
                    D4_Rlow = self.mainFitter(auto = True)
                    if D4_Rlow < sig_new:
                        self.peakHeightAdjust(peak_type = names[i], direction = 'up', limit = 'low')
                        # continue
            ## UPPER LIMIT ##
            self.peakHeightAdjust(peak_type = names[i], direction = 'up', limit = 'high')
            D4_Rlow = self.mainFitter(auto = True)
            if D4_Rlow < sig_new or D4_Rlow == sig_new:
                self.peakHeightAdjust(peak_type = names[i], direction = 'down', limit = 'high')
            if D4_Rlow > sig_new:
                while D4_Rlow > sig_new:
                    sig_new = D4_Rlow
                    self.peakHeightAdjust(peak_type = names[i], direction = 'up', limit = 'high')
                    D4_Rlow = self.mainFitter(auto = True)
                    if D4_Rlow < sig_new:
                        self.peakHeightAdjust(peak_type = names[i], direction = 'down', limit = 'high')
                        # continue

#--------------------------------------------------------------#   

## INITIALIZE APP WHEN FILE RUNS ##
if __name__ == '__main__':
    
    f = open('tmp1','w')
    f.write('.')
    f.close()

    f = open('tmp2','w')
    f.write('.')
    f.close()

    f = open('tmp3','w')
    f.write('.')
    f.close()

    f = open('tmp4','w')
    f.write('.')
    f.close()

    f = open('tmp5','w')
    f.write('.')
    f.close()

    f = open('tmp6','w')
    f.write('.')
    f.close()

    f = open('tmp7','w')
    f.write('.')
    f.close()

    f = open('tmp8','w')
    f.write('.')
    f.close()

    f = open('dataTrimmed.txt', 'w')
    f.truncate()
    f.close()

    f = open('click_coords.txt', 'w')
    f.truncate()
    f.close()

    f = open('base_click_coords.txt', 'w')
    f.truncate()
    f.close()

    f = open('dataTrimmed.txt', 'w')
    f.truncate()
    f.close()

    f = open('centers', 'w')
    f.truncate()
    f.close()

    f = open('heights', 'w')
    f.truncate()
    f.close()

    f = open('sigmas', 'w')
    f.truncate()
    f.close()

    f = open('halfmax', 'w')
    f.truncate()
    f.close()

    app = QtWidgets.QApplication(sys.argv)

    mainWindow = QtWidgets.QMainWindow()

    ui = Ui_MainWindow()

    ui.setupUi(mainWindow)

    mainWindow.show()

    sys.exit(app.exec_())
    
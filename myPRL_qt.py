import sys
import numpy as np
from scipy.optimize import minimize
from PyQt5.QtWidgets import (QApplication, 
							QWidget, 
							QMainWindow, 
							QPushButton, 
							QComboBox, 
							QLabel,
							QLineEdit,
							QVBoxLayout,
							QHBoxLayout,
							QFormLayout,
							QGridLayout,
							QFrame,
							QSpinBox,
							QDoubleSpinBox)

import Pcalib


class MyQSeparator(QFrame):
	def __init__(self):
		super().__init__()
		self.setFrameShape(QFrame.HLine)
		self.setFrameShadow(QFrame.Sunken)

class MyPRLMain(QMainWindow):
	def __init__(self):
		super().__init__()
	
		self.setWindowTitle("myPRL qt")
		self.resize(300, 550)

		# useful dict
		self.calibdict = {'Ruby':               ['Ruby2020','test'],
						  'Samarium Borate':    ['test1','test2'],
						  'Diamond Raman Edge': ['test3','test4'],
						  'cBN Raman':          ['test12', 'test23']}

		# large layout containing all widgets
		layout = QVBoxLayout()

		# load layout 
		load_layout = QVBoxLayout()

		self.load_button = QPushButton('load')
		self.load_last_button = QPushButton('load last')
		
		load_layout.addWidget(self.load_button)
		load_layout.addWidget(self.load_last_button)

		# directory layout inside load layout
		dir_layout = QHBoxLayout()
		dir_label = QLabel('directory:')
		self.dir_lineedit = QLineEdit()
		self.dir_button = QPushButton('Browse')
		self.dir_button.setMinimumWidth(60)

		dir_layout.addWidget(dir_label,1)
		dir_layout.addWidget(self.dir_lineedit,10)
		dir_layout.addWidget(self.dir_button,1)

		load_layout.addLayout(dir_layout)

		self.plot_button = QPushButton('Plot')
		load_layout.addWidget(self.plot_button)

		layout.addLayout(load_layout)

		# separator
		layout.addStretch()
		layout.addWidget(MyQSeparator())
		layout.addStretch()

		# data form layout
		data_form = QFormLayout()

		self.lambda_spinbox = QDoubleSpinBox()
		self.lambda0_spinbox = QDoubleSpinBox()

		self.T_spinbox = QDoubleSpinBox()
		self.T0_spinbox = QDoubleSpinBox()

		self.lambda_spinbox.setDecimals(2)
		self.lambda0_spinbox.setDecimals(2)
		self.lambda_spinbox.setRange(0, 1e6)
		self.lambda0_spinbox.setRange(0, 1e6)
		self.lambda_spinbox.setSingleStep(.01)
		self.lambda0_spinbox.setSingleStep(.01)

		self.T_spinbox.setDecimals(0)
		self.T0_spinbox.setDecimals(0)
		self.T_spinbox.setRange(0, 1e6)
		self.T0_spinbox.setRange(0, 1e6)
		self.T_spinbox.setSingleStep(1)
		self.T0_spinbox.setSingleStep(1)


		self.lambda_spinbox.setValue(694.50)
		self.T_spinbox.setValue(298)
		self.lambda0_spinbox.setValue(694.28)
		self.T0_spinbox.setValue(298)

		
		data_form.addRow('lambda (nm)', self.lambda_spinbox)
		data_form.addRow('T (K)', self.T_spinbox)
		data_form.addRow('lambda0 (nm)', self.lambda0_spinbox)
		data_form.addRow('T0 (K)', self.T0_spinbox)

		layout.addLayout(data_form)

		# separator
		layout.addStretch()
		layout.addWidget(MyQSeparator())
		layout.addStretch()

		# pressure layout
		pressure_layout = QVBoxLayout()

		self.pressure_spinbox = QDoubleSpinBox()
		self.Pm_spinbox = QDoubleSpinBox()

		pressure_form = QFormLayout()
		pressure_form.addRow('P (GPa)', self.pressure_spinbox)
		pressure_form.addRow('Pm (bar)', self.Pm_spinbox)
	
		self.pressure_spinbox.setDecimals(2)
		self.pressure_spinbox.setRange(-1e6, 1e6)
		self.pressure_spinbox.setSingleStep(.1)

		self.Pm_spinbox.setDecimals(2)
		self.Pm_spinbox.setRange(-1e6, 1e6)
		self.Pm_spinbox.setSingleStep(.1)

		pressure_layout.addLayout(pressure_form)

		# Pm vs. P sublayout inside pressure layout
		PmP_layout = QHBoxLayout()

		self.add_PmP_button = QPushButton('add')
		self.add_PmP_button.setMinimumWidth(50)
		self.PmP_button = QPushButton('P vs Pm')

		PmP_layout.addWidget(self.add_PmP_button,1)		
		PmP_layout.addWidget(self.PmP_button,5)

		pressure_layout.addLayout(PmP_layout)
	
		layout.addLayout(pressure_layout)

		# separator
		layout.addStretch()
		layout.addWidget(MyQSeparator())
		layout.addStretch()

		# scales layout
		scales_layout = QGridLayout()
		scales_layout.setColumnStretch(0, 1)
		scales_layout.setColumnStretch(1, 10)

		self.calibrant_combo = QComboBox()
		self.calibration_combo = QComboBox()
		self.temperaturecor_combo = QComboBox()

		self.calibrant_combo.addItem('Ruby')
		self.calibrant_combo.addItem('Samarium Borate')
		self.calibrant_combo.addItem('Diamond Raman Edge')
		self.calibrant_combo.addItem('cBN Raman')



		scales_layout.addWidget(QLabel("Calibrant"), 0, 0)
		scales_layout.addWidget(self.calibrant_combo, 0, 1)
		scales_layout.addWidget(QLabel("Calibration"), 1, 0)
		scales_layout.addWidget(self.calibration_combo, 1, 1)
		scales_layout.addWidget(QLabel("Temperature cor."), 2, 0)
		scales_layout.addWidget(self.temperaturecor_combo, 2, 1)

		layout.addLayout(scales_layout)

		# vcontainer is the central widget for the MainWindow
		vcontainer = QWidget()
		vcontainer.setLayout(layout)
		self.setCentralWidget(vcontainer)	
		#self.setLayout(layout) #only if inherits from QWidget/not QMainWindow


		# Connects

		self.lambda_spinbox.valueChanged.connect(self.evaluate)
		self.T_spinbox.valueChanged.connect(self.evaluate)
		self.lambda0_spinbox.valueChanged.connect(self.evaluate)
		self.T0_spinbox.valueChanged.connect(self.evaluate)

		self.pressure_spinbox.valueChanged.connect(self.invevaluate)

		self.calibrant_combo.currentIndexChanged.connect(self.updatecalib)


		# evaluate at __init__ (opening)
		self.updatecalib(self)
		self.evaluate(self)


	def evaluate(self, s):
		if self.pressure_spinbox.hasFocus() == False:
			_l = self.lambda_spinbox.value()
			_l0 = self.lambda0_spinbox.value()
			_T = self.T_spinbox.value()
			_T0 = self.T0_spinbox.value()

			if self.calibrant_combo.currentText() == 'Ruby':
				self.pressure_spinbox.setValue(
							Pcalib.Pruby2020(_l, _l0, _T, _T0))

	def invevaluate(self, s):
		if self.pressure_spinbox.hasFocus() == True:
			_p = self.pressure_spinbox.value()
			_l0 = self.lambda0_spinbox.value()
			_T = self.T_spinbox.value()
			_T0 = self.T0_spinbox.value()

			self.lambda_spinbox.setValue(
						Pcalib.invPruby2020(_p, _l0, _T, _T0))


	def updatecalib(self, index):
		self.calibration_combo.clear()
		self.calibration_combo.addItems(
			self.calibdict[self.calibrant_combo.currentText()])

app = QApplication(sys.argv)

main = MyPRLMain()
main.show()

app.exec()
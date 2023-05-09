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
							 QDoubleSpinBox,
							 QStackedWidget)

# my modules
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
		self.resize(250, 550)

		# calibrations dict
		self.calibdict = {'Ruby':               ['Ruby2020'],
						  'Samarium Borate':    ['Datchi1997'],
						  'Diamond Raman Edge': [],
						  'cBN Raman':          ['Datchi2007']}

##############################################################################

		# large layout containing all widgets
		layout = QVBoxLayout()

##############################################################################

		self.load_button = QPushButton('load')
		self.load_last_button = QPushButton('load last')

		# directory layout inside load layout
		dir_label = QLabel('directory:')
		self.dir_lineedit = QLineEdit()
		self.dir_lineedit.setMinimumWidth(60)
		self.dir_button = QPushButton('Browse')
		self.dir_button.setMinimumWidth(60)

		dir_layout = QHBoxLayout()
		dir_layout.addWidget(dir_label,1)
		dir_layout.addWidget(self.dir_lineedit,10)
		dir_layout.addWidget(self.dir_button,1)

		self.plot_button = QPushButton('Plot')

		# load layout 
		load_layout = QVBoxLayout()

		load_layout.addWidget(self.load_button)
		load_layout.addWidget(self.load_last_button)
		load_layout.addLayout(dir_layout)
		load_layout.addWidget(self.plot_button)

##############################################################################

		self.lam_spinbox = QDoubleSpinBox()
		self.lam0_spinbox = QDoubleSpinBox()
		self.T_spinbox = QDoubleSpinBox()
		self.T0_spinbox = QDoubleSpinBox()

		self.lam_spinbox.setDecimals(2)
		self.lam_spinbox.setRange(0, 1e6)
		self.lam_spinbox.setSingleStep(.01)
		self.lam0_spinbox.setDecimals(2)
		self.lam0_spinbox.setRange(0, 1e6)
		self.lam0_spinbox.setSingleStep(.01)

		self.T_spinbox.setDecimals(0)
		self.T_spinbox.setRange(0, 1e6)
		self.T_spinbox.setSingleStep(1)
		self.T0_spinbox.setDecimals(0)
		self.T0_spinbox.setRange(0, 1e6)
		self.T0_spinbox.setSingleStep(1)
		
		self.lam_label = QLabel('lambda (nm)')
		self.lam0_label = QLabel('lambda0 (nm)')

		# data form
		data_form = QFormLayout()
		data_form.addRow(self.lam_label, self.lam_spinbox)
		data_form.addRow('T (K)', self.T_spinbox)
		data_form.addRow(self.lam0_label, self.lam0_spinbox)
		data_form.addRow('T0 (K)', self.T0_spinbox)

##############################################################################


		self.P_spinbox = QDoubleSpinBox()
		self.Pm_spinbox = QDoubleSpinBox()

		pressure_form = QFormLayout()
		pressure_form.addRow('P (GPa)', self.P_spinbox)
		pressure_form.addRow('Pm (bar)', self.Pm_spinbox)
	
		self.P_spinbox.setDecimals(2)
		self.P_spinbox.setRange(-1e6, 1e6)
		self.P_spinbox.setSingleStep(.1)

		self.Pm_spinbox.setDecimals(2)
		self.Pm_spinbox.setRange(-1e6, 1e6)
		self.Pm_spinbox.setSingleStep(.1)

		# Pm vs. P sublayout inside pressure layout
		PmP_layout = QHBoxLayout()

		self.add_PmP_button = QPushButton('add')
		self.add_PmP_button.setMinimumWidth(50)
		self.PmP_button = QPushButton('P vs Pm')

		PmP_layout.addWidget(self.add_PmP_button,1)		
		PmP_layout.addWidget(self.PmP_button,5)

		# pressure layout
		pressure_layout = QVBoxLayout()
		pressure_layout.addLayout(pressure_form)
		pressure_layout.addLayout(PmP_layout)

##############################################################################

		self.calibrant_combo = QComboBox()
		self.calibration_combo = QComboBox()
		self.temperaturecor_combo = QComboBox()

		self.calibrant_combo.setMinimumWidth(100)
		self.calibration_combo.setMinimumWidth(100)
		self.temperaturecor_combo.setMinimumWidth(100)

		self.calibrant_combo.addItem('Ruby')
		self.calibrant_combo.addItem('Samarium Borate')
		self.calibrant_combo.addItem('Diamond Raman Edge')
		self.calibrant_combo.addItem('cBN Raman')

		# scales layout
		scales_layout = QGridLayout()
		scales_layout.setColumnStretch(0, 1)
		scales_layout.setColumnStretch(1, 10)
		scales_layout.addWidget(QLabel("Calibrant"), 0, 0)
		scales_layout.addWidget(self.calibrant_combo, 0, 1)
		scales_layout.addWidget(QLabel("Calibration"), 1, 0)
		scales_layout.addWidget(self.calibration_combo, 1, 1)
		scales_layout.addWidget(QLabel("Temperature cor."), 2, 0)
		scales_layout.addWidget(self.temperaturecor_combo, 2, 1)


##############################################################################
	
		layout.addLayout(load_layout)

		layout.addStretch()
		layout.addWidget(MyQSeparator())
		layout.addStretch()

		layout.addLayout(data_form)

		layout.addStretch()
		layout.addWidget(MyQSeparator())
		layout.addStretch()
		
		layout.addLayout(pressure_layout)

		layout.addStretch()
		layout.addWidget(MyQSeparator())
		layout.addStretch()

		layout.addLayout(scales_layout)

		# vcontainer is the central widget for the MainWindow
		vcontainer = QWidget()
		vcontainer.setLayout(layout)
		self.setCentralWidget(vcontainer)	
		#self.setLayout(layout) #only if inherits from QWidget/not QMainWindow



##############################################################################
		
		# init some values:
		self.lam_spinbox.setValue(694.28)
		self.T_spinbox.setValue(298)
		self.T0_spinbox.setValue(298)
		
		# Connects
		self.lam_spinbox.valueChanged.connect(self.evaluate)
		self.lam0_spinbox.valueChanged.connect(self.evaluate)
		self.T_spinbox.valueChanged.connect(self.evaluate)
		self.T0_spinbox.valueChanged.connect(self.evaluate)

		self.P_spinbox.valueChanged.connect(self.evaluate)

		self.calibrant_combo.currentIndexChanged.connect(self.updatecalib)

		# evaluate is called through updatecalib
		self.updatecalib(self)
		


	def evaluate(self, s):
		if not self.P_spinbox.hasFocus():
			lam = self.lam_spinbox.value()
			lam0  = self.lam0_spinbox.value()
			T = self.T_spinbox.value()
			T0 = self.T0_spinbox.value()

			if self.calibration_combo.currentText() == 'Ruby2020':
	
				P = Pcalib.Pruby2020(lam, lam0, T, T0)

			elif self.calibration_combo.currentText() == 'Datchi1997':
				
				P = Pcalib.PsamDatchi1997(lam, lam0, T, T0)

			elif self.calibration_combo.currentText() == 'Datchi2007':
				
				P = -12
	
			self.P_spinbox.setValue(P)

		else: 
			# inverse evaluation
			P = self.P_spinbox.value()
			lam0  = self.lam0_spinbox.value()
			T = self.T_spinbox.value()
			T0 = self.T0_spinbox.value()

			if self.calibration_combo.currentText() == 'Ruby2020':
	
				lam = Pcalib.invPruby2020(P, lam0, T, T0)

			elif self.calibration_combo.currentText() == 'Datchi1997':
				
				lam = Pcalib.invPsamDatchi1997(P, lam0, T, T0)
	
			self.lam_spinbox.setValue(lam)		

	def updatecalib(self, s):

		self.calibration_combo.clear()
		self.calibration_combo.addItems(
			self.calibdict[self.calibrant_combo.currentText()])

		# reset lam0. Change labels. Evaluate is called.
		if self.calibrant_combo.currentText() == 'Ruby':
			self.lam_label.setText('lambda (nm)')
			self.lam0_label.setText('lambda0 (nm)')

			self.lam0_spinbox.setValue(694.28)

		if self.calibrant_combo.currentText() == 'Samarium Borate':
			self.lam_label.setText('lambda (nm)')
			self.lam0_label.setText('lambda0 (nm)')
			
			self.lam0_spinbox.setValue(685.41)

		if self.calibrant_combo.currentText() == 'cBN Raman':
			self.lam_label.setText('nu (cm-1)')
			self.lam0_label.setText('nu0 (cm-1)')

			self.lam0_spinbox.setValue(1054.0)


app = QApplication(sys.argv)

main = MyPRLMain()
main.show()

app.exec()
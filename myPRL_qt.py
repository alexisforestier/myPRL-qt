import sys
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from PyQt5.QtGui import QColor
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
from PyQt5.QtCore import QLocale

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

		# dot as decimal separator in the whole app
		self.setLocale(QLocale(QLocale.C))

		self.setWindowTitle("myPRL qt")
		self.resize(240, 500)

		# calibrations dict
		self.calibrations = {'Ruby2020':
								{'func':Pcalib.Pruby2020,
								 'Tcor':'Datchi2007',
								 'col':'lightcoral',
								 'unit':'nm',
								 'lam_default':694.28,
								 'lam_step':.01},

						     'Samarium Borate Datchi1997':
						     	{'func':Pcalib.PsamDatchi1997,
						     	 'Tcor':'NA',
						     	 'col':'moccasin',
						     	 'unit':'nm',
						     	 'lam_default':685.41,
						     	 'lam_step':.01},

						     'Diamond Raman Edge Akahama2006':
						     	{'func':Pcalib.PAkahama2006,
						     	 'Tcor':'NA',
						     	 'col':'darkgrey',
						     	 'unit':'cm-1',
						     	 'lam_default':1333,
						     	 'lam_step':.1},

						     'cBN Raman Datchi2007': 
						     	{'func':Pcalib.PcBN,
						     	 'Tcor':'Datchi2007',
						     	 'col':'lightblue',
						     	 'unit':'cm-1',
						     	 'lam_default':1054,
						     	 'lam_step':.1}}

		self.data = pd.DataFrame(columns=['lam', 
										  'lam0',
										  'T',
										  'T0',
										  'P',
										  'Pm',
										  'calib'])

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
		self.lam_spinbox.setRange(-np.inf, +np.inf)
		self.lam0_spinbox.setDecimals(2)
		self.lam0_spinbox.setRange(-np.inf, +np.inf)

		self.T_spinbox.setDecimals(0)
		self.T_spinbox.setRange(-np.inf, +np.inf)
		self.T_spinbox.setSingleStep(1)
		self.T0_spinbox.setDecimals(0)
		self.T0_spinbox.setRange(-np.inf, +np.inf)
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
		self.P_spinbox.setRange(-np.inf, np.inf)
		self.P_spinbox.setSingleStep(.1)

		self.Pm_spinbox.setDecimals(2)
		self.Pm_spinbox.setRange(-np.inf, np.inf)
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

		self.calibration_combo = QComboBox()
		temperaturecor_Label0 = QLabel('T correction:')
		self.temperaturecor_Label = QLabel('NA')

		self.calibration_combo.setMinimumWidth(100)

		self.calibration_combo.addItems( self.calibrations.keys() )
		
		for ind in range(len(self.calibrations.keys())):
			k, v = list( self.calibrations.items() )[ind]

			self.calibration_combo.model().item(ind).setBackground(QColor(
				v['col']))

		# scales layout
		scales_layout = QGridLayout()
		scales_layout.setColumnStretch(0, 1)
		scales_layout.setColumnStretch(1, 10)
		scales_layout.addWidget(QLabel("Calibration:"), 0, 0)
		scales_layout.addWidget(self.calibration_combo, 0, 1)
		scales_layout.addWidget(temperaturecor_Label0,  1, 0)
		scales_layout.addWidget(self.temperaturecor_Label,  1, 1)

##############################################################################
	
		layout.addLayout(load_layout)

		layout.addStretch()
		layout.addWidget(MyQSeparator())
		layout.addStretch()

		layout.addLayout(scales_layout)

		layout.addStretch()
		layout.addWidget(MyQSeparator())
		layout.addStretch()

		layout.addLayout(data_form)

		layout.addStretch()
		layout.addWidget(MyQSeparator())
		layout.addStretch()
		
		layout.addLayout(pressure_layout)

		# vcontainer is the central widget for the MainWindow
		vcontainer = QWidget()
		vcontainer.setLayout(layout)
		self.setCentralWidget(vcontainer)	
		#self.setLayout(layout) #only if inherits from QWidget/not QMainWindow


##############################################################################
		
		# init some values:
		self.lam_spinbox.setValue(694.28)
		# lam0 is done through update
		self.T_spinbox.setValue(298)
		self.T0_spinbox.setValue(298)
		
		# Connects
		self.lam_spinbox.valueChanged.connect(self.evaluate)
		self.lam0_spinbox.valueChanged.connect(self.evaluate)
		self.T_spinbox.valueChanged.connect(self.evaluate)
		self.T0_spinbox.valueChanged.connect(self.evaluate)

		self.P_spinbox.valueChanged.connect(self.evaluate)

		self.add_PmP_button.clicked.connect(self.add)

		self.calibration_combo.currentIndexChanged.connect(self.updatecalib)

		# evaluate is called through updatecalib through valuechanged of lam0
		self.updatecalib(self)

	def evaluate(self, s):
		if not self.P_spinbox.hasFocus():

			lam = self.lam_spinbox.value()
			lam0  = self.lam0_spinbox.value()
			T = self.T_spinbox.value()
			T0 = self.T0_spinbox.value()
			cal = self.calibration_combo.currentText()
			calfunc = self.calibrations[cal]['func']

			try:

				P = calfunc(lam, lam0, T, T0)

				self.P_spinbox.setValue(P)
				self.P_spinbox.setStyleSheet("background: #c6fcc5;")
			
			except:	
				
				self.P_spinbox.setStyleSheet("background: #ff7575;")

		else: 
			# inverse evaluation
			P = self.P_spinbox.value()
			lam0  = self.lam0_spinbox.value()
			T = self.T_spinbox.value()
			T0 = self.T0_spinbox.value()
			cal = self.calibration_combo.currentText()
			calfunc = self.calibrations[cal]['func']

			try:
				
				lam = Pcalib.invfuncP(calfunc, P, lam0, T, T0)
	
				self.lam_spinbox.setValue(lam)
				self.lam_spinbox.setStyleSheet("background: #c6fcc5;")
			
			except:
				
				self.lam_spinbox.setStyleSheet("background: #ff7575;")

	def updatecalib(self, s):

		self.temperaturecor_Label.setText(
			self.calibrations[self.calibration_combo.currentText()]['Tcor'])

		col1 = self.calibration_combo.model().item(
		   self.calibration_combo.currentIndex()).background().color().getRgb() 
		self.calibration_combo.setStyleSheet("background-color: rgba{};\
					selection-background-color: k;".format(col1))

		calval = self.calibrations[self.calibration_combo.currentText()]

		if calval['unit'] == 'nm':
			self.lam_label.setText('lambda (nm)')
			self.lam0_label.setText('lambda0 (nm)')

		elif calval['unit'] == 'cm-1':
			self.lam_label.setText('nu (cm-1)')
			self.lam0_label.setText('nu0 (cm-1)')

		self.lam_spinbox.setSingleStep(calval['lam_step'])
		self.lam0_spinbox.setSingleStep(calval['lam_step'])

		self.lam0_spinbox.setValue(calval['lam_default'])

	def add(self, s):

		d_i = {'lam':   self.lam_spinbox.value(),
		       'lam0':  self.lam0_spinbox.value(),
		       'T':     self.T_spinbox.value(),
		       'T0':    self.T0_spinbox.value(),
		       'P':     self.P_spinbox.value(),
		       'Pm':    self.Pm_spinbox.value(),
		       'calib': self.calibration_combo.currentText()}

		self.data = pd.concat([self.data, pd.DataFrame(d_i, 
									index = [len(self.data)+1])])

app = QApplication(sys.argv)

main = MyPRLMain()
main.show()

app.exec()
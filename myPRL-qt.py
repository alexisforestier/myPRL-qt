import sys
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from PyQt5.QtGui import (QColor, 
						QDoubleValidator)
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
							 QTableWidget,
							 QTableWidgetItem,
							 QHeaderView,
							 QItemDelegate,
							 QDoubleSpinBox,
							 QStackedWidget)
from PyQt5.QtCore import QObject, pyqtSignal, QLocale

# myPRL-qt modules:
import HPCalibfuncs
import HPModels



class MyQSeparator(QFrame):
	def __init__(self):
		super().__init__()
		self.setFrameShape(QFrame.HLine)
		self.setFrameShadow(QFrame.Sunken)


#class HPTableWidget(QTableWidget):
#	''' Qt widget class for HPDataTable objects '''
#
#	def __init__(self, HPDataTable):
#		super().__init__()
#
#		
#		self.df = df
#		self.setStyleSheet('font-size: 14px;')
#
#		nrows, ncols = self.df.shape
#
#		self.setColumnCount(ncols)
#		self.setRowCount(nrows)
#
#		self.setHorizontalHeaderLabels( list(self.df.columns) )
#		self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
#
#		# populate
#		for irow in range(self.rowCount()):
#			for icol in range(self.columnCount()):
#				self.setItem(irow, icol, 
#					QTableWidgetItem( str(self.df.iloc[irow,icol]) ))
#
#		self.cellChanged[int,int].connect( self.getfromentry )
#
#	def getfromentry(self, row, col):
#		try:
#			self.df.iloc[row, col] = float( self.item(row, col).text() )
#		except:
#			pass
#
#	def updatetable(self, df):
#		if not df.equals(self.df):
#			# df is the new, self.df is the old
#			nrows, ncols = df.shape
#			self.setRowCount(nrows)
#			
#			# populate
#			for irow in range(self.rowCount()):
#				for icol in range(self.columnCount()):
#					self.setItem(irow, icol, 
#						QTableWidgetItem( str(df.iloc[irow,icol]) ))
#			# updating df
#			self.df = df

#class PressureTableWindow(QWidget):
#	def __init__(self, df):
#		super().__init__()
#
#		self.resize(600,400)
#
#		layout = QVBoxLayout()
#		
#		self.table_widget = DFTableWidget(df)
#		layout.addWidget(self.table_widget)
#		
#		self.setLayout(layout)

class MyPRLMain(QMainWindow):
	def __init__(self):
		super().__init__()

		Ruby2020 = HPModels.HPCalibration(name = 'Ruby2020',
							     func = HPCalibfuncs.Pruby2020,
							     Tcor_name='Datchi 2007',
							     xname = 'lambda',
							     xunit = 'nm',
							     x0default = 694.28,
							     xstep = .01,
							     color = 'lightcoral')

		SamariumDatchi = HPModels.HPCalibration(name = 'Samarium Borate Datchi 1997',
							     	   func = HPCalibfuncs.PsamDatchi1997,
							     	   Tcor_name='NA',
							     	   xname = 'lambda',
							     	   xunit = 'nm',
							     	   x0default = 685.41,
							     	   xstep = .01,
							     	   color = 'moccasin')

		Akahama2006 = HPModels.HPCalibration(name = 'Diamond Raman Edge Akahama 2006',
							     	func = HPCalibfuncs.PAkahama2006,
							     	Tcor_name='NA',
							     	xname = 'nu',
							     	xunit = 'cm-1',
							     	x0default = 1333,
							     	xstep = .1,
							     	color = 'darkgrey')

		cBNDatchi = HPModels.HPCalibration(name = 'cBN Raman Datchi 2007',
							      func = HPCalibfuncs.PcBN,
							      Tcor_name='Datchi 2007',
							      xname = 'nu',
							      xunit = 'cm-1',
							      x0default = 1054,
							      xstep = .1,
							      color = 'lightblue')

		# put all calibrations here
		# keys are names
		self.calibrations = {'Ruby2020': Ruby2020, 
						     'Samarium Borate Datchi 1997': SamariumDatchi,
						     'Diamond Raman Edge Akahama 2006': Akahama2006,
						     'cBN Raman Datchi 2007': cBNDatchi}

		# this will be our initial state
		self.buffer = HPModels.HPData(Pm = 0, 
	     		  					P = 0,
	      		  					x = 694.28,
	       	 	  					T = 298,
	      		  					x0 = 694.28,
	      		  					T0 = 298, 
	      		  					calib = self.calibrations['Ruby2020'],
	      		  					file = 'No')


##############################################################################

		# dot as decimal separator in the whole app
		self.setLocale(QLocale(QLocale.C))

		self.setWindowTitle("myPRL-qt")
		self.resize(240, 250)

		# large layout containing all widgets
		layout = QVBoxLayout()

		self.Pm_spinbox = QDoubleSpinBox()
		self.Pm_spinbox.setObjectName('Pm_spinbox')
		self.Pm_spinbox.setDecimals(2)
		self.Pm_spinbox.setRange(-np.inf, np.inf)
		self.Pm_spinbox.setSingleStep(.1)

		self.P_spinbox = QDoubleSpinBox()
		self.P_spinbox.setObjectName('P_spinbox')
		self.P_spinbox.setDecimals(2)
		self.P_spinbox.setRange(-np.inf, np.inf)
		self.P_spinbox.setSingleStep(.1)

		self.x_spinbox = QDoubleSpinBox()
		self.x_spinbox.setObjectName('x_spinbox')
		self.x_spinbox.setDecimals(2)
		self.x_spinbox.setRange(-np.inf, +np.inf)

		self.T_spinbox = QDoubleSpinBox()
		self.T_spinbox.setObjectName('T_spinbox')
		self.T_spinbox.setDecimals(0)
		self.T_spinbox.setRange(-np.inf, +np.inf)
		self.T_spinbox.setSingleStep(1)

		self.x0_spinbox = QDoubleSpinBox()
		self.x0_spinbox.setObjectName('x0_spinbox')
		self.x0_spinbox.setDecimals(2)
		self.x0_spinbox.setRange(-np.inf, +np.inf)

		self.T0_spinbox = QDoubleSpinBox()
		self.T0_spinbox.setObjectName('T0_spinbox')
		self.T0_spinbox.setDecimals(0)
		self.T0_spinbox.setRange(-np.inf, +np.inf)
		self.T0_spinbox.setSingleStep(1)


		self.calibration_combo = QComboBox()
		self.calibration_combo.setObjectName('calibration_combo')
		self.calibration_combo.setMinimumWidth(100)
		self.calibration_combo.addItems( self.calibrations.keys() )
		
		for k, v in self.calibrations.items():
			ind = self.calibration_combo.findText( k )

			self.calibration_combo.model().item(ind).setBackground(QColor(
				v.color))

		self.x_label = QLabel('lambda (nm)')
		self.x0_label = QLabel('lambda0 (nm)')

		# pressure form
		pressure_form = QFormLayout()
		pressure_form.addRow('Pm (bar)', self.Pm_spinbox)
		pressure_form.addRow('P (GPa)', self.P_spinbox)


		# data form
		data_form = QFormLayout()
		data_form.addRow(self.x_label, self.x_spinbox)
		data_form.addRow('T (K)', self.T_spinbox)
		data_form.addRow(self.x0_label, self.x0_spinbox)
		data_form.addRow('T0 (K)', self.T0_spinbox)


		self.Tcor_Label = QLabel('NA')

		calibration_form = QFormLayout()
		calibration_form.addRow(QLabel('Calibration: '), self.calibration_combo)
		calibration_form.addRow(QLabel('T correction: '), self.Tcor_Label)



		layout.addLayout(pressure_form)

		layout.addStretch()
		layout.addWidget(MyQSeparator())
		layout.addStretch()

		layout.addLayout(data_form)

		layout.addStretch()
		layout.addWidget(MyQSeparator())
		layout.addStretch()
		
		layout.addLayout(calibration_form)



		# vcontainer is the central widget for the MainWindow
		vcontainer = QWidget()
		vcontainer.setLayout(layout)
		self.setCentralWidget(vcontainer)	
		#self.setLayout(layout) #only if inherits from QWidget/not QMainWindow

		# set some initial values 
		self.Pm_spinbox.setValue(self.buffer.Pm)
		self.P_spinbox.setValue(self.buffer.P)
		self.x_spinbox.setValue(self.buffer.x)
		self.T_spinbox.setValue(self.buffer.T)
		self.x0_spinbox.setValue(self.buffer.x0)
		self.T0_spinbox.setValue(self.buffer.T0)
		self.calibration_combo.setCurrentText(self.buffer.calib.name) 
	#	self.file


		# Connects

		self.calibration_combo.currentIndexChanged.connect(self.updatecalib)

		self.Pm_spinbox.valueChanged.connect(self.update)
		self.P_spinbox.valueChanged.connect(self.update)

		self.x_spinbox.valueChanged.connect(self.update)
		self.x0_spinbox.valueChanged.connect(self.update)
		self.T_spinbox.valueChanged.connect(self.update)
		self.T0_spinbox.valueChanged.connect(self.update)


#		self.buffer.changed.connect(self.testreceive)


		# 1 cause it needs a signal
		self.updatecalib(1)	
		# for some reason updatecalib does not call update at __init__
		self.update(1)

#	def testreceive(self, s):
#		print(s)

		# update is called two time, not very good but working
	def update(self, s):

		if self.P_spinbox.hasFocus():
			self.buffer.P = self.P_spinbox.value()
			try:
				self.buffer.invcalcP()
				self.x_spinbox.setValue(self.buffer.x)
				
				self.x_spinbox.setStyleSheet("background: #c6fcc5;") # green
			except:
				self.x_spinbox.setStyleSheet("background: #ff7575;") # red

		else:
			# read everything stupidly
			self.buffer.Pm = self.Pm_spinbox.value()
			self.buffer.x = self.x_spinbox.value()
			self.buffer.T = self.T_spinbox.value()
			self.buffer.x0 = self.x0_spinbox.value()
			self.buffer.T0 = self.T0_spinbox.value()

			try:
				self.buffer.calcP()
				self.P_spinbox.setValue(self.buffer.P)
				
				self.P_spinbox.setStyleSheet("background: #c6fcc5;") # green
			except:
				self.P_spinbox.setStyleSheet("background: #ff7575;") # red
			


	def updatecalib(self, s):

		self.buffer.calib = self.calibrations[ self.calibration_combo.currentText() ]
		newind = self.calibration_combo.currentIndex()

		self.Tcor_Label.setText( self.buffer.calib.Tcor_name )

		col1 = self.calibration_combo.model()\
							.item(newind).background().color().getRgb() 
		self.calibration_combo.setStyleSheet("background-color: rgba{};\
					selection-background-color: k;".format(col1))

		self.x_label.setText('{} ({})'.format(self.buffer.calib.xname, 
													self.buffer.calib.xunit))
		self.x0_label.setText('{}0 ({})'.format(self.buffer.calib.xname, 
													self.buffer.calib.xunit))

		self.x_spinbox.setSingleStep(self.buffer.calib.xstep)
		self.x0_spinbox.setSingleStep(self.buffer.calib.xstep)

		# note that this should call update() but it does not at __init__ !!
		self.x0_spinbox.setValue(self.buffer.calib.x0default)

if __name__ == '__main__':

	app = QApplication(sys.argv)
	
	main = MyPRLMain()
	main.show()
	
	app.exec()
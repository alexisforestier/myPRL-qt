import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from scipy.optimize import minimize
from PyQt5.QtGui import (QColor, 
						QDoubleValidator,
						QKeySequence)
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
							 QStackedWidget,
							 QDesktopWidget,
							 QFileDialog,
							 QShortcut)
from PyQt5.QtCore import (QObject, 
						  pyqtSignal, 
						  QLocale)

# myPRL-qt modules:
import myPRLCalibfuncs
import myPRLModels



class MyQSeparator(QFrame):
	def __init__(self):
		super().__init__()
		self.setFrameShape(QFrame.HLine)
		self.setFrameShadow(QFrame.Sunken)

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi, constrained_layout=True)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class PmPPlotWindow(QWidget):
	def __init__(self, HPDataTable_, calibrations_):
		super().__init__()

		self.setWindowTitle('myPRL-qt plot')

		self.resize(500,400)

		centerPoint = QDesktopWidget().availableGeometry().center()
		thePosition = (centerPoint.x() + 300, centerPoint.y() - 400)
		self.move(*thePosition)

		self.data = HPDataTable_
		self.calibrations = calibrations_

		self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
		self.toolbar = NavigationToolbar(self.canvas, self)		
		layout = QVBoxLayout()

		layout.addWidget(self.toolbar)
		layout.addWidget(self.canvas)

		self.setLayout(layout)

#		self.updateplot()

	def updateplot(self): 

		self.canvas.axes.cla()

		self.canvas.axes.set_xlabel('Pm (bar)')
		self.canvas.axes.set_ylabel('P (GPa)')

		gr = self.data.df.groupby('calib')
		groups = gr.groups.keys()

		for g in groups:
			subdf = gr.get_group(g)
			self.canvas.axes.plot(subdf['Pm'], 
								  subdf['P'], 
								  marker='o',
								  color=self.calibrations[g].color,
								  label=g)
		if len(groups) != 0:
			self.canvas.axes.legend()
		self.canvas.draw()

class HPTableWidget(QTableWidget):
	''' Qt widget class for HPDataTable objects '''
	def __init__(self, HPDataTable_):
		super().__init__()

		self.data = HPDataTable_

		self.setStyleSheet('font-size: 12px;')

		nrows, ncols = self.data.df.shape

		self.setColumnCount(ncols)
		self.setRowCount(nrows)

		self.setHorizontalHeaderLabels( list(self.data.df.columns) )
		self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

		self.cellChanged[int,int].connect( self.getfromentry )

		deleteline_shortcut = QShortcut(QKeySequence("Ctrl+D"), self)
		deleteline_shortcut.activated.connect(self.remove_line)

	def getfromentry(self, row, col):
		# takes care of types
		try:
			newval = float( self.item(row, col).text() )
		except ValueError:
			newval =  self.item(row, col).text()
	
		key = self.data.df.columns[col]
	
		if key != 'calib':
			self.data.setitemval(row, key, newval)

			if key == 'P':
				self.data.reinvcalc_item_P(row)
			elif key in ['x', 'x0', 'T', 'T0'] :
				self.data.recalc_item_P(row)
	
		else: # k = calib 
			# I do not accept any calib change (for now a least)
			pass

	def updatetable(self):

		nrows, ncols = self.data.df.shape
		self.setRowCount(nrows)

		# Absolutely necessary to disconnect otherwise infinite loop
		self.cellChanged[int,int].disconnect()

		for irow in range(self.rowCount()):
			for icol in range(self.columnCount()):

				# print round() values in table
				v = self.data.df.iloc[irow,icol]
				if isinstance(v, (int, float)):
					s = str( round(v, 3) )
				else:
					s = str( v )

				self.setItem(irow, icol, QTableWidgetItem(s))

		self.cellChanged[int,int].connect( self.getfromentry )
		

	def remove_line(self):
		index = self.currentRow()
		if index >= 0:
			self.data.removespecific(index)



class HPTableWindow(QWidget):
	def __init__(self, HPDataTable_, calibrations_):
		super().__init__()

		self.data = HPDataTable_
		self.calibrations = calibrations_
		self.setWindowTitle('myPRL-qt table')

		self.resize(500,400)

		centerPoint = QDesktopWidget().availableGeometry().center()
		thePosition = (centerPoint.x() + 200, centerPoint.y() + 50)
		self.move(*thePosition)

		layout = QVBoxLayout()
		
		self.table_widget = HPTableWidget(HPDataTable_)
		layout.addWidget(self.table_widget)
		
		table_actions_layout = QHBoxLayout()

		self.table_save_csv_button = QPushButton('Save data to csv')
		self.table_load_csv_button = QPushButton('Load data from csv')
		table_actions_layout.addWidget(self.table_save_csv_button)
		table_actions_layout.addWidget(self.table_load_csv_button)

		layout.addLayout(table_actions_layout)

		self.setLayout(layout)

		self.table_save_csv_button.clicked.connect(self.save_data_to_csv)
		self.table_load_csv_button.clicked.connect(self.load_data_from_csv)

		save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
		load_shortcut = QShortcut(QKeySequence("Ctrl+O"), self)
		save_shortcut.activated.connect(self.save_data_to_csv)
		load_shortcut.activated.connect(self.load_data_from_csv)


	def save_data_to_csv(self):
		file = self.get_save_filename_dialog()
		if file:
			self.data.df.to_csv(file, 
								sep='\t', 
								decimal='.', 
								header=True,
								index=False)

	def load_data_from_csv(self):
		file = self.get_load_filename_dialog()
		if file:
			df_ = pd.read_csv(file, 
							  sep='\t', 
							  decimal='.', 
							  header=[0],
							  index_col=None)

		self.data.reconstruct_from_df(df_, self.calibrations)

	def get_save_filename_dialog(self):

		options =  QFileDialog.Options() 
	#	options = QFileDialog.DontUseNativeDialog
	# seems to bring an warning on Linux 5.10.0-19-amd64 #1 SMP Debian 5.10.149-2 (2022-10-21) x86_64 GNU/Linux
	# if I choose to not use Native Dialog - Hope it works with native on other platform

		fileName, fileType = \
			QFileDialog.getSaveFileName(self,
										"myPRL-qt: Save data to csv", 
										"",
										"CSV Files (*.csv);;All Files (*)", 
										options=options)

		if fileType == 'CSV Files (*.csv)':
			if '.csv' in fileName:
				pass
			else:
				fileName += '.csv'

		if fileName:
			return fileName
		else:
			return None

	def get_load_filename_dialog(self):

		options =  QFileDialog.Options() 
	#	options = QFileDialog.DontUseNativeDialog
	# seems to bring an warning on Linux 5.10.0-19-amd64 #1 SMP Debian 5.10.149-2 (2022-10-21) x86_64 GNU/Linux
	# if I choose to not use Native Dialog - Hope it works with native on other platform

		fileName, _ = \
			QFileDialog.getOpenFileName(self,
										"myPRL-qt: Load data from csv", 
										"",
										"CSV Files (*.csv);;All Files (*)", 
										options=options)
		if fileName:
			return fileName
		else:
			return None


class MyPRLMain(QMainWindow):
	def __init__(self):
		super().__init__()

		Ruby2020 = myPRLModels.HPCalibration(name = 'Ruby2020',
							     func = myPRLCalibfuncs.Pruby2020,
							     Tcor_name='Datchi 2007',
							     xname = 'lambda',
							     xunit = 'nm',
							     x0default = 694.28,
							     xstep = .01,
							     color = 'lightcoral')

		SamariumDatchi = myPRLModels.HPCalibration(name = 'Samarium Borate Datchi 1997',
							     	   func = myPRLCalibfuncs.PsamDatchi1997,
							     	   Tcor_name='NA',
							     	   xname = 'lambda',
							     	   xunit = 'nm',
							     	   x0default = 685.41,
							     	   xstep = .01,
							     	   color = 'moccasin')

		Akahama2006 = myPRLModels.HPCalibration(name = 'Diamond Raman Edge Akahama 2006',
							     	func = myPRLCalibfuncs.PAkahama2006,
							     	Tcor_name='NA',
							     	xname = 'nu',
							     	xunit = 'cm-1',
							     	x0default = 1333,
							     	xstep = .1,
							     	color = 'darkgrey')

		cBNDatchi = myPRLModels.HPCalibration(name = 'cBN Raman Datchi 2007',
							      func = myPRLCalibfuncs.PcBN,
							      Tcor_name='Datchi 2007',
							      xname = 'nu',
							      xunit = 'cm-1',
							      x0default = 1054,
							      xstep = .1,
							      color = 'lightblue')

		calib_list = [Ruby2020, 
					  SamariumDatchi, 
					  Akahama2006, 
					  cBNDatchi]

###############################################################################


		self.calibrations = {a.name:a for a in calib_list}
		self.data = myPRLModels.HPDataTable()
		self.DataTableWindow = HPTableWindow(self.data, self.calibrations)
		self.PmPplot_win = PmPPlotWindow(self.data, self.calibrations)

		# this will be our initial state
		self.buffer = myPRLModels.HPData(Pm = 0, 
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
		self.resize(240, 325)

		# large layout containing all widgets
		layout = QVBoxLayout()

		self.Pm_spinbox = QDoubleSpinBox()
		self.Pm_spinbox.setObjectName('Pm_spinbox')
		self.Pm_spinbox.setDecimals(2)
		self.Pm_spinbox.setRange(-np.inf, np.inf)
		self.Pm_spinbox.setSingleStep(.1)

		self.P_spinbox = QDoubleSpinBox()
		self.P_spinbox.setObjectName('P_spinbox')
		self.P_spinbox.setDecimals(3)
		self.P_spinbox.setRange(-np.inf, np.inf)
		self.P_spinbox.setSingleStep(.1)

		self.x_spinbox = QDoubleSpinBox()
		self.x_spinbox.setObjectName('x_spinbox')
		self.x_spinbox.setDecimals(3)
		self.x_spinbox.setRange(-np.inf, +np.inf)

		self.T_spinbox = QDoubleSpinBox()
		self.T_spinbox.setObjectName('T_spinbox')
		self.T_spinbox.setDecimals(0)
		self.T_spinbox.setRange(-np.inf, +np.inf)
		self.T_spinbox.setSingleStep(1)

		self.x0_spinbox = QDoubleSpinBox()
		self.x0_spinbox.setObjectName('x0_spinbox')
		self.x0_spinbox.setDecimals(3)
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


		self.add_button = QPushButton('+')
		self.add_button.setMinimumWidth(25)

		self.removelast_button = QPushButton('-')
		self.removelast_button.setMinimumWidth(25)

		self.table_button = QPushButton('Table')
		self.table_button.setMinimumWidth(70)

		self.PmPplot_button = QPushButton('P vs Pm')
		self.PmPplot_button.setMinimumWidth(70)

		actions_form = QHBoxLayout()

		actions_form.addWidget(self.add_button)
		actions_form.addWidget(self.removelast_button)
		actions_form.addWidget(self.table_button)
		actions_form.addWidget(self.PmPplot_button)

		layout.addLayout(pressure_form)

		layout.addStretch()
		layout.addWidget(MyQSeparator())
		layout.addStretch()

		layout.addLayout(data_form)

		layout.addStretch()
		layout.addWidget(MyQSeparator())
		layout.addStretch()
		
		layout.addLayout(calibration_form)

		layout.addStretch()
		layout.addWidget(MyQSeparator())
		layout.addStretch()

		layout.addLayout(actions_form)


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



		# Connects

		self.calibration_combo.currentIndexChanged.connect(self.updatecalib)

		self.Pm_spinbox.valueChanged.connect(self.update)
		self.P_spinbox.valueChanged.connect(self.update)

		self.x_spinbox.valueChanged.connect(self.update)
		self.x0_spinbox.valueChanged.connect(self.update)
		self.T_spinbox.valueChanged.connect(self.update)
		self.T0_spinbox.valueChanged.connect(self.update)

		self.add_button.clicked.connect(self.add_to_data)
		self.removelast_button.clicked.connect(self.removelast)

		self.PmPplot_button.clicked.connect(self.showPmPplot)

		# shortcuts

		add_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
		add_shortcut.activated.connect(self.add_to_data)

		removelast_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
		removelast_shortcut.activated.connect(self.removelast)

		showtable_shortcut = QShortcut(QKeySequence("Ctrl+T"), self)
		showtable_shortcut.activated.connect(self.showtable)

		self.table_button.clicked.connect(self.showtable)

		self.data.changed.connect(self.DataTableWindow.table_widget.updatetable)
		self.data.changed.connect(self.PmPplot_win.updateplot)
#		self.data.changed.connect(self.testreceive)

		# 1 cause it needs a signal
		self.updatecalib(1)	
		# for some reason updatecalib does not call update at __init__
		self.update(1)

#	def testreceive(self):
#		print('changed!')

	def add_to_data(self):
		self.data.add(self.buffer)
	#	print(self.data)

	def removelast(self):
		if len(self.data) > 0:
			self.data.removelast()

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

	def showtable(self, s=None):
		if self.DataTableWindow.isVisible(): 
			self.DataTableWindow.hide()
		else:
			self.DataTableWindow.show()

	def showPmPplot(self, s=None):
		if self.PmPplot_win.isVisible(): 
			self.PmPplot_win.hide()
		else:
			self.PmPplot_win.show()


if __name__ == '__main__':

	app = QApplication(sys.argv)
	
	main = MyPRLMain()
	main.show()
	
	app.exec()
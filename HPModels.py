import numpy as np
import pandas as pd
from scipy.optimize import minimize
from PyQt5.QtCore import QObject, pyqtSignal

class HPCalibration:
	''' A general HP calibration object '''
	def __init__(self, name, func, Tcor_name, 
					xname, xunit, x0default, xstep, color):
		self.name = name
		self.func = func
		self.Tcor_name = Tcor_name
		self.xname = xname
		self.xunit = xunit
		self.x0default = x0default
		self.xstep = xstep  # x step in spinboxes using mousewheel
		self.color = color  # color printed in calibration combobox

	def inv_func(self, p, *args, **kwargs):
		res = minimize( lambda x: ( self.func(x, *args, **kwargs) - p )**2, 
									x0=self.x0default, tol=1e-6)
		return res.x[0]


class HPDataTable(QObject):
	''' A general HP data table object containing the dataframe and all
		calculation methods '''

	# signal sends a pd.DataFrame object
	changed = pyqtSignal(pd.DataFrame)

	def __init__(self, df):
		super().__init__()

		self.df = df
		#self.changed.connect()

	def update(self, newdf):
		self.df = newdf
		self.changed.emit(self.df)

	def eval(self):
		

if __name__ == '__main__':
	a = {'a': np.linspace(1,10,10),
		 'b': np.linspace(1,42,10)}
	data = HPDataTable(pd.DataFrame(a))
	print(data.df)
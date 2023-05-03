from scipy.optimize import minimize

# Shen G., Wang Y., Dewaele A. et al. (2020) High Pres. Res. doi: 10.1080/08957959.2020.1791107
def Pruby2020(l, l0, T, T0):
	dT = T - T0
	dlcorr = 0.00746 * dT - 3.01e-6 * dT**2 + 8.76e-9 * dT**3  # Datchi HPR 2007
	dl = (l - dlcorr) - l0
	P = 1870 * dl/l0 * (1 + 5.63 * dl/l0)

	return P

def invPruby2020(p, l0, T, T0):
#	l1 = np.linspace(694, 740, 50)
#	p1 = Pruby2020(l1, l0, T, T0)
#	polyapprox = np.poly1d(np.polyfit(p1, l1, 2))
#	print(polyapprox(p))
	res = minimize( lambda x: (Pruby2020(x, l0, T, T0) - p)**2, x0=700, tol=1e-5)
	l = res.x[0]	

	return l

#  F. Datchi, High Pressure Research, 27:4, 447-463, DOI: 10.1080/08957950701659593 
def PsamDatchi(l, l0 = 685.41, T = 298, T0 = 298):
    dT = T - T0
#    dlcorr = -8.7e-5 * dT + 4.62e-6 * dT**2 -2.38e-9 * dT**3    # problem here !? (Datchi HPR 2007)
#    if T >= 500:
#        dlcorr = 1.06e-4 * (T-500) + 1.5e-7 * (T-500)**2    # these Queyroux p. 68
#    else:
#        dlcorr = 0
    dlcorr=0
    dl = (l-dlcorr) - l0
    P = 4.032 * dl * (1 + 9.29e-3 * dl) / (1 + 2.32e-2 * dl)
    return P
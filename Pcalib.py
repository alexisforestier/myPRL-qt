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
def PsamDatchi1997(l, l0, T, T0):
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

def invPsamDatchi1997(p, l0, T, T0):
	res = minimize( lambda x: (PsamDatchi1997(x, l0, T, T0) - p)**2, x0=690, tol=1e-5)
	l = res.x[0]	

	return l



#  F. Datchi, High Pressure Research, 27:4, 447-463, DOI: 10.1080/08957950701659593 
def PcBN(nu, T = 298, nu0 = 1058.4):
    nu0_T = nu0 - 0.0091 * T - 1.54e-5 * T**2
    B0_T = 396.5 - 0.0288 * (T - 300) - 6.84e-6 * (T - 300)**2
    B0p = 3.62
    P = (B0_T/B0p) * ( (nu/nu0_T)**2.876 - 1 )
    return P

def find_cBN_nu00(nu, P, T):
    result = minimize( lambda nu00: (PcBN(nu, T, nu00) - P)**2, 1058.4) # Initial value F. Datchi HPR
    return np.float( result.x )
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

"""
Forme i(t) = [1-exp(-t/taux)]Iper avec Iper = U/Re
Re = Rm + 220
"""
Re = 9.3 + 220
data = pd.read_csv("ressources/acquisitionL.txt", delimiter=",")
t, u = np.array(data["t"]), np.array(data["Ur(t)"])
i = u/Re

indice0 = 0
while t[indice0] < 0:
    indice0 += 1
t = t[indice0:]
i = i[indice0:]

def f(t, Iper, taux):
    return Iper*(1-np.exp(-t/taux)) # taux = L/Re
[Iper, taux], val = curve_fit(f, t, i)
plt.plot(t*1e3, i*1e3, label="acquisition")
plt.plot(t*1e3, f(t, Iper, taux)*1e3, label="curve_fit")
plt.xlabel("t (ms)")
plt.ylabel("i(t) (mA)")
L = Re*taux
plt.title(f"L = Re/taux = {round(L, 3)}H")
print(f"L= {L} H")
plt.show()
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

data = pd.read_csv('ressources/acquisition12v.txt', delimiter=';')
x12, y12 = np.array(data['t']), np.array(data['w(t)'])
data = pd.read_csv('ressources/acquisition10v.txt', delimiter=';')
x10, y10 = np.array(data['t']), np.array(data['w(t)'])
data = pd.read_csv('ressources/acquisition8v.txt', delimiter=';')
x8, y8 = np.array(data['t']), np.array(data['w(t)'])
data = pd.read_csv('ressources/acquisition15v.txt', delimiter=';')
x15, y15 = np.array(data['t']), np.array(data['w(t)'])
def ideal(x, A, taux):
    return A*(1-np.exp(-x/taux))

nbr_pts = 30
minx = min(len(x12), len(x10), len(x8), len(x15))
if nbr_pts > minx:
    nbr_pts = minx

x12, y12 = x12[:nbr_pts]/1e6, y12[:nbr_pts]
x10, y10 = x10[:nbr_pts]/1e6, y10[:nbr_pts]
x8, y8 = x8[:nbr_pts]/1e6, y8[:nbr_pts]
x15, y15 = x15[:nbr_pts]/1e6, y15[:nbr_pts]

[A12, taux12], vals = curve_fit(ideal, x12, y12)
[A10, taux10], vals2 = curve_fit(ideal, x10, y10)
[A8, taux8], vals3 = curve_fit(ideal, x8, y8)
[A15, taux15], vals4 = curve_fit(ideal, x15, y15)

x2 = np.linspace(0, x12[-1], 100)

y2_12 = ideal(x2, A12, taux12)
y2_8 = ideal(x2, A8, taux8)
y2_15 = ideal(x2, A15, taux15)
y2_10 = ideal(x2, A10, taux10)

plt.plot(x15, y15, label='w15(t) en rad/s')
plt.plot(x12, y12, label='w12(t) en rad/s')
plt.plot(x10, y10, label='w10(t) en rad/s')
plt.plot(x8, y8, label='w8(t) en rad/s')

x = x12[-1]/2
size = 8
plt.plot(x2, y2_15)
plt.text(x, y2_15[-1]+size/2, f"\N{greek small letter tau}15 = {round(taux15, 4)} s", fontsize=size)
plt.plot(x2, y2_12, label="curve_fit w12")
plt.text(x, y2_12[-1]+size/2, f"\N{greek small letter tau}12 = {round(taux12, 4)} s", fontsize=size)
plt.plot(x2, y2_10, label="curve_fit w10")
plt.text(x, y2_10[-1]+size/2, f"\N{greek small letter tau}10 = {round(taux10, 4)} s", fontsize=size)
plt.plot(x2, y2_8, label="curve_fit w8")
plt.text(x, y2_8[-1]+size/2, f"\N{greek small letter tau}8 = {round(taux8, 4)} s", fontsize=size)

print(f"\N{greek small letter tau}_15 = {taux15} s")
print(f"\N{greek small letter tau}_12 = {taux12} s")
print(f"\N{greek small letter tau}_10 = {taux10} s")
print(f"\N{greek small letter tau}_8 = {taux8} s")
print(f"\N{greek small letter tau} moyenne = {(taux15+taux12+taux10+taux8)/4} s")
# plt.legend()
plt.xlabel("temps (s)")
plt.ylabel("w_m (rad/s)")
plt.grid()
plt.show()

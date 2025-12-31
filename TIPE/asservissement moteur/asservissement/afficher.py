import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

data = pd.read_csv("acquisition.txt", delimiter=";")
t, teta, wr, erreur, pwm = np.array(data["t"]), data["teta(t)"], data["wr(t)"], data["erreur"], data["pwm"]

t = t/1e6 # prendre en secondes

fig, (ax1, ax3) = plt.subplots(2, 1)
ax1.plot(t, teta)
ax1.plot([t[0], t[-1]], [180, 180], color='red')
ax1.set_title("teta(t) (°)")
ax1.grid()

# ax2.plot(t, wr)
# ax2.set_title("wr(t) (°/s)")
# ax2.grid()

ax3.plot(t, erreur)
ax3.set_title("erreur(t)")
ax3.grid()

# ax4.plot(t, pwm)
# ax4.set_title("pwm(t)")
# ax4.grid()

plt.show()

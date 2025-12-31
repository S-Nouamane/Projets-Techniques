import matplotlib.pyplot as plt
import numpy as np

# sscale
scale = [1, 20, 50, 103, 150]
m_reel = [0, 10, 20, 30, 50, 60, 70, 80]
out = [[0, 3600, 4200, 6300, 8600, 9900, 10250, 11630],
       [0, 62, 105, 156, 260, 310, 340, 380],
       [0, 28, 46, 69, 113, 135, 150, 168],
       [0, 10.3, 19.7, 30.1, 50.3, 60, 68.4, 78],
       [0, 9.5, 14, 25.8, 41, 48, 54, 61]
       ]
def f(x, a, b):
    return a*x + b

for i in range(len(scale)):
    y = out[i]
    a, b = np.polyfit(m_reel, y, 1)
    plt.scatter(m_reel, out[i], label=f"scale = {scale[i]}")
    plt.plot([0, 90], f(np.linspace(0, 90, 2), a, b), label=f"fit, a={round(a, 3)}, b={round(b, 3)}")
    plt.grid()
    plt.legend()
    plt.show()
    # plt.savefig(f"load_cell/experience/HX711_scale_{scale[i]}.pdf")
    # plt.savefig(f"load_cell/experience/HX711_scale_{scale[i]}.png")
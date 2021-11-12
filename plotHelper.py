import matplotlib
import matplotlib.pyplot as plt
import random

colors = []
colorsDone = False

# get random different colors matplotlib
def getRandomColors(n):
    global colors
    global colorsDone
    if colorsDone:
        return colors
    for _ in range(n * 30):
        # colors.append(matplotlib.colors.to_hex(matplotlib.colors.hsv_to_rgb([random.random(), 1, 1])))
        colors.append(matplotlib.colors.to_hex(matplotlib.colors.hsv_to_rgb([random.random(), 1, 1])))
    colorsDone = True
    return colors

def getPlot(matrix, seeds):
    cmap = matplotlib.colors.ListedColormap(getRandomColors(len(seeds)), name = 'colors', N=None)
    plt.imshow(matrix, cmap=cmap)
    # plt.scatter(100,100, s=102.4, c="white", edgecolors=["black"])
    # plt.show()
    plt.pause(0.1)
    plt.draw()

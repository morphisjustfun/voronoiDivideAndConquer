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
    for i in range(n * 30):
        # colors.append(matplotlib.colors.to_hex(matplotlib.colors.hsv_to_rgb([random.random(), 1, 1])))
        if i == 0:
            colors.append(matplotlib.colors.to_hex(matplotlib.colors.hsv_to_rgb([0, 0, 1])))
        else:
            colors.append(matplotlib.colors.to_hex(matplotlib.colors.hsv_to_rgb([random.random(), 1, 1])))
    colorsDone = True
    return colors

def getPlot(matrix, seeds):
    cmap = matplotlib.colors.ListedColormap(getRandomColors(len(seeds)), name = 'colors', N=None)
    plt.imshow(matrix, cmap=cmap)
    # plt.scatter(100,100, s=102.4, c="white", edgecolors=["black"])
    plt.pause(0.00001)
    plt.draw()

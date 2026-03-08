import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
import numpy as np

fig, ax = plt.subplots()
xdata, ydata = [], []
ln, = ax.plot([], [], 'ro')

def init():
    ax.set_xlim(0, 2*np.pi)
    ax.set_ylim(-1, 1)
    return ln,

def update(frame):
    xdata.append(frame)
    ydata.append(np.sin(frame))
    ln.set_data(xdata, ydata)
    return ln,

ani = FuncAnimation(fig, update, frames=np.linspace(0, 2*np.pi, 20), init_func=init, blit=True)

writer = FFMpegWriter(fps=10, metadata=dict(title="Test"), extra_args=["-vcodec", "libx264", "-pix_fmt", "yuv420p"])
ani.save("test_min.mp4", writer=writer)
plt.close()

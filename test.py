# import matplotlib.pyplot as plt

# x = [1, 2, 3]
# y = [2, 4, 1]
# plt.plot(x, y)
# plt.show()
from gi.repository import GdkPixbuf

for fmt in GdkPixbuf.Pixbuf.get_formats():
    print(fmt.get_extensions())

import os
import numpy as np
import argparse
import cv2
from PIL import Image
from matplotlib import pyplot as plt

parser = argparse.ArgumentParser(description='mark clicked points on an image')
parser.add_argument('img_file_path', help="img_file_path", type=str)
parser.add_argument('-c', '--count', help="offset of the count", type=int, default=0)
parser.add_argument('-a', '--auto_save_interval', help="auto_save_interval", type=int, default=10)
parser.add_argument('-s', '--image_scale', help="scale for image", type=float, default=0.5)



class Img_Mgr:
    
    def __init__(self, fig, ax, img, count, auto_save_interval, img_file_path):
        self.press_pos = [-1, -1]
        self.fig = fig
        self.ax = ax
        self.auto_save_interval = auto_save_interval

        self.dirname = os.path.dirname(img_file_path)
        self.basename = os.path.basename(img_file_path)
        self.basename, self.ext = os.path.splitext(self.basename)

        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.img = img
        self.count = count

    def on_press(self, event):
        # print('on_press', event)

        if event.button != 1:
            return
        
        x = event.xdata
        y = event.ydata
        if x == None or y == None:
            self.press_pos = [-1, -1]
            return
        self.press_pos = [x, y]
        # print("pressed: {}, {}".format(x, y))


    def on_release(self, event):
        # print('on_press', event)
        if event.button != 1:
            return
        
        x = event.xdata
        y = event.ydata
        px, py = self.press_pos

        if x == None or y == None:
            return

        if np.linalg.norm([(x - px, y - py)]) > 1.0:
            self.press_pos = [-1, -1]
            return
        
        self.count += 1
        x, y = int(x), int(y)
        color = (0, 255, 0), (0, 0, 0)
        cv2.circle(self.img, (x, y), 3 + 4, color[1], -1)
        cv2.circle(self.img, (x, y), 3, color[0], -1)

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.0
        ofs = 5
        cv2.putText(self.img, "{}".format(self.count), (x + ofs, y), font, font_scale, color[1], thickness=2 + 4)
        cv2.putText(self.img, "{}".format(self.count), (x + ofs, y), font, font_scale, color[0], thickness=2)

        self.ax.imshow(self.img)
        plt.draw()

        if self.count % auto_save_interval == 0:
            print('auto save...')
            self.save('(auto_saved)')

        
    def save(self, suffix=''):
        dst = '{}_{:04d}{}{}'.format(self.basename, self.count, suffix, self.ext)
        dst = os.path.join(self.dirname, dst)
        print('save: {}'.format(dst))
        cv2.imwrite(dst, self.img)


if __name__ == '__main__':
    args = parser.parse_args()
    img_file_path = args.img_file_path
    count = args.count
    auto_save_interval = args.auto_save_interval
    image_scale = args.image_scale


    print("open {}".format(img_file_path))

    img = Image.open(img_file_path)
    s = (int(image_scale * img.width), int(image_scale * img.height))
    img = img.resize(s)
    img = np.asarray(img)

    fig, ax = plt.subplots(1, 1)
    ax.imshow(img)
    img_mgr = Img_Mgr(fig, ax, img, count, auto_save_interval, img_file_path)

    plt.show()
    img_mgr.save()


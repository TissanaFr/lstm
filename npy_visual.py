import os
import numpy as np
import cv2
import click
import glob
import json
import shutil


@click.command()
@click.option('--folder', type=str, default=None)
@click.option('--filename', type=str, default=None)
def fmain(folder, filename):
    folder = 'D:/datasets/close3_npy'
    # os.makedirs(dst, exist_ok=True)

    if folder is not None:
        for filename in glob.iglob(os.path.join(folder, '**', '*.npy'), recursive=True):
            with open(filename, 'rb') as f:
                data = np.load(f)

            i = 0
            while True:
                print(os.path.basename(filename))
                print(data[i].shape)
                cv2.imshow(str(i) + ' ' + os.path.basename(filename), data[i])
                # cv2.imshow(str(i), data[49])
                cv2.moveWindow(str(i) + ' ' + os.path.basename(filename), 20, 20)
                key = cv2.waitKey()
                if key == 115:
                    cv2.destroyAllWindows()
#                    shutil.move(filename, os.path.join(dst, os.path.basename(filename)))
                    break
                if key == 100:
                    i = i + 1 if i < len(data) - 1 else len(data) - 1
                if key == 97:
                    i = i - 1 if i > 0 else 0

                cv2.destroyAllWindows()

                if key == 27:
                    cv2.imwrite("d:/datasets/far.jpg", data[i])
                    return 0
                if key == 13:
                    break

    else:
        with open(filename, 'rb') as f:
            data = np.load(f)

        i = 0
        while True:
            cv2.imshow(str(i) + ' ' + os.path.basename(filename), data[i])
            cv2.moveWindow(str(i) + ' ' + os.path.basename(filename), 20, 20)
            key = cv2.waitKey()
            if key == 100:
                i = i + 1 if i < len(data)-1 else len(data)-1
            if key == 97:
                i = i - 1 if i > 0 else 0

            cv2.destroyAllWindows()

            if key == 27:
                return 0
            if key == 13:
                cv2.destroyAllWindows()
                break


if __name__ == "__main__":
    fmain()

import os
import click
import json
import numpy as np
import cv2
import uuid
from collections import deque
import glob
import sys


def resize_frame(img, new_size):
    old_w, old_h, _ = img.shape
    l = float(min(new_size[0], new_size[1]) / max(old_w, old_h))
    new_frame = cv2.resize(img, None, fx=l, fy=l, interpolation=cv2.INTER_LINEAR)
    w, h, _ = new_frame.shape
    delta_w = new_size[0] - w
    delta_h = new_size[1] - h

    color = [0, 0, 0]

    resized_frame = cv2.copyMakeBorder(new_frame, 0, delta_w, 0, delta_h, cv2.BORDER_CONSTANT, value=color)
    return resized_frame


@click.command()
@click.option('--size', nargs=2, type=int, help='Size of frames.')
@click.option('--src', type=str, help='Directory with annotated vids.')
@click.option('--dst', type=str, help='Folder to store sequences.')
def transform(src:str, size, dst: str):
    wc = '*.mp4'
    for video in glob.iglob(os.path.join(src, '**', wc), recursive=True):
        action_idx = {
            'empty': 0,
            'left': 1,
            'right': 2,
            'far': 3,
            'close': 4,
            'up': 5,
            'down': 6,
            'smile': 7,
            'eyes': 8
        }

        def _save_npy_and_ann(seq, seq_filename, annotation):
            np.save(seq_filename, np.array(seq))

            with open(seq_filename + '.npy.annotations', 'w') as fan:
                json.dump(annotation, fan)

            return seq

        if not os.path.exists(video):
            click.secho('--> Video file not found!', fg='red')
            return -1

        if not os.path.exists(video + '.annotations'):
            click.secho('--> Annotation file not found!', fg='red')
            return -1

        reader = None
        try:
            reader = cv2.VideoCapture(video)
        except:
            click.secho('--> Failed to initialize video source {}'.format(video), fg='red')
            return -1

        filename = os.path.splitext(os.path.basename(video))[0]

        raw_folder = None

        raw_folder = os.path.join(dst, filename+'_'+str(size[0]))
        if not os.path.exists(raw_folder):
            os.makedirs(raw_folder)
        else:
            continue

        fb_folder = None
        if fb:
            fb_folder = os.path.join(dst, filename+'_'+str(length)+'_'+str(size[0])+'_'+'fb')
            if not os.path.exists(fb_folder):
                os.makedirs(fb_folder)

        frame_cnt = 0
        seq_raw = deque(list())
        seq_fb = deque(list())
        frame_idx = deque(list())

        data = None
        with open(video+'.annotations', 'r') as f:
            data = json.load(f)

        prev_frame = None
        total = int(reader.get(cv2.CAP_PROP_FRAME_COUNT))

        while True:
            # frame = reader.next_frame()
            _, frame = reader.read()
            if frame is None:
                break
            if raw:
                seq_filename_raw = str(uuid.uuid4().hex)
                seq_filename_raw = os.path.join(raw_folder, seq_filename_raw)
            if fb:
                seq_filename_fb = str(uuid.uuid4().hex)
                seq_filename_fb = os.path.join(fb_folder, seq_filename_fb)

            print(len(seq_raw))

            if len(seq_raw) == length:
                cur_action = None
                prev_action = None
                action_cnt = 0
                conf = 0.0

                for idx in frame_idx:
                    cur_action = get_action_from_annotations(idx, data)

                    if cur_action is not None:
                        if cur_action == prev_action or prev_action is None:
                            action_cnt += 1
                            prev_action = cur_action
                    else:
                        conf = float(action_cnt / length)
                        cur_action = prev_action

                if action_cnt != 0:
                    conf = float(action_cnt / length)

                if conf >= high or conf <= low:
                    ann = dict()
                    if conf <= low:
                        ann['class'] = action_idx['empty']
                    else:
                        ann['class'] = action_idx[cur_action]
                    ann['conf'] = float('{:.2}'.format(conf))

                    print(ann['class'], ': ', ann['conf'])

                    if raw:
                        seq_raw = _save_npy_and_ann(seq_raw, seq_filename_raw, ann)
                    if fb:
                        seq_fb = _save_npy_and_ann(seq_fb, seq_filename_fb, ann)
                else:
                    seq_raw.popleft() if raw else None
                    seq_fb.popleft() if fb else None

                frame_idx.popleft()

            w, h, _ = frame.shape

            if raw:
                frame_raw_resized = resize_frame(frame, size)
                seq_raw.append(frame_raw_resized)
            if fb:
                if prev_frame is None: prev_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frame_fb = cv2.calcOpticalFlowFarneback(prev_frame, frame_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
                prev_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frame_fb = np.concatenate((frame_fb, np.zeros((w, h, 1))), axis=2)
                frame_fb_resized = resize_frame(frame_fb, size)
                seq_fb.append(frame_fb_resized)

            print("\033[H\033[J")
            per = round(float(frame_cnt/total), 2)
            print(video)
            print("Progress: {0}%".format(per*100))

            frame_idx.append(frame_cnt)
            frame_cnt += 1


if __name__ == '__main__':
    transform()

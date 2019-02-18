#!/usr/bin/env python3
# Mucks with the frames in a video file to produce a "datamosh" effect.

# ------------------------------------------------------------------------------
#
# Adapted from https://github.com/thisisparker/automosh
#
# Read the accompanying blog posts:
# https://parkerhiggins.net/2017/07/making-mosh-ups-automated-datamoshing-from-multiple-video-sources/
# https://parkerhiggins.net/2017/07/he-did-the-monster-mosh-automated-datamoshing-with-tweaked-gop-lengths/
#
# ------------------------------------------------------------------------------


import argparse
import json
import os
import operator
import random
import subprocess

class VideoMosh:
    def __init__(self, inpath, outpath):
        self.inpath = inpath
        self.outpath = outpath

        print("Getting list of frames for {}.".format(self.inpath))

        f = subprocess.run(['ffprobe','-select_streams','v','-show_frames','-print_format','json', '-loglevel', 'quiet', self.inpath], stdout=subprocess.PIPE).stdout
        flist = json.loads(str(f,'utf-8'))
        flist = flist['frames']

        self.frames = flist

        self.i_frames = [frame for frame in self.frames if frame['pict_type'] == 'I']
        self.p_frames = [frame for frame in self.frames if frame['pict_type'] == 'P']


        with open(self.inpath,"rb") as f:
            self.data = f.read()

    def mosh(self):
        print("Moshing up video.")
        self.datamosh = self.data[:]

        to_shuffle = self.i_frames[1:]

#        random.shuffle(to_shuffle)
        to_shuffle.sort(key=operator.itemgetter('pkt_size'))

        for index in range(len(to_shuffle) - 1):
            if index % 2:
                swap_1, swap_2 = swap_frames(to_shuffle[index],
                                             to_shuffle[index + 1],
                                             self.data)

                self.datamosh = self.datamosh[:swap_1['pkt_pos']] \
                                + swap_1['data'] \
                                + self.datamosh[swap_1['end_pos']:]

                self.datamosh = self.datamosh[:swap_2['pkt_pos']] \
                                + swap_2['data'] \
                                + self.datamosh[swap_2['end_pos']:]

def insert_frames(target_video, origin_video):
    target_list = target_video.i_frames[:]
    origin_list = origin_video.i_frames[:]

    count = min(len(target_list),len(origin_list))

    for index in range(count):
        target_pos = int(target_list[index]['pkt_pos'])
        target_size = int(target_list[index]['pkt_size'])
        target_end = target_pos + target_size

        origin_pos = int(origin_list[index]['pkt_pos'])
        origin_size = int(origin_list[index]['pkt_size'])
        origin_end = origin_pos + origin_size

        diff = target_size - origin_size

        frame_data = origin_video.data[origin_pos:origin_pos + target_size] if diff < 0 else origin_video.data[origin_pos:origin_end] + bytes(diff)

        target_video.data = target_video.data[:target_pos] + frame_data + target_video.data[target_end:]

    return target_video

def swap_frames(frame_1, frame_2, video):
    if frame_1['pkt_pos'] > frame_2['pkt_pos']:
        temp = frame_1
        frame_1 = frame_2
        frame_2 = temp

    swap_1 = {'pkt_pos':int(frame_1['pkt_pos']),
              'end_pos':int(frame_1['pkt_pos']) + int(frame_1['pkt_size']),
              'pkt_size':int(frame_1['pkt_size'])}

    swap_2 = {'pkt_pos':int(frame_2['pkt_pos']),
              'end_pos':int(frame_2['pkt_pos']) + int(frame_2['pkt_size']),
              'pkt_size':int(frame_2['pkt_size'])}

    diff = swap_1['pkt_size'] - swap_2['pkt_size']

    if diff > 0:
        swap_1['data'] = video[swap_2['pkt_pos']:swap_2['end_pos']] + bytes(diff)
        swap_2['data'] = video[swap_1['pkt_pos']:swap_1['pkt_pos'] + swap_2['pkt_size']]

    else:
        swap_1['data'] = video[swap_2['pkt_pos']:swap_2['pkt_pos'] + swap_1['pkt_size']]
        swap_2['data'] = video[swap_1['pkt_pos']:swap_1['end_pos']] + bytes(-diff)

    return swap_1, swap_2

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Path for the video you want to mosh.")
    parser.add_argument("output", help="Path for the outputted video file.")

    parser.add_argument("-r", "--replace", help="Path for video to use replacement frames from", default=None)

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print("No file named {}.".format(args.input))
        return None

    if os.path.exists(args.output):
        clobber = input("{} already exists. Overwrite? (y/N) ".format(args.output))
        if clobber.lower() != 'y':
            return None

    video = VideoMosh(args.input, args.output)

    if args.replace:
        origin = VideoMosh(args.replace, None)
        print("Moshing the video {} into the video {}.".format(video.inpath, origin.inpath))
        print("Target video is {} frames long, origin video is {} frames long.".format(str(len(video.frames)), str(len(origin.frames))))
        moshed = insert_frames(video, origin)
        with open(video.outpath, "wb") as f:
            f.write(moshed.data)

        return None

    print("Video to mosh is " + video.inpath)
    print("That video is {} frames long".format(str(len(video.frames))))

    video.mosh()

    print("Saving video as {}.".format(video.outpath))

    with open(video.outpath,"wb") as f:
        f.write(video.datamosh)

if __name__ == "__main__":
    main()

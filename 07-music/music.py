#!/usr/bin/python3
import sys
import numpy as np
import wave
import struct
import math
# import matplotlib.pyplot as plt


class Segment:
    def __init__(self):
        self.start_time = 0.0
        self.end_time = 0.0
        self.peaks = []

    def __eq__(self, other):
        if len(self.peaks) != len(other.peaks):
            return False
        this_peaks = sorted(self.peaks)
        other_peaks = sorted(other.peaks)
        for index in range(0, len(self.peaks)):
            if this_peaks[index] != other_peaks[index]:
                return False
        return True


def get_tone(a_reference, frequency):
    tones = ['a', 'bes', 'b', 'c', 'cis', 'd', 'es', 'e', 'f', 'fis', 'g', 'gis']
    steps = math.log((frequency / a_reference), math.pow(2, (1/12)))
    steps_up = True
    if steps < 0:
        steps_up = False
    steps = np.abs(steps)
    octave_shift = int(steps // 12)
    tone = int(steps % 12)
    cents = float("{0:.2f}".format((steps - tone) % 12))
    cents = int(cents * 100)
    if cents > 50:
        cents = cents - 100
        tone = tone + 1
        tone = tone % 12
    if tone > 2:
        tone = tone - 12
        # octave_shift += 1
    if not steps_up:
        cents = cents * (-1)
        tone = tone * (-1)
        octave_shift = octave_shift * (-1)
    tone_label = tones[tone]

    if octave_shift < -1:
        tone_label = tone_label.capitalize()
    while octave_shift < -2:
        tone_label = tone_label + ','
        octave_shift += 1
    # if octave_shift < -2:
    #     tone_label = tone_label + ','
    # if octave_shift < -3:
    #     tone_label = tone_label + ','
    while octave_shift > -1:
        tone_label = tone_label + '’'
        octave_shift -= 1
    # if octave_shift > -1:
    #     tone_label = tone_label + '’'
    # if octave_shift > 0:
    #     tone_label = tone_label + '’'
    cents_string = str(cents)
    if cents >= 0:
        cents_string = '+' + cents_string
    return tone_label + cents_string


def music(a_reference, file):
    wave_stream = wave.open(file, 'rb')

    frame_rate = wave_stream.getframerate()
    num_frames = wave_stream.getnframes()
    num_channels = wave_stream.getnchannels()
    # print('frame rate:', frame_rate)
    # print('number of frames:', num_frames)
    # print('number of channels:', num_channels)

    max_cluster_deviaion = 1  # max cluster deviation in Hz
    window_shift_time = 0.1
    window_shift = (window_shift_time * frame_rate)
    p = 1
    n = frame_rate * p
    total_samples = num_frames * num_channels
    sample_width = wave_stream.getsampwidth()

    num_windows = int(num_frames / window_shift) - (int(p/window_shift_time) - 1)
    # print('total samples:', total_samples)
    # print('sample width:', sample_width)
    # print('number of windows:', num_windows)

    raw_data = wave_stream.readframes(num_frames)
    wave_stream.close()

    if sample_width == 1:
        fmt = "%iB" % total_samples  # unsigned
    elif sample_width == 2:
        fmt = "%ih" % total_samples  # signed 2 byte shorts
    else:
        raise ValueError("Only supports 8 and 16 bit audio formats.")

    integer_data = struct.unpack(fmt, raw_data)
    #stereo
    if num_channels == 2:
        channels = [[] for time in range(num_channels)]

        for index, value in enumerate(integer_data):
            bucket = index % num_channels
            channels[bucket].append(value)

        integer_data = []
        for index in range(0, num_frames):
            integer_data.append(int( (channels[0][index] + channels[1][index]) / 2 ))

    # print('integer data len:', len(integer_data))
    last_segment = Segment()
    for index in range(0, num_windows):
        segment = Segment()
        start = int(index * window_shift)
        end = (start + n)
        segment.start_time = float("{0:.2f}".format(index * window_shift_time))
        segment.end_time = float("{0:.2f}".format(segment.start_time + window_shift_time))
        # print('start:', start, 'end:', end)
        data_window = integer_data[start:end]
        fft_res = np.abs(np.fft.rfft(a=data_window, n=int(n)))
        window_avg = sum(fft_res) / len(fft_res)
        # print('window_avg:', window_avg)
        peak_dict = {}
        for i in range(0, len(fft_res)):
            if fft_res[i] >= 20 * window_avg:
                freq = i
                peak_dict[fft_res[i]] = i
                # print('freq', i)
                # segment.peaks.append(i)

        for amplitude in sorted(peak_dict, reverse=True):
            add_peak = True
            # print(amplitude)
            # print(peak_dict[amplitude])
            for peak in segment.peaks:
                if np.abs(peak_dict[amplitude] - peak) < max_cluster_deviaion:
                    add_peak = False
            if add_peak:
                if len(segment.peaks) < 3:
                    segment.peaks.append(peak_dict[amplitude])
        if start == 0:
            last_segment = segment
        if last_segment.__eq__(segment):
            last_segment.end_time = float("{:.2f}".format((index * window_shift_time) + window_shift_time))
            # print('updated:', last_segment.end_time)
        else:
            print_segment(last_segment, a_reference)
            last_segment = Segment()
            last_segment.start_time = segment.start_time
            last_segment.end_time = segment.end_time
            last_segment.peaks = segment.peaks
    print_segment(last_segment, a_reference)


def print_segment(segment, a_reference):
    if len(segment.peaks) > 0:
        if segment.start_time < 10.0:
            print(str(0), end='')
        print(segment.start_time, '-', end='', sep='')
        if segment.end_time < 10.0:
            print(str(0), end='')
        print(segment.end_time, end=' ')
        for p in sorted(segment.peaks):
            print(get_tone(int(a_reference), p), end=' ')
        print()


if __name__ == "__main__":

    if len(sys.argv) == 3:
        music(sys.argv[1], sys.argv[2])
        # print(get_tone(int(sys.argv[1]), int(sys.argv[2])))
    else:
        print("Wrong number of arguments")
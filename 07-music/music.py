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


class Cluster:
    def __init__(self):
        self.start_frequency = 0
        self.end_frequency = 0
        self.max_amplitude = 0.0
        self.frequency_of_max_amplitude = 0
        self.hertz_deviation = 1

    def contains_cluster(self, other_cluster):
        return (other_cluster.end_frequency <= (self.end_frequency + self.hertz_deviation) and other_cluster.start_frequency >= (self.start_frequency - self.hertz_deviation))

    def append_cluster(self, other_cluster):
        if self.contains_cluster(other_cluster):
            if other_cluster.start_frequency < self.start_frequency:
                self.start_frequency = other_cluster.start_frequency
                if other_cluster.max_amplitude > self.max_amplitude:
                    self.max_amplitude = other_cluster.max_amplitude
                    self.frequency_of_max_amplitude = other_cluster.frequency_of_max_amplitude
            if other_cluster.end_frequency > self.end_frequency:
                self.end_frequency = other_cluster.end_frequency
                if other_cluster.max_amplitude > self.max_amplitude:
                    self.max_amplitude = other_cluster.max_amplitude
                    self.frequency_of_max_amplitude = other_cluster.frequency_of_max_amplitude


def get_tone(a_reference, frequency):
    tones = ['a', 'bes', 'b', 'c', 'cis', 'd', 'es', 'e', 'f', 'fis', 'g', 'gis']
    steps = math.log((frequency / a_reference), math.pow(2, (1/12)))
    steps_up = True
    if steps < 0:
        steps_up = False
    steps = np.abs(steps)
    octave_shift = int(steps // 12)
    tone = int(steps % 12)
    cents = float((steps - tone) % 12)
    cents = int(round(cents * 100))
    if cents > 50:
        cents = cents - 100
        tone = tone + 1
        # tone = tone % 12
        if tone > 11:
            tone = tone % 12
            octave_shift += 1
    if steps_up:
        if tone > 2:
            tone = tone - 12
            octave_shift += 1
    if not steps_up:
        if tone > 9:
            tone = tone - 12
            octave_shift += 1
        cents = cents * (-1)
        tone = tone * (-1)
        octave_shift = octave_shift * (-1)
    tone_label = tones[tone]
    if octave_shift < -1:
        tone_label = tone_label.capitalize()
    while octave_shift < -2:
        tone_label = tone_label + ','
        octave_shift += 1
    while octave_shift > -1:
        tone_label = tone_label + '’'
        octave_shift -= 1
    cents_string = str(cents)
    if cents >= 0:
        cents_string = '+' + cents_string
    return tone_label + cents_string


def get_clustered_peaks(peak_dict):
    cluster_array = []
    for frequency in sorted(peak_dict):
        cluster = Cluster()
        cluster.start_frequency = frequency
        cluster.end_frequency = frequency
        cluster.max_amplitude = peak_dict[frequency]
        cluster.frequency_of_max_amplitude = frequency
        add_cluster = True
        for clust in cluster_array:
            if clust.contains_cluster(cluster):
                clust.append_cluster(cluster)
                add_cluster = False
        if add_cluster:
            cluster_array.append(cluster)
    result_dict = {}
    for cluster in cluster_array:
        result_dict[cluster.max_amplitude] = cluster.frequency_of_max_amplitude
    return result_dict


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
                peak_dict[i] = fft_res[i]
        peaks = get_clustered_peaks(peak_dict)
        for amplitude in sorted(peaks, reverse=True):
            if len(segment.peaks) < 3:
                segment.peaks.append(peaks[amplitude])
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
        # if segment.start_time < 10.0:
        #     print(str(0), end='')
        print(segment.start_time, '-', segment.end_time, end=' ', sep='')
        # if segment.end_time < 10.0:
        #     print(str(0), end='')
        # print(segment.end_time, end=' ')
        for p in sorted(segment.peaks):
            print(get_tone(int(a_reference), p), end=' ')
        print()


if __name__ == "__main__":

    if len(sys.argv) == 3:
        music(sys.argv[1], sys.argv[2])
        # print(get_tone(int(sys.argv[1]), int(sys.argv[2])))
    else:
        print("Wrong number of arguments")
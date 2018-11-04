#!/usr/bin/python3
import sys
import numpy as np
import wave
import struct
# import matplotlib.pyplot as plt


def peaks(file):
    wave_stream = wave.open(file, 'rb')

    frame_rate = wave_stream.getframerate()
    num_frames = wave_stream.getnframes()
    num_channels = wave_stream.getnchannels()
    # print('frame rate:', frame_rate)
    # print('number of frames:', num_frames)
    # print('number of channels:', num_channels)

    p = 1
    n = frame_rate * p
    total_samples = num_frames * num_channels
    sample_width = wave_stream.getsampwidth()

    num_windows = int(num_frames / n)
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

    low = None
    high = None
    for index in range(0, num_windows):
        start = index * n
        end = start + n
        data_window = integer_data[start:end]
        fft_res = np.abs(np.fft.rfft(a=data_window, n=int(n)))
        # freqs = np.fft.rfftfreq(len(data_window))
        # freqs = freqs * frame_rate
        freqs = np.arange((len(data_window) / 2) + 1) / (float(len(data_window)) / frame_rate)
        # freqs = np.arange((n / 2) + 1) / (float(n) / frame_rate)
        # print('data window len:', len(data_window))
        # print('fft len:', len(fft_res))
        # print('freqs len:', len(freqs))
        window_avg = sum(fft_res) / len(fft_res)
        # print('window_avg:', window_avg)
        for i in range(0, len(fft_res)):
            if fft_res[i] >= 20 * window_avg:
                freq = freqs[i]
                if low is not None:
                    if freq < low:
                        low = freq
                else:
                    low = freq
                if high is not None:
                    if freq > high:
                        high = freq
                else:
                    high = freq
    if low is None or high is None:
        print('no peaks')
    else:
        print('low = ', int(low), end='')
        print(', high = ', int(high))

    # print('ints:', integer_data)
    # res = np.abs(np.fft.rfft(integer_data, int(total_samples/2)))
    # avg = sum(res) / len(res)
    # print('res:',res)
    # print(avg)
    # print(len(res))
    # for amp in res:
    #     if amp > 20 * avg:
    #         print(amp)
    # np.rfft()



if __name__ == "__main__":

    if len(sys.argv) == 2:
        peaks(sys.argv[1])
    else:
        print("Wrong number of arguments")
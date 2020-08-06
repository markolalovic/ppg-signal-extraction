#!/usr/bin/python3
# save-measurement.py - Reads a sequence of images and stores it's PPG signal to:
#   ../data/df-ac-measurements.csv

from PIL import Image
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import time
import os, sys, os.path, shutil
import csv

def get_image(image_path):
    '''
    Return a numpy array of red image values so that we can access values[x][y]
    '''
    image = Image.open(image_path)
    width, height = image.size
    red, green, blue = image.split()
    red_values = list(red.getdata())
    return np.array(red_values).reshape((width, height))

def get_mean_intensity(image_path):
    '''
    Return mean intensity of an image values
    '''
    image = get_image(image_path)
    return np.mean(image)

def plot(x):
    '''
    Plot the signal
    TODO: Vertical flip and plot a normal PPG signal instead of an inverted one
    '''
    fig = plt.figure(figsize=(13, 6))
    ax = plt.axes()
    ax.plot(list(range(len(x))), x)
    plt.show()

def get_signal_from(dirname='sample'):
    '''
    Return the AC component of a signal from the recording, i.e. the sequence
    of images
    '''
    length = len(os.listdir('../data/' + dirname))
    t = list(range(length))
    x = []

    for i in range(length):
        image_path = '../data/%s/image%s.jpg' %(dirname, i,)
        print('reading image: ' + image_path)
        x.append(get_mean_intensity(image_path))

    t = np.array(t).reshape((-1, 1))
    x = np.array(x)
    model = LinearRegression()
    model.fit(t, x)
    # calculate trend (DC component)
    model = LinearRegression().fit(t, x)
    x_pred = model.predict(t)
    trend = list(x_pred)
    x = list(x)
    detrended = [x[i] - trend[i] for i in range(length)]

    return detrended

if __name__ == "__main__":
    dirname = 'recording'
    x = get_signal_from(dirname)
    plot(x)

    if input('Save it? (y/n): ') == 'y':
        filename = '../data/df-ac-measurements.csv'
        if os.stat(filename).st_size == 0:
            # write header
            with open(filename, 'a') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'sys', 'dia', 'hr'] \
                    + ['x'+str(i) for i in range(len(x))])

        timestr = time.strftime("%Y-%m-%d-%H:%M:%S")
        pid = input('ID: ')  # e.g. 0
        sys = input('SYS: ') # e.g. 116
        dia = input('DIA: ') # e.g. 59
        hr = input('HR: ')   # e.g. 55

        fields = [str(pid), timestr, str(sys), str(dia), str(hr)] \
            + [str(elt) for elt in x]
        with open(filename, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(fields)

    try:
        shutil.rmtree('../data/' + dirname)
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))

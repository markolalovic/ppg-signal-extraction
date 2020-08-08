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

def get_signal_from(device):
    '''
    Return PPG signal as a sequence of mean intensities from the sequence of
    images that were captured by a device (NoIR camera or iphone camera)
    '''
    if device == 'noir':
        length = len(os.listdir('../data/recording'))
        x = []
        for i in range(length):
            image_path = '../data/recording/image%s.jpg' %(i,)
            print('reading image: ' + image_path)
            x.append(get_mean_intensity(image_path))
        return x
    else:
        images = os.listdir('../data/iphone/')
        numbers = [image[3:][:-4] for image in images]
        numbers = [int(n) for n in numbers]
        numbers = sorted(numbers)
        length = len(numbers)

        x = []
        for n in numbers:
            image_path = '../data/iphone/out' + str(n) + '.png'
            print('reading image: ' + image_path)
            x.append(get_mean_intensity(image_path))
        return x

def get_detrended(x):
    length = len(x)
    t = list(range(length))
    t = np.array(t).reshape((-1, 1))
    x = np.array(x)
    model = LinearRegression()
    model.fit(t, x)

    # calculate the trend (DC component)
    model = LinearRegression().fit(t, x)
    x_pred = model.predict(t)
    trend = list(x_pred)
    x = list(x)
    detrended = [x[i] - trend[i] for i in range(length)]
    return detrended

if __name__ == "__main__":
    device = input('device (noir, iphone): ')
    x = get_signal_from(device)
    plot(x)

    if input('Save it? (y/n): ') == 'y':
        filename = '../data/df-ac-measurements.csv'
        if os.stat(filename).st_size == 0:
            # write header
            with open(filename, 'a') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'date', 'device', 'sys', 'dia', 'hr'] \
                    + ['x'+str(i) for i in range(len(x))])


        pid = input('ID: ')  # e.g. 0
        if device == 'noir':
            dev = 'Pi NoIR Camera V2'
        else:
            dev = 'iPhone 6s'
        timestr = time.strftime("%Y-%m-%d-%H:%M:%S")
        sys = input('SYS: ') # e.g. 116
        dia = input('DIA: ') # e.g. 59
        hr = input('HR: ')   # e.g. 55

        fields = [str(pid), timestr, dev, str(sys), str(dia), str(hr)] \
            + [str(elt) for elt in x]
        with open(filename, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(fields)

    if device == 'noir':
        try:
            shutil.rmtree('../data/recording')
        except OSError as e:
            print ('Error: %s - %s.' % (e.filename, e.strerror))
    else:
        for filename in os.listdir('../data/iphone'):
            file_path = os.path.join('../data/iphone', filename)
            try:
                os.unlink(file_path)
            except Exception as e:
                print('Error: %s - %s.' % (file_path, e))

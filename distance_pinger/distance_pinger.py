#!/usr/bin/python3

from argparse import ArgumentParser
from datetime import datetime
from io import BufferedReader, TextIOWrapper
from signal import SIGHUP, SIGINT, SIGQUIT, SIGTERM, signal
from time import sleep, time

import RPi.GPIO as GPIO
from serial import Serial

TRIG = 13
ECHO = 19
VALID_DISTANCE_RANGE = 2, 400

time_index = 1
# latitude_index = 2
# latitude_direction_index = 3
# longitude_index = 4
# longitude_direction_index = 5
fix_quality_index = 6
# altitude_index = 9
# altitude_units_index = 10
needed_indexes = [1, 2, 3, 4, 5, 9, 10]


def end_process(signum=None, frame=None):
    print('Cleaning up GPIO...', end='')
    GPIO.cleanup()
    print(' done.')

    exit(0)


def parse_arguments():
    # Construct the argument parser
    ap = ArgumentParser()

    # Add the arguments to the parser
    ap.add_argument('-f', '--file', required=True,
                    help='Data file to write the results to (written in CSV format)')

    ap.add_argument('-l', '--log', default='distance_logger.log',
                    help='Log file')

    ap.add_argument('-t', '--timeout', default=5, type=float,
                    help='Timeout in seconds for getting GPS and distance data')

    ap.add_argument('-o', '--offset', default=0.5, type=float,
                    help='Sensor calibration distance')

    ap.add_argument('-c', '--count', default=20, type=int,
                    help='Calculate mean distance from COUNT samples')

    return vars(ap.parse_args())


def log(path, data, append=True):
    date_time = datetime.now().strftime("%Y-%m-%d,%H:%M:%S,")

    with open(path, 'a' if append else 'w') as log_file:
        log_file.write(date_time + str(data))
        # print(date_time + str(data))


def get_distance(trig, echo, offset):
    pulse_end = 0
    pulse_start = 0

    # Get distance measurement
    GPIO.output(trig, GPIO.LOW)            # Set TRIG LOW
    # Min gap between measurements
    sleep(0.1)
    # Create 10 us pulse on TRIG
    GPIO.output(trig, GPIO.HIGH)           # Set TRIG HIGH
    sleep(0.00001)                              # Delay 10 us
    GPIO.output(trig, GPIO.LOW)            # Set TRIG LOW

    # Measure return echo pulse duration
    while GPIO.input(echo) == GPIO.LOW:
        pulse_start = time()

    while GPIO.input(echo) == GPIO.HIGH:
        pulse_end = time()

    # Distance = 17160.5 * Time (unit cm) at sea level and 20C
    distance = (pulse_end - pulse_start) * 17160.5
    # distance = round(distance, 2)
    return distance + offset


def get_mean_distance(count, trig, echo, offset, timeout):
    end_time = time() + timeout

    i = 0
    distances = []
    while i < count and time() < end_time:
        dist = get_distance(trig, echo, offset)
        if VALID_DISTANCE_RANGE[0] <= dist <= VALID_DISTANCE_RANGE[1]:
            distances.append(dist)
            i += 1

    return sum(distances) / len(distances) if i > 0 else 0


def get_gps_data(serial_IO, timeout):
    end_time = time() + timeout
    print(time())
    print(end_time)

    while time() < end_time:
        try:
            line = serial_IO.readline()
        except:
            continue

        if len(line) < 6 or line[0:6] != '$GPGGA':
            continue

        gps_data = line.split(',')

        if int(gps_data[fix_quality_index]) > 0:
            return gps_data

    return ['' for _ in needed_indexes]


def main():
    args = parse_arguments()
    gps_data = []

    # Assign handler for process exit
    signal(SIGTERM, end_process)
    signal(SIGINT, end_process)
    signal(SIGHUP, end_process)
    signal(SIGQUIT, end_process)

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)

    distance = get_mean_distance(
        args['count'], TRIG, ECHO, args['offset'], args['timeout'])

    log(args['log'],
        'TRIG - {0}, ECHO - {1}, Offset: {2} cm\n'.format(TRIG, ECHO, args['offset']))

    try:
        with Serial(port='/dev/serial0', baudrate=9600, timeout=args['timeout']) as serialPort:
            while not gps_data:
                gps_data = get_gps_data(TextIOWrapper(
                    BufferedReader(serialPort)), args['timeout'])
                # Format GPS time to readable format
                gps_data[time_index] = '{}:{}:{}'.format(
                    gps_data[time_index][0:2].zfill(2), gps_data[time_index][2:4].zfill(2), gps_data[time_index][4:6].zfill(2))
                # Filter only needed data
                gps_data = [gps_data[i] for i in needed_indexes]
    except Exception as e:
        log(args['log'], 'Error: {}\n'.format(e))

    log(args['file'], '{:.2f},{}\n'.format(distance, ','.join(gps_data)))
    end_process()


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Create a recording with arbitrary duration.

"""
import argparse         #to club arguments
import tempfile         
import queue
import sys

import sounddevice as sd    
import soundfile as sf
import numpy  # Make sure NumPy is loaded before it is used in the callback
assert numpy  # avoid "imported but unused" message (W0611)


def int_or_str(text):                           
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


parser = argparse.ArgumentParser(add_help=False)            #creates a container to hold args (add_help false removes the description of all args)
parser.add_argument(
    '-l', '--list-devices', action='store_true',            #file name -l presents list of devices
    help='show list of audio devices and exit')
args, remaining = parser.parse_known_args()                 #ask inputs
if args.list_devices:                                       #if input contains -l
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(                           #new container
    description=__doc__,                                    #sets the premade comments as description 
    formatter_class=argparse.RawDescriptionHelpFormatter,   
    parents=[parser])
parser.add_argument(
    'filename', nargs='?', metavar='FILENAME',              #attach filename
    help='audio file to store recording to')
parser.add_argument(                                        #show devices
    '-d', '--device', type=int_or_str,
    help='input device (numeric ID or substring)')
parser.add_argument(                                        #set sampling rate
    '-r', '--samplerate', type=int, help='sampling rate')
parser.add_argument(                                        #set no of channels
    '-c', '--channels', type=int, default=1, help='number of input channels')
parser.add_argument(                                        #set file sub-type
    '-t', '--subtype', type=str, help='sound file subtype (e.g. "PCM_24")')
args = parser.parse_args(remaining)                         #the left out arguments from line 28

q = queue.Queue()


def callback(indata, frames, time, status): 
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(indata.copy())


try:
    if args.samplerate is None:                                     #sets a default rate if not set
        device_info = sd.query_devices(args.device, 'input')
        # soundfile expects an int, sounddevice provides a float:
        args.samplerate = int(device_info['default_samplerate'])            


    if args.filename is None:                                           #makes a temp audio file
        args.filename = tempfile.mktemp(prefix='delme_rec_unlimited_',
                                        suffix='.wav', dir='')

    # Make sure the file is opened before recording anything:
    with sf.SoundFile(args.filename, mode='x', samplerate=args.samplerate,  #opens file (file handling)
                      channels=args.channels, subtype=args.subtype) as file:
        with sd.InputStream(samplerate=args.samplerate, device=args.device, #inputs stream
                            channels=args.channels, callback=callback):
            print('#' * 80)
            print('press Ctrl+C to stop the recording')                         #ctrl-c is to terminate a command in terminal
            print('#' * 80)
            while True:
                file.write(q.get())

except KeyboardInterrupt:
    print('\nRecording finished: ' + repr(args.filename))
    parser.exit(0)
except Exception as e:
    parser.exit(1, type(e).__name__ + ': ' + str(e))

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
    
q=queue.Queue()

def callback(indata, frames, time, status): 
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(indata.copy())


filename=str(input("enter file name"))
try:

    with sf.SoundFile(filename, mode='x', samplerate=16000,  #opens file in x mode (create file) (file handling)
                      channels=1) as file:
        with sd.InputStream(samplerate=16000, #inputs stream
                            channels=1, callback=callback):
            print('#' * 80)
            print('press Ctrl+C to stop the recording')                         #ctrl-c is to terminate a command in terminal
            print('#' * 80)
            while True:
                file.write(q.get())


except KeyboardInterrupt:
    print("recorded")
    

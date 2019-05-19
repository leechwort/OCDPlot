#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Simple openocd variable monitor
#
# Copyright (c) 2019 Artem Synytsyn
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
import telnetlib
import argparse
import re
from ctypes import *

from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

class OpenOCD:
    """Low-level communication class"""
    def __init__(self, host="localhost", port=4444):
        self.tn = telnetlib.Telnet(host, port)
        # Read initial invitation message from OpenOCD
        self.tn.read_until(b"> ")
    def close_connection(self):
        self.tn.close()
    def reset_target(self):
        """Perform as hard a reset as possible, using SRST if possible"""
        self.tn.write(b"reset\n")
        self.tn.read_until(b"> ")
        
    def mdw(self, address):
        """Display contents of address, as 32-bit words (openocd mdw command)"""
        self.tn.write(b"mdw " + address + b"\n");
        output = self.tn.read_until(b"> ")
        result = None
        try:  
            result = re.search(b": (.*) \r\n\r> ", output).group(1)
        except AttributeError:
            result = b'0'
        return result
    
    def mdh(self, address):
        """Display contents of address, as 16-bit words (openocd mdh command)"""
        self.tn.write(b"mdh " + address + b"\n");
        output = self.tn.read_until(b"> ")
        result = None
        try:  
            result = re.search(b": (.*) \r\n\r> ", output).group(1)
        except AttributeError:
            result = b'0'
        return result
    
    def mdb(self, address):
        """Display contents of address, as 8-bit bytes (openocd mdb command)"""
        self.tn.write(b"mdb " + address + b"\n");
        output = self.tn.read_until(b"> ")
        result = None
        try:  
            result = re.search(b": (.*) \r\n\r> ", output).group(1)
        except AttributeError:
            result = b'0'
        return result

def convert(raw_string, variable_type):
    """
    Converts bytestring like this b'12345678' to selected type
    variable_type: {c_float, c_int, ...}
    Solution Was taken from there https://stackoverflow.com/a/1592200/3132844 
    TODO: Shoud we rewrite this in more elegant way?
    """
    int_value = int(raw_string, 16)  # convert from hex to a Python int
    cp = pointer(c_int(int_value))   # make this into a c integer
    # cast the int pointer to selected value
    fp = cast(cp, POINTER(variable_type))  
    return fp.contents.value         # dereference the pointer, get the value
        
def init():
    ax.set_xlim(0, 30)
    ax.set_xlabel("Samples")
    ax.grid()
    return ln,

def update(frame, address, variable_type):
    new_y_data = convert(openocd.mdw(address), variable_type)
    xdata.append(frame)
    ydata.append(new_y_data)
    print("Sample: %d; Value: " % frame, end='')
    print(new_y_data)
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    if new_y_data < ymin:
        ax.set_ylim(new_y_data, ymax)
        ax.figure.canvas.draw()
    if new_y_data > ymax:
        ax.set_ylim(ymin, new_y_data)
        ax.figure.canvas.draw()
    if frame > xmax:
        xdata.clear()
        ydata.clear()
        ax.set_xlim(frame, max_samples + xmax)
        ax.figure.canvas.draw()
        
    ln.set_data(xdata, ydata)
    return ln,

variable_address = b'0x12345678'
variable_type = c_float
# Parse commandline arguments
parser = argparse.ArgumentParser()
parser.add_argument("-a","--address", type=str,
                    help="variable address, e.g. 0x12345678")
parser.add_argument("-t", "--type", type=str,
                    help="variable type <float, uint32_t, int32_t>")
parser.add_argument("-n", "--interval", type=int, default=1000,
                    help="milliseconds between updates")
args = parser.parse_args()

if args.address and args.type:
    if args.type == 'float':
        variable_type = c_float
    elif args.type == 'int32_t':
        variable_type = c_int32
    elif args.type == 'uint32_t':
        variable_type = c_uint32
    variable_address = args.address.encode("utf-8")

    openocd = OpenOCD()
    openocd.reset_target()  
    
    # On window close event  
    def handle_close(evt):
        openocd.close_connection()
        
    fig, ax = plt.subplots()
    xdata = []
    ydata = []
    ln, = plt.plot([], [], 'ro-')
    max_samples = 30
    
    fig.canvas.mpl_connect('close_event', handle_close)
    fig.canvas.set_window_title('OCDPlot')
    
    ani = FuncAnimation(fig, update,
                        init_func=init, blit=True, interval=args.interval, 
                        fargs=(variable_address, variable_type))
    plt.show()

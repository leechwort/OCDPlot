# OCDPlot
Realtime plotting tool for OpenOCD gdb server

Small utility, which connects to OpenOCD server and can plot selected variable

![Imgur](https://i.imgur.com/4lukjYb.png)

```bash
$ ./ocdplot.py --help
usage: ocdplot.py [-h] [-a ADDRESS] [-t TYPE] [-n INTERVAL]

optional arguments:
  -h, --help            show this help message and exit
  -a ADDRESS, --address ADDRESS
                        variable address, e.g. 0x12345678
  -t TYPE, --type TYPE  variable type <float, uint32_t, int32_t>
  -n INTERVAL, --interval INTERVAL
                        milliseconds between updates
```

Example of usage:
```bash
$ ./ocdplot.py -a 0x40000024 -t uint32_t -n 100
```
This will read value of `TIM2->CNT` register in my STM32F101RCT6 microcontroller. OpenOCD server should be 
already started and connected to target.

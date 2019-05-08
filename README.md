# adm - Acoustic Directivity Measurement
**Made for faster acoustic directivity measurements.**

This Graphical User Interface ensures the generation and the acquisition of mutiple I/O audio signals while enslaving an electronic turn table via an [Arduino Nano](https://store.arduino.cc/arduino-nano).

<img src="pictures/ScreenCapture.png">

_Only tested with the [ET250-3D Electronic Turn Table from Outline](https://outline.it/outline-products/measurement-systems/et-250-3d/) yet._

## Installation
Adm runs with Python 3.7 and depends on [PyQt5](https://pypi.org/project/PyQt5/), [pyqtgraph](http://www.pyqtgraph.org/), [numpy](https://www.numpy.org/), [pyaudio](https://pypi.org/project/PyAudio/), [serial](https://pypi.org/project/serial/) and [wave](https://docs.python.org/3/library/wave.html#module-wave). 

To install the libraries, clone this repository and in that directory execute:
```sh
python3 -m pip install -r requirements.txt
```

## About this project
Created by [Tom Aubier](https://github.com/Tomaubier) and [Raphaël Dumas](https://github.com/DumasRaphael) for a project first initiated at [Le Mans University](http://www.univ-lemans.fr/fr/index.html).


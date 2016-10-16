# Deep Music

## Installation
Requirements:
- [TensorFlow](https://www.tensorflow.org/)
- [Keras](https://keras.io/)
- [seq2seq](https://github.com/farizrahman4u/seq2seq)
- [Recurrent Shop](https://github.com/datalogai/recurrentshop)
- [Python Midi](http://https://github.com/vishnubob/python-midi) / pip install python-midi

## MIDI Input Details
Every input vector x is 66-dimensional and structured as follows:
- x[0]: relative event time from previous input (tick)
- x[1]: BPM
- x[2-5]: Channel 1: font, note, velocity, duration
- x[6-9]: Channel 2
- ...
- x[62-65]: Channel 16

In MIDI, an event is characterized by the following features:
- Font: Integer in [0,127]
- Note: Integer in [0,127]
- Velocity: Integer in (0,infinity)
- Duration: Integer in (0,infinity)

We use a -1 in all features to indicate a rest.

## Resources
* [The Neural Network Zoo](http://www.asimovinstitute.org/neural-network-zoo/)

* [Analyzing Six Deep Learning Tools for Music Generation](http://www.asimovinstitute.org/analyzing-deep-learning-tools-music/)

* [Composing Music With Recurrent Neural Networks: Theory](http://www.hexahedria.com/2015/08/03/composing-music-with-recurrent-neural-networks/)
* [Composing Music With Recurrent Neural Networks: Code](https://github.com/hexahedria/biaxial-rnn-music-composition)
* [Composing Music With Recurrent Neural Networks: Extensions](http://www.hexahedria.com/2016/08/08/summer-research-on-the-hmc-intelligent-music-software-team)

* [Magenta: Blog](https://magenta.tensorflow.org/)
* [Magenta: Code](https://github.com/tensorflow/magenta)

* [Keras](https://keras.io/)
* [Sequence to Sequence Learning with Keras](https://github.com/farizrahman4u/seq2seq)

* [About MIDI](http://stackoverflow.com/questions/14448380/how-do-i-read-a-midi-file-change-its-instrument-and-write-it-back)
* [Python MIDI Library](https://github.com/vishnubob/python-midi)

* [Free MIDI Files](http://www.mididb.com/genres/)

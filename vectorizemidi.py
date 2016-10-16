import midi
import numpy as np

class MidiContainer:
    '''
    The MidiContainer class contains a vector representation of 
    the midi track to be fed to our neural net. It is a 67 x n matrix,
    contents specified in the README. 
    '''
    def __init__(self):
        self.data = np.array([], dtype=np.int64).reshape(6,0) #todo change this to 3+16*4
        self.curr_bpm = 120
        self.curr_instrument = 0
        self.abs_time = 0
        self.active_pitches = {} #[pitch] = (velocity, time note was turned on)
        
    def note_to_vector(self, pitch, time):
        velocity = self.active_pitches[pitch][0]
        note_start = self.active_pitches[pitch][1]
        return np.vstack((self.curr_instrument, pitch, velocity, time + self.abs_time - note_start))
    
    def add_data(self, note_vector, note_start):
        event_column = np.vstack((note_start, self.curr_bpm, note_vector))
        self.data = np.hstack((self.data, event_column))
    
def midi_to_vector(fname):
    '''
    Given a filename of a midi to read, returns a MidiContainer object of its vector representation.
    '''
    pattern = midi.read_midifile(fname)
    midi_vector = MidiContainer()
    for track in pattern:
        for event in track:
            if isinstance(event, midi.SetTempoEvent): 
                midi_vector.curr_bpm = event.get_bpm()
            if isinstance(event, midi.EndOfTrackEvent): #first metadata track
                continue 
            if isinstance(event, midi.ProgramChangeEvent):
                midi_vector.curr_instrument = event.get_value()
            if isinstance(event, midi.NoteOnEvent):
                midi_vector.abs_time += event.tick
                midi_vector.active_pitches[event.get_pitch()] = (event.get_velocity(), midi_vector.abs_time)
            if isinstance(event, midi.NoteOffEvent):
                pitch = event.get_pitch()
                time = event.tick
                if pitch in midi_vector.active_pitches:
                    note_vec = midi_vector.note_to_vector(pitch, time)
                    midi_vector.add_data(note_vec, midi_vector.active_pitches[pitch][1]) #ugh bad data abstraction
                    midi_vector.active_pitches.pop(pitch, None)
                    midi_vector.abs_time += event.tick
                
    return midi_vector    


fname = ''
while fname == '':
	fname = raw_input("Filename of midi to convert: ")
vectorized = midi_to_vector(fname)
print "Here's the end data: \n", vectorized.data
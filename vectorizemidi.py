import midi
import numpy as np
class MidiContainer:
    '''
    The MidiContainer class contains a vector representation of 
    the midi track to be fed to our neural net. It is a 67 x n matrix,
    contents specified in the README. 
    '''
    def __init__(self):
        self.data = np.array([], dtype=np.int64).reshape(66,0) 
        self.curr_bpm = 120
        self.curr_instrument = 0
        self.abs_time = 0
        self.active_pitches = {} #[pitch] = (velocity, time note was turned on)
        
    def note_to_vector(self, pitch, time):
        velocity = self.active_pitches[pitch][0]
        note_start = self.active_pitches[pitch][1]
        return np.vstack((self.curr_instrument, pitch, velocity, time + self.abs_time - note_start))
    
    def add_data(self, note_vector, note_start):
        event_column = np.vstack((note_start, self.curr_bpm, note_vector, np.ones((60,1))*-1))
        self.data = np.hstack((self.data, event_column))
    
    def combine_tracks(self):
        self.data = self.data.T[self.data.T[:, 0].argsort()].T #maybe we dont need so many transposes
        prev_duration = -1
        edit_index = 0 
        i = 0
        delete_this = []
        old_inst = self.data[2,0]
        for col in self.data.T:
            curr_duration = col[0]
            if curr_duration == prev_duration:
                for ni in xrange(2,67,4):
                    note_vec = col[ni:ni+4]
                    curr_inst = note_vec[0] if note_vec.any() else 0
                    if np.sum(note_vec) > 0 and curr_inst != old_inst:
                        i_rep = np.where(self.data[5:,edit_index] == 0)[0][0]+5
                        self.data[i_rep:i_rep+4, edit_index] = note_vec
                        delete_this.append(i)
            else:
                old_inst = col[2]
                edit_index = i
            i += 1 
            prev_duration = curr_duration
            
        mask = np.ones(self.data.shape, np.bool)
        mask[:,delete_this] = 0
        self.data = self.data[mask].reshape(66,-1)
    
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
    midi_vector.combine_tracks()             
    return midi_vector    

def vector_to_midi(vector):
    '''Given a np array (vector.data), returns a python midi pattern'''
    pattern = midi.Pattern(resolution=960)
    #first, separate tracks
    tracklist = []
    for i in xrange(2,vector.shape[0],4):
        track = vector[i:i+4,:]
        if np.sum(track) > 0:
            tracklist.append(np.vstack((vector[0:2], track)))
   
    for track in tracklist:
        miditrack = midi.Track()
        pattern.append(miditrack)
        bpm = track[1,0]
        tempoevent = midi.SetTempoEvent(tick=0, bpm=bpm)
        miditrack.append(tempoevent)
        instrument = int(track[2,0])
        fontevent = midi.ProgramChangeEvent(tick=0, value=instrument)
        miditrack.append(fontevent)
        if not np.array_equal(bpm * np.ones(track.shape[1]), track[1,:]):
            print 'Tempo changes. Code assumes it doesn\'t. Contact Jingyi.'
        
        event_tick = 0   
        track_duration = np.max(track[0,:] + track[-1,:])
        active_notes = {}
        start_times = track[0,:]
        for t in xrange(0, int(track_duration)+1):
            for pitch in active_notes:
                active_notes[pitch] -= 1
            
            negs = [k for k,v in active_notes.iteritems() if v < 0]
            for n in negs:
                active_notes.pop(n)
                
            if 0 in active_notes.values():
                pitches = [k for k,v in active_notes.iteritems() if v == 0]
                for pitch in pitches:
                    off = midi.NoteOffEvent(tick=t - event_tick, pitch=pitch)
                    miditrack.append(off)
                    active_notes.pop(pitch)
                    event_tick = t
                    #relatively subtract
                    for pitch in active_notes:
                        active_notes[pitch] -= event_tick
                    if active_notes:
                        if sum(active_notes.itervalues()) > 0:
                            start_times -= event_tick
                            event_tick = 0
                    
            #run through track to add on/off events
            if t in start_times:
                ni = np.where(t == start_times)
                for n in ni[0]:
                    note = track[:, n]
                    start_time = int(note[0])
                    pitch = int(note[3])
                    velocity = int(note[4])
                    duration = int(note[5])
                    active_notes[pitch] = duration
                    on = midi.NoteOnEvent(tick = t - event_tick, velocity=velocity, pitch=pitch)
                    miditrack.append(on)
                    event_tick = start_time
                    
        miditrack.append(midi.EndOfTrackEvent(tick=0))
    return pattern



fname = ''
while fname == '':
    fname = raw_input("Filename of midi to convert: ")
vectorized = midi_to_vector(fname)
print "Here's the end data: \n", vectorized.data
pattern = vector_to_midi(vectorized.data)
fout = ''
while fout == '':
    fout = raw_input("Filename to send output midi: ")
if '.mid' in fout:
   fout = fout[:-4] 
midi.write_midifile(fout+'.mid', pattern)
print "Saved to " + fout+".mid - Verify it's the same as the original"
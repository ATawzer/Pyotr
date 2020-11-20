import music21 as m21
import os

# Classes
class MidiEncoder:
    """
    Encoder object containing many different encoding options for midi files to be fed into models.
    """
    def __init__(self):
        """
        The encoder is initialized without any porameters. Once initilized just pass a midi file into
        .Encode(), specifying a type of encoding and it will be returned encoded.
        """
        # function map
        self.encoder_map = {
            'pitch_position_strings': self.pitch_position_strings,
            'pitch_position_duration_strings': self.pitch_position_duration_strings
        }

    # Core function for calling encoders
    def Encode(self, midi, enc_type='pitch_position_strings'):
        """
        Function to call to encode a m21.Score object
        :param midi: parsed m21 midi file (or measure)
        :param enc_type: type of encoding to apply, run MidiEncoder().encoder_map.keys() to see supported types
        :return: encoded object, type depends on encoder used
        """
        if enc_type in self.encoder_map.keys():
            return self.encoder_map[enc_type](midi)
        else:
            raise ValueError("Encoding Type not Found, see MidiEncoder().encoder_map for supported types.")

    # Encoders
    def pitch_position_strings(self, midi):
        """
        Turns midi file or measure into a string token, '<pitch>:<offset>'.
        Offset is relative to input, either offset in song or measure
        :param midi: file to encode
        :return: list of encoded string tokens
        """
        encoded_string = []
        for n in midi.notes:
            if type(n) == m21.note.Note:
                encoded_string.append(str(n.pitch) + ':' + str(n.offset))
            elif type(n) == m21.chord.Chord:
                for i in range(0, len(n)):
                    encoded_string.append(str(n[i].pitch) + ':' + str(n[i].offset))
            else:
                print("No Notes Detected.")
        return encoded_string

    def pitch_position_duration_strings(self, midi):
        """
        Turns midi file or measure into a string token, '<pitch>:<offset>:<duration in quarter notes>'.
        Offset is relative to input, either offset in song or measure
        :param midi: file to encode
        :return: list of encoded string tokens
        """
        encoded_string = []
        for n in midi.notes:
            if type(n) == m21.note.Note:
                encoded_string.append(str(n.pitch) + ':' + str(n.offset) + ':' + str(n.duration.quarterLength))
            elif type(n) == m21.chord.Chord:
                for i in range(0, len(n)):
                    encoded_string.append(
                        str(n[i].pitch) + ':' + str(n[i].offset) + ':' + str(n[i].duration.quarterLength))
            else:
                print("No Notes Detected.")
        return encoded_string

class MidiWriter:
    """
    Class for writing midi files from encoded formats
    """
    def __init__(self, output='./data/generated'):
        """
        call .Write() to perform decoding process
        :param output: directory to write decoded files to, if None will only be returned
        """
        self.output = output
        self.midi = m21.stream.Stream()

        # function map
        self.decoder_map = {
            'pitch_position_strings': self.pitch_position_strings,
            'pitch_position_duration_strings': self.pitch_position_duration_strings
        }

    # Core function
    def Write(self, mid_enc, enc_type, filename):
        """
        Main function used to perform decoding and writing process.
        :param mid_enc: Encoded midi file
        :param enc_type: Type of encoding on the file
        :return: m21 midi file (also writes to path if specified)
        """
        if enc_type in self.decoder_map.keys():
            self.string_to_stream(mid_enc, enc_type)
            if self.output is not None:
                self.midi.write('midi', self.output+'/'+filename)

            return self.midi

        else:
            raise ValueError("Encoding Type not Found, see MidiWriter().decoder_map for supported types.")

    def string_to_stream(self, mid_enc, enc_type):
        """
        Loops through tokens and applies the appropriate encoder to convert notes
        :param mid_enc: encoded midi file
        :param enc_type: type of encoding to apply
        :return: None, writes to object's midi file
        """
        # reset internal midi before writing to it
        self.midi = m21.stream.Stream()

        for enc_note in mid_enc:
            note = self.decoder_map[enc_type](enc_note)
            self.midi.insert(note.offset, note)

    # Take a token and convert note
    def pitch_position_duration_strings(self, token):
        """
        decoder for pitch_position_duration tokens
        :param token: encoded token to be converted to m21.note.Note object
        :return: m21.note.Note of token
        """
        info = token.split(":")
        note = m21.note.Note(info[0])
        note.offset = int(info[1].split('/')[0])/int(info[1].split('/')[1]) if '/' in info[1] else float(info[1])
        note.quarterLength = int(info[2].split('/')[0])/int(info[2].split('/')[1]) if '/' in info[2] else float(info[2])
        return note

    def pitch_position_strings(self, token):
        """
        decoder for pitch_position_duration tokens
        :param token: encoded token to be converted to m21.note.Note object
        :return: m21.note.Note of token
        """
        info = token.split(":")
        return m21.note.Note(info[0], offset=info[1])

# Other functions
def gen_md_from_path(mdir, **kwargs):
    """
    Automatic creation of a midi dictionary from all midi files in a path
    :param mdir: directory to read
    :param kwargs: arguments for processing the midi files
    :return: dictionary of files {'filename':m21 midi file}
    """
    mdict = {}
    for filename in os.listdir(mdir):
        if filename.endswith(".mid"):
            mdict[filename[:-4]] = {}
            mdict[filename[:-4]] = process_midi_file(mdir + '/' + filename, **kwargs)
        else:
            continue

    return mdict

def null_func(*k):
    return None

def process_midi_file(path, transpose=True, by_measure=True, verbose=True):
    """
    function to read a .mid file on disk into a m21 object
    :param path: path of midi file
    :param transpose: whether to transpose the file to C
    :param by_measure: whether to make measures on the midi file
    :param verbose: whether to print the file's metadata as read-in
    :return: m21 midi file
    """
    vprint = print if verbose else null_func
    # read-in
    mid = m21.converter.parse(path)
    vprint(f"File Read in: {path[7:]}")

    # Make measures
    if by_measure:
        mid = m21.stream.makeNotation.makeMeasures(mid)
        vprint(f"Number of Measures: {len(mid)}")

    # Transpose
    if transpose:
        key = mid.analyze('key').tonic
        vprint(f"Detected Key: {key}")
        mid = mid.transpose(m21.interval.Interval(key, m21.pitch.Pitch('C')))

    return mid

# training prep
def gen_measure_train_set(mdict):
    return mdict



import glob
from tqdm import tqdm
import music21 as m21
import sys
import os

class MidiDataFrame:
    """
    MIDI as both an m21 file and a data-driven structure wrapped into one object. The purpose of the
    object is to help decompose MIDI files with an easy interface into the parts needed to be fed into
    Artificial music composition.
    """

    def __init__(self, path):
        """
        Simple Class for storing MIDI data as a dataframe and outputting for training
        :param path: Location on disk of the MIDI file to be parsed
        """
        self.path = path
        self.midi = m21.converter.parse(self.path)
        self.parts = m21.instrument.partitionByInstrument(self.midi)

        # Initilization of variables
        self.note_sequence = []

        # Populate object functions
        self.gen_note_sequence()

    def flatten_midi(self):
        """
        Often times easier to work with flattened parts, this function will do just that. Still works
        if no flattening needed
        :return: flattened midi file
        """
        # Flatten parts to one line
        flattened_parts = None
        if self.parts:
            flattened_parts = self.parts.parts[0].recurse()
        else:
            flattened_parts = self.midi.flat.notes

        return flattened_parts

    def gen_note_sequence(self):
        """
        Use the midi file and m21 package to turn the midi file into a sequence of character strings
        Written directly to self.note_sequence
        """
        # Build character string from flattened midi
        for element in self.flatten_midi():
            if isinstance(element, m21.note.Note):
                self.note_sequence.append(str(element.pitch))
            elif isinstance(element, m21.chord.Chord):
                self.note_sequence.append('.'.join(str(n) for n in element.normalOrder))


class MidiCollection:
    """
    MDF's in bulk, Tool wrapped around a MIDI Data-frame to allow for quick and easy use of MIDI files in
    Machine Learning. Given a directory of MIDI files, it will locate and construct the necessary data types
    to use the MIDI in Machine Learning and Music Composition. Functionality and syntax is meant to mirror
    the mdf as if the collection were just one combined MIDI file. An individual MDF can be accessed from
    the MidiCollection via indexing.

    Usage: Passing a directory only initializes the collection. To utilize the MIDI files just call the
    build method, which will officially parse and organize the MIDI files into Machine Learning ready data.
    This can be lengthy, hence the ability to disable if static functions are desired or reading in
    pre-processed MIDI from disk.
    """

    def __init__(self, dir, verbose=True, auto_build=True):

        self.dir = dir
        self.midi_files = [file for file in glob.glob(f"{self.dir}/*.mid")]
        self.verbose = verbose
        self.built = False

        # Initialization of variables
        self.mdf_list = []
        self.note_sequence = []

        # Initial Functions
        self.set_verbose()
        self.build() if auto_build else print("Caution: Collection not Built.")

    def __getitem__(self, item):
        return self.mdf_list[item]

    # Class Usage functions
    def set_verbose(self):
        if not self.verbose:
            sys.stdout = open(os.devnull, 'w')

    def build(self):
        """
        Run this function to properly read in and organize the MDF's. This function is called by default
        but can be avoided if user doesn't want to process the MIDI files in the directory.

        Future Work: More useful once the collection has the option to load from disk rather than reprocess
        each of the MIDI files. This will save time as MIDI libraries grow to massive sizes.
        """
        if self.built:
            print("MidiCollection already built.")
        else:
            print("Constructing MidiCollection Objects . . .")
            self.mdf_list = [MidiDataFrame(midi) for midi in tqdm(self.midi_files)]
            self.gen_note_sequence()

            print("MidiCollection Built.")

            self.built = True

    # Build Functions
    def gen_note_sequence(self):
        """
        Build Function that combines the MDF's in the MidiCollection into one note sequence.
        """
        for mdf in self.mdf_list:
            self.note_sequence.extend(mdf.note_sequence)

    # IO Functionality
    def save(self):
        """
        Writes the MidiCollection and pre-processed MDF's to disk for easy use in the future.
        """



def test():

    ind_track = r"D:\Documents\GitHub\Pyotr\MIDI Files\tch\tch_sym6m1.mid"
    testPath = r"D:\Documents\GitHub\Pyotr\MIDI Files\Piano Training"

    mc = MidiCollection(testPath, auto_build=True, verbose=True)
    print(mc.note_sequence)


test()
import pandas as pd
from py_midicsv import midicsv
from os import walk
from tqdm import tqdm

class MidiDataFrame:
    """
    Simple Class for storing a single midi file as nested dataframe and keeping contents organized.
    Implements a nested structure to keep musical elements from metadata elements
    """
    def __init__(self, path):
        self.path = path
        self.df = pd.DataFrame()

        # Function Initialization
        self.parse_midi_to_df()

    def parse_midi_to_df(self):
        """ Function for converting midi file in path to a pandas dataframe"""

        try:
            self.df = pd.DataFrame([line.split(", ") for line in midicsv.parse(self.path)])
        except:
            raise(IOError("Invalid Midi File, Midi df could not be parsed."))

    def nest_parsed_df(self):
        """ Nests the dataframes into different types of data"""

    def unnest_parsed_df(self):
        """ Unnests the dataframe into the self.df. Useful if writing midi file back out to drive"""

    def parse_df_to_midi(self, outpath):
        """ Writes the midi object back into a midi file, needs the directory of new file """

def parse_all_midi_files(midi_dir):
    """ Pyotr specific function where it will read in every midi file desired for training
    Arguments:
          directory containing all of the midi files
    Returns:
        list of MidiDataFrames
    """
    midi_list = []
    for (dirpath, dirnames, filenames) in walk(midi_dir):
        for file in filenames:
            midi_list.append(f"{dirpath}\\{file}")

    print("Parsing Midi Files . . .")
    mdf_list = [MidiDataFrame(midi) for midi in tqdm(midi_list)]
    return mdf_list

def Main():

    testPath = r"D:\Documents\GitHub\Pyotr\MIDI Files"
    print(parse_all_midi_files(testPath))

Main()
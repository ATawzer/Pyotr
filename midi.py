import pandas as pd
from py_midicsv import midicsv
from os import walk
from tqdm import tqdm
import numpy as np
import tensorflow as tf

class MidiDataFrame:

    def __init__(self, path):
        """
        Simple Class for storing MIDI data as a dataframe and keeping data clean.
        :param path: Location on disk of the MIDI file to be parsed
        """
        self.path = path
        self.df = pd.DataFrame()
        self.notes = pd.DataFrame()

        # Function Initialization
        self.parse_midi_to_df()
        self.split_parsed_df()
        self.convert_notes_to_matrix()

    def parse_midi_to_df(self):
        """ Function for converting midi file in path to a pandas dataframe"""

        try:
            self.df = pd.DataFrame([line.split(", ") for line in midicsv.parse(self.path)])
        except:
            raise(IOError("Invalid Midi File, Midi df could not be parsed."))

        # Name the columns
        columns = ['Track', 'Time', 'Type']
        for i in range(3, len(self.df.columns)):
            columns.append(f'TypeInfo{i}')

        self.df.columns = columns
        self.df.replace('\n', '', regex=True, inplace=True)

    def split_parsed_df(self):
        """ Nests the dataframes into different types of data
        Notes: Dataframe containing note-on/note-off events
        """

        # Notes
        notes_schema = {'track':int,
                  'time':int,
                  'type':str,
                  'channel':int,
                  'note':int,
                  'velocity':int}

        self.notes = self.df[(self.df.Type == 'Note_on_c') | (self.df.Type == 'Note_off_c')][self.df.columns[0:6]]
        self.notes.columns = notes_schema.keys()
        self.notes = self.notes.astype(notes_schema)

        # Misc. Controls

    def join_split_df(self):
        """ Unnests the dataframe into the self.df. Useful if writing midi file back out to drive"""

    def parse_df_to_midi(self, outpath):
        """ Writes the midi object back into a midi file, needs the directory of new file """

    def convert_notes_to_matrix(self):
        """
        Converts the notes dataframe into a n-dimensional array for later use
        :return: Converted Matrix
        """

        # Initialize a blank array
        matrix = []

        # For every unique track, add information as a triple
        for i in self.notes.track.unique():
            track_triples = []
            for j in self.notes[self.notes.track == i].index:
                event = [self.notes.loc[j, 'time'],
                          self.notes.loc[j, 'note'],
                          self.notes.loc[j, 'velocity']]
                track_triples.extend([event])
            matrix.append(track_triples)

        self.notes_matrix = np.ndarray(matrix)

def parse_all_midi_files(midi_dir):
    """ Pyotr specific function where it will read in every midi file desired for training
    :param midi_dir: directory containing all of the midi files
    :return: List of MidiDataFrames
    """

    midi_list = []
    for (dirpath, dirnames, filenames) in walk(midi_dir):
        for file in filenames:
            midi_list.append(f"{dirpath}\\{file}")

    print("Parsing Midi Files . . .")
    mdf_list = [MidiDataFrame(midi) for midi in tqdm(midi_list)]
    return mdf_list

def Main():

    ind_track = r"D:\Documents\GitHub\Pyotr\MIDI Files\tch\tch_sym6m1.mid"
    testPath = r"D:\Documents\GitHub\Pyotr\MIDI Files"
    mdf = MidiDataFrame(ind_track)
    #mdf_list = parse_all_midi_files(testPath)

    mdf.convert_notes_to_matrix()
    print(mdf.notes_matrix.shape)

Main()
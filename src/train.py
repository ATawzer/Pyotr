import pandas as pd
from .midi import *

class TrainingSet:

    def __init__(self, mdict_enc, num_notes, by_measure=True, build_type='next_note'):
        """
        Class to hold and access data for training in torch.
        This is wrapped around a TrainingSetBuilder object which
        does much of the data manipulation. This object makes getting
        information out of the prepared set much easier.
        :param mdict: dict of encoded midi objects
        :param by_measure: Whether the encoding was done by measure
        :param num_notes: Number of notes to include per training sample
        """

        self.mdict_enc = mdict_enc
        self.by_measure = by_measure
        self.num_notes = num_notes
        self.build_type = build_type

        # Initialized Attributes
        self.Xnp = None # numpy for X
        self.ynp = None # numpy for y
        self.tsg = TrainingSetBuilder()
        self.unique_tokens = []
        self.token_idx_map = {}
        self.idx_token_map = {}

        # build and setup the data
        self.build()

    def build(self):
        """
        Builds or Rebuilds TSG object and corresponding metadata if parameters or mdict has changed.
        :return:
        """
        self.tsg = TrainingSetBuilder(self.mdict_enc, num_notes=self.num_notes, by_measure=self.by_measure)
        self.Xnp, self.ynp = self.tsg.Build(build_type=self.build_type)
        self.gen_unique_tokens()
        self.gen_token_idx_maps()

    # Generation and initialization functions
    def gen_unique_tokens(self, flush=False):
        """
        Update unique_tokens attribute
        :param flush: Whether to clear unique_tokens if mdict updates, defaults to False
        :return: None
        """
        if flush:
            self.unique_tokens = []

        for piece in self.tsg.mdict_enc_f:
            for token in self.tsg.mdict_enc_f[piece]:
                if token not in self.unique_tokens:
                    self.unique_tokens.append(token)

    def gen_token_idx_maps(self, flush=True):
        """
        Generates a mapping from tokens to numbers
        :param flush: Whether to clear current map before changing, defaults to True
        :return: None, updates object
        """
        if flush:
            self.token_idx_map = {}
            self.idx_token_map = {}

        for i, token in enumerate(self.unique_tokens):
            self.token_idx_map[token] = i
            self.idx_token_map[i] = token

    def get_vocab_size(self):
        """
        Function for determining unique tokens in midi training data
        :return:
        """
        # Vocab Sizes
        return len(self.unique_tokens)

    def tokens_to_index(self):
        """
        Applys token to index mapping
        :return:
        """
        for i in range(0, self.get_vocab_size()):



class TrainingSetBuilder:

    def __init__(self, mdict_enc, num_notes=16, by_measure=False):
        """
        Class for managing the construction of training datasets for different target/train sets
        see TrainingSetBuilder().build_map for supported outputs.
        Methods will return numpy arrays
        :param mdict: dict of encoded midi objects
        :param by_measure: Whether the encoding was done by measure
        :param num_notes: Number of notes to include per training sample
        """

        self.mdict_enc = mdict_enc
        self.mdict_enc_f = mdict_enc if not by_measure else self.flatten_measures()
        self.by_measure = by_measure
        self.num_notes = num_notes
        self.build_map = {

            'next_note':self.build_next_note,
            'previous_note':self.build_previous_note,
        }

    # core functions
    def Build(self, build_type):
        """
        Function for building a dataframe of predictions
        :return:
        """
        if build_type in self.build_map.keys():
            return self.build_map[build_type]()
        else:
            raise ValueError("Build Type not Found, see TrainingSetBuilder().build_map for supported types.")

    # builder functions
    def build_next_note(self):
        """
        generate numpy arrays from the mdict object where next note is target
        :param num_notes: how many notes used to predict next notes
        :return: DataFrame of inputs and targets
        """

        X_cols = [f"n_{x}" for x in range(1, self.num_notes+1)]
        y_col =  'n_target'
        df = pd.DataFrame(index=[x for x in range(0, self.get_train_set_size())],
                          columns=X_cols+[y_col])

        offset = 0
        for piece in self.mdict_enc_f:
            num_samples = len(self.mdict_enc_f[piece])-self.num_notes
            for i in range(0, num_samples):
                df.loc[i+offset, X_cols] = self.mdict_enc_f[piece][i:i+self.num_notes]
                df.loc[i+offset, y_col] = self.mdict_enc_f[piece][i+self.num_notes]
            offset += num_samples

        return df[df.columns[:-1]].values, df[df.columns[-1]].values

    def build_previous_note(self):
        """
        generate numpy arrays from the mdict object where first note is target
        :param num_notes: how many notes used to predict next notes
        :return: DataFrame of inputs and targets
        """

        X_cols = [f"n_{x}" for x in range(1, self.num_notes + 1)]
        y_col = 'n_target'
        df = pd.DataFrame(index=[x for x in range(0, self.get_train_set_size())],
                          columns=X_cols + [y_col])

        offset = 0
        for piece in self.mdict_enc_f:
            num_samples = len(self.mdict_enc_f[piece]) - self.num_notes
            for i in range(0, num_samples):
                df.loc[i + offset, X_cols] = self.mdict_enc_f[piece][i + self.num_notes:i]
                df.loc[i + offset, y_col] = self.mdict_enc_f[piece][i]
            offset += num_samples

        return df[df.columns[:-1]].values, df[df.columns[-1]].values

    # helper functions
    def flatten_measures(self):
        """
        flatten measures to a long string for other building functions
        :return: flattened mdict
        """
        flat_enc = {}
        for piece in self.mdict_enc:
            flat_enc[piece] = []
            for measure in self.mdict_enc[piece]:
                flat_enc[piece].extend(self.mdict_enc[piece][measure])

        return flat_enc

    def get_train_set_size(self):
        """
        Use the note and build_type to determine how many samples will be needed
        :return: int specifying the number of samples present
        """

        count = 0
        for piece in self.mdict_enc_f:
            count += len(self.mdict_enc_f[piece]) - self.num_notes
        return count


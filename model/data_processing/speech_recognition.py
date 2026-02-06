import json
import multiprocessing
import os

from campus_wave import configuration
import pocketsphinx


class SpeechRecognition:
    """This class recognizes the speech content of the audio files.
    The data filtering process is the third step of the data processing.

    """

    _speech_dictionary = {}
    _added_file_counter = 0

    def get_database(self):
        """Returns a dictionary (hash map) with the recognized speech of all audio segments.

        """

        return self._speech_dictionary

    def store_database(self):
        """Stores the recognized speech of all audio segments to the hard disc.
        The data set is stored as a JSON file.

        """

        if not os.path.isfile(configuration.SPEECH_RECOGNITION_JSON_STORAGE_FILE):
            open(configuration.SPEECH_RECOGNITION_JSON_STORAGE_FILE, 'a').close()

        with open(configuration.SPEECH_RECOGNITION_JSON_STORAGE_FILE, 'w', encoding="utf8") as file:
            for key, value in self._speech_dictionary.items():
                line_list = [key, value]
                json_content = json.dumps(line_list)
                file.write(f"{json_content}\n")

    def load_database(self):
        """Loads the recognized speech of all audio segments from the hard disc.
        The data set is stored as a JSON file.

        """

        if os.path.isfile(configuration.SPEECH_RECOGNITION_JSON_STORAGE_FILE):
            with open(configuration.SPEECH_RECOGNITION_JSON_STORAGE_FILE, encoding="utf8") as file:
                for one_line in file.readlines():
                    line_list = json.loads(one_line)
                    file_id = line_list[0]
                    file_info = line_list[1]
                    self._speech_dictionary[file_id] = file_info
        else:
            open(configuration.SPEECH_RECOGNITION_JSON_STORAGE_FILE, 'a').close()

    def _reduce_audio_database_parallel(self, audio_database):
        """Converts the dictionary (hash map) into a list of audio segments for the parallel speech recognition process.

        """

        result_list = []

        for file_id, file_list in audio_database.items():

            self._added_file_counter += 1

            # defines the maximum number of audio files in this processing step
            if self._added_file_counter > configuration.SPEECH_RECOGNITION_MAX_FILES:
                return result_list

            # checks if the file is already in the database
            if file_id not in self._speech_dictionary:

                for part_counter, new_file_path, new_file_name, duration, full_audio_duration in file_list:
                    # converts the dictionary into a list of audio segments
                    result_list.append(((file_id, part_counter, new_file_path, new_file_name, duration,
                                         full_audio_duration),
                                        configuration.SPEECH_RECOGNITION_POCKET_SPHINX_CONFIG))
            else:
                pass

        return result_list

    def _store_temporary_results(self):
        """Stores the recognized speech of all audio segments to the hard disc.

        """

        self.store_database()
        self.load_database()

    def _build_partitions(self, tuple_list, partition_number):
        """Creates multiple partitions (lists) for the parallel speech recognition process.
        Each partition is separately processed.

        """

        tuple_list_len = len(tuple_list)

        if tuple_list_len <= partition_number:
            return [tuple_list]

        return_list = []
        temp_list = []

        for index, tuple_elem in enumerate(tuple_list):

            # checks if a new partition is created
            if ((index + 1) % partition_number == 0) or ((index + 1) == tuple_list_len):

                # adds the new audio segment to a temporary list
                temp_list.append(tuple_elem)

                # adds the partition (list of audio segments) to the final list.
                return_list.append(temp_list)

                temp_list = []
            else:
                temp_list.append(tuple_elem)

        return return_list

    def update_database_parallel(self, audio_database):
        """Starts a new parallel speech recognition process.

        """

        # converts the dictionary to a list of audio segments
        reduced_file_part_list = self._reduce_audio_database_parallel(audio_database)

        if reduced_file_part_list:

            # initializes all processes for the parallel speech recognition
            process_pool = multiprocessing.Pool(processes=configuration.SPEECH_RECOGNITION_CALCULATION_CORES)

            # splits the list of audio segments into multiple partitions
            partition_list = self._build_partitions(reduced_file_part_list,
                                                    configuration.SPEECH_RECOGNITION_CALCULATION_BATCH_NUMBER)

            partition_counter = 0

            # each partition is separately processed.
            for partition in partition_list:

                # maps the list of audio segments to a set of processes
                result_file_part_list = process_pool.map(extract_speech_from_file_parallel, partition)

                for file_id, part_counter, _new_file_path, _new_file_name, _duration_milli_seconds, \
                    _full_audio_duration, token_list in result_file_part_list:

                    # stores the recognized speech into a dictionary (hash map)
                    if file_id in self._speech_dictionary:
                        self._speech_dictionary[file_id].append([part_counter, token_list])
                    else:
                        self._speech_dictionary[file_id] = []
                        self._speech_dictionary[file_id].append([part_counter, token_list])

                # stores the recognized speech
                self._store_temporary_results()

                partition_counter += 1

        return True


_global_pocket_sphinx = pocketsphinx.Pocketsphinx(**configuration.SPEECH_RECOGNITION_POCKET_SPHINX_CONFIG)


def extract_speech_from_file_parallel(input_file_part_tuple):
    """Recognizes the speech of an audio segment.

    """

    file_info, config = input_file_part_tuple

    file_id, part_counter, new_file_path, new_file_name, duration_milli_seconds, full_audio_duration = file_info

    # sphinx processes
    _global_pocket_sphinx.decode(audio_file=new_file_path, buffer_size=2048, no_search=False,
                                 full_utt=False)

    # returns a list of different hypothesis
    detailed_segments = _global_pocket_sphinx.segments(detailed=True)

    # removes all words with low confidence score (word probability)
    removed_detailed_segments = _remove_low_probabilities(detailed_segments)

    # replace all words which contain meta information
    clean_token_list = _clean_token_list(removed_detailed_segments)

    return_tuple = (
        file_id, part_counter, new_file_path, new_file_name, duration_milli_seconds, full_audio_duration,
        clean_token_list)
    return return_tuple


def _remove_low_probabilities(speech_token_list):
    """Removes all non relevant words with low confidence scores (word probabilities) of the recognized speech.

    """

    speech_token_list_len = len(speech_token_list)

    for index in range(speech_token_list_len - 1):

        index += 1

        if index > speech_token_list_len - 2:
            index = speech_token_list_len - 2

        next_word, next_probability, next_score, next_confidence = speech_token_list[index + 1]
        word, probability, score, confidence = speech_token_list[index]
        previous_word, previous_probability, previous_score, previous_confidence = speech_token_list[index - 1]

        if probability < configuration.SPEECH_RECOGNITION_FIRST_PROBABILITY_THRESHOLD:
            speech_token_list[index] = (
                configuration.SPEECH_RECOGNITION_UNKNOWN_SPEECH_TERM, probability, score, confidence)

            if next_probability >= configuration.SPEECH_RECOGNITION_FIRST_PROBABILITY_THRESHOLD:

                start = index + 1

                while start < speech_token_list_len:
                    word, probability, score, confidence = speech_token_list[start]

                    if probability < configuration.SPEECH_RECOGNITION_SECOND_PROBABILITY_THRESHOLD:
                        speech_token_list[start] = (
                            configuration.SPEECH_RECOGNITION_UNKNOWN_SPEECH_TERM, probability, score,
                            confidence)
                        start += 1
                    else:
                        start = speech_token_list_len

            if previous_probability >= configuration.SPEECH_RECOGNITION_FIRST_PROBABILITY_THRESHOLD:

                start = index - 1

                while start >= 0:
                    word, probability, score, confidence = speech_token_list[start]

                    if probability < configuration.SPEECH_RECOGNITION_SECOND_PROBABILITY_THRESHOLD:
                        speech_token_list[start] = (
                            configuration.SPEECH_RECOGNITION_UNKNOWN_SPEECH_TERM, probability, score,
                            confidence)
                        start -= 1
                    else:
                        start = -1

    return speech_token_list


def _clean_token_list(speech_token_list):
    """Remove meta information (words) of the speech recognition framework: sphinx.

    """

    token_list = []

    for token, _probability, _score, _confidence in speech_token_list:

        token = token.lower()

        # checks if the word is defined as meta information
        if token in configuration.SPEECH_RECOGNITION_WRONG_TERMS_DICT:

            # replaces the meta information with a list of predefined words
            new_token = configuration.SPEECH_RECOGNITION_WRONG_TERMS_DICT[token]

            if new_token:
                token_list.append(new_token)
        else:
            token_list.append(token)

    return token_list

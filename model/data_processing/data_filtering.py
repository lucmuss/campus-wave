import hashlib
import json
import os
import shutil

from campus_wave import configuration
import tinytag


class DataFiltering:
    """This class locates all relevant audio files in the hard disc.
    The data filtering process is the first step of the data processing.

    """

    _file_dictionary = {}
    _added_file_counter = 0
    _is_current_file_correct = True
    _current_tiny_tag = None

    _all_byte_file_size = 0

    def get_database(self):
        """Returns a dictionary (hash map) with all relevant audio files.

        """

        return self._file_dictionary

    def store_database(self):
        """Stores the all relevant audio files to the hard disc.
        The data set is stored as a JSON file.

        """

        if not os.path.isfile(configuration.DATA_FILTERING_STORAGE_FILE):
            open(configuration.DATA_FILTERING_STORAGE_FILE, 'a').close()

        with open(configuration.DATA_FILTERING_STORAGE_FILE, 'w', encoding="utf8") as file:
            for key, value in self._file_dictionary.items():
                line_list = [key, value]
                json_content = json.dumps(line_list)
                file.write(f"{json_content}\n")

    def load_database(self):
        """Loads the all relevant audio files from the hard disc.
        The data set is stored as a JSON file.

        """

        if os.path.isfile(configuration.DATA_FILTERING_STORAGE_FILE):
            with open(configuration.DATA_FILTERING_STORAGE_FILE, encoding="utf8") as file:
                for one_line in file.readlines():
                    line_list = json.loads(one_line)
                    file_id = line_list[0]
                    file_info = line_list[1]
                    self._file_dictionary[file_id] = file_info
        else:
            open(configuration.DATA_FILTERING_STORAGE_FILE, 'a').close()

    @staticmethod
    def _has_supported_extension(file_name):
        """Returns True if the audio file has the correct file extension.

        """

        lower_file_name = file_name.lower()

        # checks if the file type is correct
        for file_type in configuration.DATA_FILTERING_SUPPORTED_FILE_TYPES:
            if lower_file_name.endswith(file_type):
                return True
        return False

    @staticmethod
    def _has_supported_file_size(file_path):
        """Returns True if the audio file has the correct file size.

        """

        _file_size = os.stat(file_path).st_size

        # the file size has to be in a predefined file size range
        return configuration.DATA_FILTERING_MIN_FILE_SIZE <= _file_size <= configuration.DATA_FILTERING_MAX_FILE_SIZE

    @staticmethod
    def _has_correct_file_name(file_name):
        """Returns True if the file name of the audio file is correct.
        Audio files with special files name are included for indexing.

        """

        lower_file_name = file_name.lower()

        for correct_file_name in configuration.DATA_FILTERING_INCLUDED_FILE_NAMES:

            # checks if the file name is in the list of predefined file names
            if lower_file_name.find(correct_file_name) > -1:
                return True
        return False

    @staticmethod
    def _has_not_wrong_file_name(file_name):
        """Returns True if the file name of the audio file is correct.
        Audio files with wrong files name are filtered out form the data set.

        """

        lower_file_name = file_name.lower()

        for correct_file_name in configuration.DATA_FILTERING_EXCLUDED_FILE_NAMES:

            # checks if the file name is in the list of excluded file names
            if lower_file_name.find(correct_file_name) > -1:
                return False

        return True

    @staticmethod
    def _has_not_wrong_path(file_path):
        """Returns True if the file path of the audio file is correct.
        Audio files which are located in predefined locations are filtered out from the data set.

        """

        lower_file_path = file_path.lower()

        for correct_file_name in configuration.DATA_FILTERING_EXCLUDED_FILE_PATHS:

            # checks if the file path is in the list of excluded file locations
            if lower_file_path.find(correct_file_name) > -1:
                return False

        return True

    def _is_podcast(self, file_path):
        """Returns True if the audio file is relevant.
        Searches for predefined patterns in the ID3 Tags of the audio files.

        """

        try:
            # returns the current ID3 Tags of the audio file
            self._current_tiny_tag = tinytag.TinyTag.get(file_path)
        except:
            self._current_tiny_tag = None

        if self._current_tiny_tag:

            # checks if the ID3 Tag track is empty
            if self._current_tiny_tag.track:
                return False

            # checks if the ID3 Tag album artist is empty
            if self._current_tiny_tag.albumartist:
                return False

            # checks if the ID3 Tag title is empty
            return not self._current_tiny_tag.title
        else:
            self._is_current_file_correct = False
            return False

    @staticmethod
    def _get_creation_date_timestamp(file_path):
        """Returns the creation date as timestamp of the audio file.

        """

        file_stat = os.stat(file_path)

        # the lowest value of all 3 timestamps types (modification / creation date ...) is used for further processing
        min_time_stamp = min(file_stat.st_atime, file_stat.st_mtime, file_stat.st_ctime)
        return int(min_time_stamp)

    @staticmethod
    def _get_file_id(file_path):
        """Calculates the file id (hash value) for each audio file.

        """

        # MD5 hash algorithm
        md5_id = hashlib.md5()
        with open(file_path, 'rb') as file:
            buffer = file.read(configuration.DATA_FILTERING_MD5_HASH_BYTES)

        md5_id.update(buffer)
        return md5_id.hexdigest()

    @staticmethod
    def _get_file_type(file_path):
        """Returns the file type of the audio file.

        """

        return os.path.splitext(file_path)[1][1:].lower()

    def _backup_file(self, from_path, file_id, file_type):
        """Stores the indexed audio file in the backup location.

        """

        # renames the audio file with the file id (hash value) for storing
        new_file_path = f'{configuration.DATA_FILTERING_STORAGE_DICTIONARY}\\{file_id}.{file_type}'

        if not os.path.isfile(new_file_path):
            # copies the file in the backup location
            shutil.copyfile(from_path, new_file_path)

    def _dictionary_walk(self):
        """Iterates over the file archive and returns a list of found files.

        """

        for dir_path, _dir_names, files in os.walk(configuration.DATA_FILTERING_START_DICTIONARY):

            for file_name in files:
                file_path = os.path.join(dir_path, file_name)

                self._is_current_file_correct = True

                yield (file_name, file_path)

    def _filter_files(self, file_walk):
        """Iterates over the file archive and returns a list of relevant audio files.

        """

        for file_name, file_path in file_walk:

            if self._has_supported_extension(file_name):

                if self._has_supported_file_size(file_path):

                    if self._has_not_wrong_path(file_path):

                        is_podcast = self._is_podcast(file_path)
                        has_correct_file_name = self._has_correct_file_name(file_name)

                        if is_podcast or has_correct_file_name:

                            has_not_wrong_file_name = self._has_not_wrong_file_name(file_name)

                            if has_not_wrong_file_name:
                                yield (file_name, file_path)
                            else:
                                pass
                        else:
                            pass

    def update_database(self):
        """Locates all relevant audio files in the hard disc.

        """

        os.makedirs(configuration.DATA_FILTERING_STORAGE_DICTIONARY, exist_ok=True)

        # returns a list of files
        file_walk = self._dictionary_walk()

        # returns a list of relevant audio files
        filtered_walk = self._filter_files(file_walk)

        for file_name, file_path in filtered_walk:

            # calculates the file id for every audio file
            file_id = self._get_file_id(file_path)

            # defines the maximum number of audio files in this processing step
            self._added_file_counter += 1

            if self._added_file_counter < configuration.DATA_FILTERING_MAX_FILES:

                # checks if the file is already in the database
                if file_id not in self._file_dictionary:

                    creation_date_timestamp = self._get_creation_date_timestamp(file_path)
                    file_type = self._get_file_type(file_path)

                    if self._is_current_file_correct:

                        self._backup_file(file_path, file_id, file_type)

                        # all relevant audio files are stored into a dictionary (hash map)
                        self._file_dictionary[file_id] = [
                            file_path, file_name, file_type,
                            creation_date_timestamp]
                    else:
                        pass
                else:
                    pass
            else:
                return True

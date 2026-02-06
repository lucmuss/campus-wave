import json
import os

from campus_wave import configuration
import pydub


class AudioProcessing:
    """This class converts all relevant audio files into the audio format wav and splits these files into
    smaller audio segments. The audio processing is the second step of the data processing.

    """

    _audio_dictionary = {}
    _added_file_counter = 0

    def get_database(self):
        """Returns a dictionary (hash map) of all relevant audio segments.

        """

        return self._audio_dictionary

    def store_database(self):
        """Stores all relevant audio segments to the hard disc.
        The data set is stored as a JSON file.

        """

        if not os.path.isfile(configuration.AUDIO_PROCESSING_STORAGE_FILE):
            open(configuration.AUDIO_PROCESSING_STORAGE_FILE, 'a').close()

        with open(configuration.AUDIO_PROCESSING_STORAGE_FILE, 'w', encoding="utf8") as file:
            for key, value in self._audio_dictionary.items():
                line_list = [key, value]
                json_content = json.dumps(line_list)
                file.write(f"{json_content}\n")

    def load_database(self):
        """Loads all audio segments from the hard disc.
        The data set is stored as a JSON file.

        """

        if os.path.isfile(configuration.AUDIO_PROCESSING_STORAGE_FILE):
            with open(configuration.AUDIO_PROCESSING_STORAGE_FILE, encoding="utf8") as file:
                for one_line in file.readlines():
                    line_list = json.loads(one_line)
                    file_id = line_list[0]
                    file_info = line_list[1]
                    self._audio_dictionary[file_id] = file_info
        else:
            open(configuration.AUDIO_PROCESSING_STORAGE_FILE, 'a').close()

    @staticmethod
    def _get_audio_segment(file_path, file_type):
        """Returns an audio segment as object of the library PyDub.

        """

        try:
            pydub_audio_segment = pydub.AudioSegment.from_file(file_path, format=file_type)
        except:
            pydub_audio_segment = None

        return pydub_audio_segment

    @staticmethod
    def _modify_sound_volume(audio_segment):
        """Changes the sound volume of the audio segment to a standard value.

        """

        optimal_loudness = configuration.AUDIO_PROCESSING_OPTIMAL_LOUDNESS
        current_loudness = audio_segment.dBFS

        # changes the sound volume of the audio segment to the value -20 dBFS
        change_loudness = abs(current_loudness) - abs(optimal_loudness)

        return audio_segment.apply_gain(change_loudness)

    @staticmethod
    def _modify_sampling_frequency(audio_segment):
        """Reduces the sampling rate of the audio segment.

        """

        return audio_segment.set_frame_rate(configuration.AUDIO_PROCESSING_SAMPLE_RATE)

    @staticmethod
    def _modify_sample_width(audio_segment):
        """Modifies the sampling resolution of the audio segment.

        """

        return audio_segment.set_sample_width(configuration.AUDIO_PROCESSING_FRAME_WIDTH)

    @staticmethod
    def _modify_channel_size(audio_segment):
        """Changes the number of channels of the audio segment.

        """

        try:
            new_audio_segment = audio_segment.set_channels(configuration.AUDIO_PROCESSING_CHANNELS)
        except:
            new_audio_segment = None

        return new_audio_segment

    @staticmethod
    def _split_audio_file(audio_segment):
        """Splits the audio file into multiple audio segments.

        """

        duration_milliseconds = len(audio_segment)

        # calculates the number of audio segments of the audio file
        part_number = int(duration_milliseconds / configuration.AUDIO_PROCESSING_PART_SIZE_MILLISECONDS) + 1

        for index in range(part_number):
            # calculates the start range in milliseconds of the current audio segment
            begin_part = index * configuration.AUDIO_PROCESSING_PART_SIZE_MILLISECONDS

            # calculates the end range in milliseconds of the current audio segment
            end_part = (index + 1) * configuration.AUDIO_PROCESSING_PART_SIZE_MILLISECONDS

            end_part_plus = end_part + configuration.AUDIO_PROCESSING_PART_SIZE_OVERLAP

            if end_part_plus > duration_milliseconds:
                end_part_plus = duration_milliseconds

            yield audio_segment[begin_part:end_part_plus]

    def _has_correct_duration(self, audio_segment):
        """Returns True if the audio file has a correct duration.

        """

        return configuration.AUDIO_PROCESSING_MAX_DURATION >= len(audio_segment) >= configuration.AUDIO_PROCESSING_MIN_DURATION

    @staticmethod
    def _export_audio_segment(audio_segment, file_path, file_type):
        """Stores the audio segment into specified audio format on the hard disc.

        """

        if not os.path.isfile(file_path):
            audio_segment.export(file_path, format=file_type)

    @staticmethod
    def _get_new_file_name(file_id, file_part, file_type):
        """Returns the new file name of the audio segment.

        """

        return f"{file_id}_{file_part}.{file_type}"

    def update_database(self, file_database):
        """Converts all audio files into the audio format wav and splits these files into smaller audio segments.

        """

        os.makedirs(configuration.AUDIO_PROCESSING_STORAGE_DICTIONARY, exist_ok=True)

        for file_id, file_info in file_database.items():

            file_path, file_name, file_type, creation_date_timestamp = file_info

            self._added_file_counter += 1

            if self._added_file_counter < configuration.AUDIO_PROCESSING_MAX_FILES:

                # checks if the audio file is already in the database
                if file_id not in self._audio_dictionary:

                    audio_segment = self._get_audio_segment(file_path, file_type)

                    counter = 0

                    # checks if the audio segment was correctly processed
                    if audio_segment:
                        correct_duration = self._has_correct_duration(audio_segment)
                        full_audio_duration = len(audio_segment)

                        if correct_duration:
                            # reduces the sampling frequency of the audio segment
                            audio_segment_frame = self._modify_sampling_frequency(audio_segment)

                            # modifies the sample resolution of the audio segment
                            audio_segment_sample = self._modify_sample_width(audio_segment_frame)

                            # modifies the number of channels of the audio segment
                            audio_segment_channel = self._modify_channel_size(audio_segment_sample)

                            if audio_segment_channel:

                                # modifies sound volume of the audio segment
                                audio_segment_loudness = self._modify_sound_volume(audio_segment_channel)

                                # splits the audio file into multiple audio segments
                                audio_segment_parts = self._split_audio_file(audio_segment_loudness)

                                file_part_list = []

                                for audio_part in audio_segment_parts:
                                    new_file_name = self._get_new_file_name(file_id, counter,
                                                                            configuration.AUDIO_PROCESSING_DEFAULT_FILE_TYPE)

                                    # calculates the new storage location of the audio segment
                                    new_file_path = os.path.join(
                                        configuration.AUDIO_PROCESSING_STORAGE_DICTIONARY,
                                        new_file_name)

                                    duration_milli_seconds = len(audio_part)
                                    file_part = [counter, new_file_path, new_file_name, duration_milli_seconds,
                                                 full_audio_duration]
                                    file_part_list.append(file_part)

                                    counter += 1

                                    self._export_audio_segment(audio_part, new_file_path,
                                                               configuration.AUDIO_PROCESSING_DEFAULT_FILE_TYPE)

                                # stores the audio segments into dictionary (hashmap)
                                self._audio_dictionary[file_id] = file_part_list

                                pass
                            else:
                                pass
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
            else:
                return True

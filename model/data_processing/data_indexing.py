import configuration
import os

from whoosh import index as whoosh_index


class DataIndexing:
    """This class adds all text blocks into retrieval system whoosh.

    """

    _added_file_counter = 0

    def update_database(self, file_database, audio_database, text_database):
        """Merges all data sources into one data set and stores them into the retrieval system.

        """

        # creates a new location for the retrieval system whoosh
        if not os.path.exists(configuration.DATA_INDEXING_WHOOSH_INDEX_LOCATION):
            os.mkdir(configuration.DATA_INDEXING_WHOOSH_INDEX_LOCATION)

        # creates or load a new whoosh index
        index = whoosh_index.create_in(configuration.DATA_INDEXING_WHOOSH_INDEX_LOCATION,
                                       schema=configuration.DATA_INDEXING_WHOOSH_SCHEME,
                                       indexname=configuration.DATA_INDEXING_WHOOSH_INDEX_NAME)

        index_writer = index.writer()

        for file_id, file_info in text_database.items():

            self._added_file_counter += 1

            # defines the maximum number of audio files in this processing step
            if self._added_file_counter < configuration.DATA_INDEXING_MAX_FILES:

                file_path, file_name, file_type, creation_date_milli_seconds = file_database[
                    file_id]

                audio_part_list = audio_database[file_id]

                for file_part, lemma_token_list, important_words, pos_token_list, concept_list in file_info:
                    counter, new_audio_file_path, new_audio_file_name, duration_milli_seconds, full_audio_duration = \
                        audio_part_list[file_part]

                    lemma_speech_text = ' '.join(lemma_token_list)
                    important_words_text = ' '.join(important_words)
                    concept_text = ' '.join(concept_list)

                    # data fields and entries of the retrieval system
                    function_arguments = {'file_id': file_id,
                                          'file_location': file_path,
                                          'file_name': file_name,
                                          'file_type': file_type,
                                          'file_creation_date': creation_date_milli_seconds,
                                          'audio_file_name': new_audio_file_name,
                                          'audio_file_location': new_audio_file_path,
                                          'audio_file_duration': full_audio_duration,
                                          'audio_file_part': file_part,
                                          'speech_text': lemma_speech_text,
                                          'important_words': important_words_text,
                                          'important_concepts': concept_text
                                          }

                    # adds the new document into the retrieval system
                    index_writer.add_document(**function_arguments)

        # commit all changes
        index_writer.commit()

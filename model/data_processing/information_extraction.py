import json
import os

from campus_wave import configuration

from model.data_processing.concept_mapping import ConceptMapping
from model.data_processing.keyword_ranking import KeywordRanking
from model.data_processing.part_of_speech_tagging import PartOfSpeechTagging
from model.data_processing.similarity_computation import SimilarityComputation


class InformationExtraction:
    """This class extracts the keywords and the concepts of the recognized speech.
    The data information process is the fourth step of the data processing.

    """

    _text_dictionary = {}
    _added_file_counter = 0
    _processed_file_counter = 0

    _pos_tagger = None
    _rdf_mapper = None

    def _init_concept_mapping(self):
        """Loads the RDF files from the hard disc.

        """

        if not self._rdf_mapper:
            self._rdf_mapper = ConceptMapping()
            self._rdf_mapper.load_rdf_files()

    def _init_pos_tagging(self):
        """Loads the training data of the part of speech tagging algorithm (spacy).

        """

        if not self._pos_tagger:
            self._pos_tagger = PartOfSpeechTagging("spacy-tagger")

    def get_database(self):
        """Returns a dictionary (hash map) of the processed speech data..

        """

        return self._text_dictionary

    def store_database(self):
        """Stores the speech data to the hard disc.
        The data set is stored as a JSON file.

        """

        if not os.path.isfile(configuration.INFORMATION_EXTRACTION_STORAGE_FILE):
            open(configuration.INFORMATION_EXTRACTION_STORAGE_FILE, 'a').close()

        with open(configuration.INFORMATION_EXTRACTION_STORAGE_FILE, 'w', encoding="utf8") as file:
            for key, value in self._text_dictionary.items():
                line_list = [key, value]
                json_content = json.dumps(line_list)
                file.write(f"{json_content}\n")

    def load_database(self):
        """Loads the speech data from the hard disc.
        The data set is stored as a JSON file.

        """

        if os.path.isfile(configuration.INFORMATION_EXTRACTION_STORAGE_FILE):
            with open(configuration.INFORMATION_EXTRACTION_STORAGE_FILE, encoding="utf8") as file:
                for one_line in file.readlines():
                    line_list = json.loads(one_line)
                    file_id = line_list[0]
                    file_info = line_list[1]
                    self._text_dictionary[file_id] = file_info
        else:
            open(configuration.INFORMATION_EXTRACTION_STORAGE_FILE, 'a').close()

    def _extract_keywords_from_path(self, file_path):
        """Extracts multiple keywords from the file path.

        """

        file_location = file_path.lower()

        # removes multiple chars of the file path
        for key, value in configuration.INFORMATION_EXTRACTION_PATH_REPLACE_DICT.items():
            file_location = file_location.replace(key, value)

        # splitting the file path into multiple locations
        path_keywords = {path_string for path_string in file_location.split(' ') if path_string}

        # removes non relevant locations from the file path
        return_set = path_keywords.difference(configuration.INFORMATION_EXTRACTION_PATH_WRONG_KEYWORDS)

        return return_set

    def _is_correct_speech_segment(self, token_list, audio_duration):
        """Returns True if the audio segment is classified as speech.
        Audio segments with a words to seconds ratio of 1.4 and less are ignored in filtering operation.

        """

        token_len = len(token_list) + 1
        duration_seconds = int(audio_duration / 1000) + 1

        # calculates the ratio between words and seconds
        token_seconds_ration = token_len / duration_seconds

        boolean_op = (token_seconds_ration >= configuration.SPEECH_RECOGNITION_MINIMAL_TOKENS_SECONDS_RATIO)
        return boolean_op

    def update_database(self, speech_database, audio_database, file_database):
        """Extracts keywords and concepts of all annotated audio segments.

        """

        for file_id, file_info in speech_database.items():

            self._added_file_counter += 1

            # defines the maximum number of audio files in this processing step
            if self._added_file_counter < configuration.INFORMATION_EXTRACTION_MAX_FILES:

                # checks if the file is already in the database
                if file_id not in self._text_dictionary:

                    if (file_id in audio_database) and (file_id in file_database):

                        result_token_list = []

                        audio_part_list = audio_database[file_id]
                        file_path, file_name, file_type, creation_date_timestamp = file_database[file_id]

                        # extracts additional keywords of the file path
                        path_keywords = self._extract_keywords_from_path(file_path)

                        for file_part, token_list in file_info:
                            counter, new_audio_file_path, new_audio_file_name, duration_milli_seconds, \
                            full_audio_duration = audio_part_list[file_part]

                            # checks if the audio segment will be classified as speech
                            if self._is_correct_speech_segment(token_list, duration_milli_seconds):

                                self._init_pos_tagging()
                                self._init_concept_mapping()

                                # removes the unknown word tags from the recognized speech
                                removed_token_list = self._pos_tagger.remove_unknown_token(token_list)
                                token_string = ' '.join(removed_token_list)

                                # adds part of speech tags
                                tuple_list = self._pos_tagger.tag(token_string)

                                pos_token_list = self._pos_tagger.get_pos_list(tuple_list)

                                # removes non relevant part of speech tags like adjectives
                                noun_token_list = self._pos_tagger.filter_unigram_pos_list(pos_token_list)

                                # extends the keyword list with the extracted keywords of the file path
                                noun_token_list.extend(path_keywords)

                                # extracts the concepts out of the keywords
                                concept_list = list(self._rdf_mapper.get_concept_set(noun_token_list))

                                important_words_list = list(set(noun_token_list))

                                result_token_list.append(
                                    [file_part, token_list, important_words_list, pos_token_list, concept_list])
                            else:
                                pass

                        if result_token_list:
                            self._text_dictionary[file_id] = result_token_list
                else:
                    pass
            else:
                return True

    def update_concept_mapping(self):
        """Updates concept annotations, when the RDF files changed.

        """

        self._init_concept_mapping()

        for _file_id, file_info in self._text_dictionary.items():

            for index, file_content in enumerate(file_info):
                file_part, token_list, important_words_list, pos_token_list, concept_list = file_content

                # extracts the new concepts out of the keywords
                new_concept_list = list(self._rdf_mapper.get_concept_set(important_words_list))

                new_file_content = [file_part, token_list, important_words_list, pos_token_list, new_concept_list]
                file_info[index] = new_file_content

    def process_text_data(self):
        """Calculates the keyword ranking and semantic relation between the keywords.

        """

        # initializes the keyword ranking components
        relevant_db = KeywordRanking()
        visual_db = SimilarityComputation()

        self._processed_file_counter = 0

        for file_id, file_info in self._text_dictionary.items():

            self._processed_file_counter += 1

            # defines the maximum number of audio files in this processing step
            if self._processed_file_counter < configuration.INFORMATION_EXTRACTION_MAX_FILES:

                for file_part, _lemma_token_list, _important_words, pos_token_list, _concept_list in file_info:
                    # initializes the POS tagging algorithm
                    self._init_pos_tagging()

                    noun_token_list = self._pos_tagger.filter_unigram_pos_list(pos_token_list)

                    # extracts the bigrams of the keywords
                    bi_gram_list = self._pos_tagger.make_bigram_list(pos_token_list)

                    noun_bi_gram_list = self._pos_tagger.filter_bigram_pos_list(bi_gram_list)

                    # updates the keyword ranking component with a new sequence of words
                    relevant_db.update_relevant_unigram_terms(noun_token_list, file_part, file_id)

                    # updates the similarity component with a new sequence of words
                    visual_db.update_visual_terms(noun_token_list, file_part, file_id)

                    # updates the bigram ranking component a new sequence words
                    relevant_db.update_relevant_bigram_terms(noun_bi_gram_list)

        # calculates the keyword ranking
        relevant_db.calculate_unigram_term_rank_list()
        relevant_db.calculate_bigram_term_rank_list()

        most_relevant_terms = relevant_db.get_pure_relevant_term_list()

        # only the highest ranked keywords are used for the similarity computation
        n_best_ranked_terms = most_relevant_terms[0:configuration.SIMILARITY_COMPUTATION_MOST_RELEVANT_TERMS_FOR_SIMILARITY]

        # calculates the semantic relation between keywords
        visual_db.calculate_term_similarities(n_best_ranked_terms)

        # calculates the group cluster of the highest ranked keywords
        visual_db.calculate_term_clusters(n_best_ranked_terms)

        term_cluster_dict = visual_db.get_term_cluster_dict()

        term_concept_dict = self._rdf_mapper.get_term_mapping_dict()

        # updates the cluster information to the keyword ranking component
        relevant_db.update_cluster_information(term_cluster_dict)
        relevant_db.update_concept_information(term_concept_dict)

        # stores the highest ranked keywords in the hard disc
        relevant_db.store_database()
        visual_db.store_database()

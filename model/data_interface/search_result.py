import collections
import ntpath

from campus_wave import configuration
from controller.html_formatter import HtmlFormatter
from whoosh import index as whoosh_index
from whoosh import qparser as whoosh_parser

from model.data_interface.search_history import SearchHistory
from model.data_interface.search_term import SearchTerm
from model.data_processing.concept_mapping import ConceptMapping
from model.data_processing.keyword_ranking import KeywordRanking


class SearchResult:
    """This class performs all search queries of the retrieval system.

    """

    _current_whoosh_index = None
    _current_parser = None

    _frequent_db = None

    _history_db = None

    _rdf_mapper = None

    _result_formatter = None

    _relevant_db = None
    _most_relevant_term_dict = []

    def init_search(self):
        """Initializes all components of the retrieval system.

        """

        self._result_formatter = HtmlFormatter()

        # loads all concepts form the RDF files
        self._rdf_mapper = ConceptMapping()
        self._rdf_mapper.load_rdf_files()

        # initializes the search history for statistics
        self._history_db = SearchHistory()
        self._history_db.load_database()

        # initializes the search terms for statistics
        self._frequent_db = SearchTerm()
        self._frequent_db.load_database()

        # initializes the relevant keywords
        self._relevant_db = KeywordRanking()
        self._relevant_db.load_database()
        self._most_relevant_term_dict = self._relevant_db.get_relevant_term_dict()

        # creates a new instance of the retrieval system
        self._current_whoosh_index = whoosh_index.open_dir(configuration.DATA_INDEXING_WHOOSH_INDEX_LOCATION,
                                                           indexname=configuration.DATA_INDEXING_WHOOSH_INDEX_NAME)
        self._current_parser = whoosh_parser.MultifieldParser(configuration.DATA_INDEXING_WHOOSH_SEARCH_FIELDS,
                                                              schema=configuration.DATA_INDEXING_WHOOSH_SCHEME)

    def finalize_search(self):
        """Stores all entered keywords to the hard disc.

        """

        self._frequent_db.store_database()
        self._history_db.store_database()

    def search_all_parameter(self, search_terms, date_from, date_to, duration_from, duration_to,
                             search_path, page_number, result_number, search_concept, user_id, search_id):
        """Searches for audio files in the database.
        Performs a search request with different input parameters.
        The default value of the parameters is None.

        """

        query_list = []

        # extends the search query with a file identifier
        if search_id:
            search_string = f"file_id:({search_id})"
            query_list.append(search_string)

        # extends the search query with a sequence of terms
        if search_terms:
            # recognized speech
            search_string_text = f"speech_text:({search_terms})"

            # extracted keywords
            search_string_keywords = f"important_words:({search_terms})"

            # boolean search operator OR
            # the search term can occur in extracted keywords and in recognized speech
            term_or_keyword = f"({search_string_text} OR {search_string_keywords})"
            query_list.append(term_or_keyword)

        # extends the search query with a sequence of concepts
        # multiple concepts are separated with a comma
        if search_concept:
            concept_list = search_concept.split(',')

            if isinstance(concept_list, list):
                search_concept = ' AND '.join(concept_list)

            concept_search = f"important_concepts:({search_concept})"
            query_list.append(concept_search)

        # extends the search query with a file location
        if search_path:
            search_string = f"file_location:\"{search_path}\""
            query_list.append(search_string)

        # extends the search query with a date of creation
        if date_to:
            search_string = f"file_creation_date:[{date_from} TO {date_to}]"
            query_list.append(search_string)

        # extends the search query with a date of creation
        if duration_to:
            search_string = f"audio_file_duration:[{duration_from} TO {duration_to}]"
            query_list.append(search_string)

        # extends the search query the current search page
        # page 1 out of 10
        if not page_number:
            page_number = 1

        # extends the search query with the maximum number of audio files per search page
        if not result_number:
            result_number = configuration.SEARCH_RESULT_DEFAULT_RESULT_NUMBER

        result_query = ' '.join(query_list)
        return self._search_database(result_query, page_number, result_number, user_id)

    def _update_query_terms(self, whoosh_query, user_id):
        """Extracts and updates the entered keywords of the search query in the data set.

        """

        term_list = [term[1] for term in whoosh_query.iter_all_terms()]

        if term_list:
            self._frequent_db.update_search_terms(term_list)
            self._history_db.update_search_terms(term_list, user_id)

    def _search_database(self, search_query, search_page, result_number, user_id):
        """Performs a search request to the retrieval system.

        """

        # query parsing
        whoosh_query = self._current_parser.parse(search_query)

        self._update_query_terms(whoosh_query, user_id)

        result_tuple_list = []
        rank_counter = 0

        # performs the search query to the retrieval system whoosh
        with self._current_whoosh_index.searcher() as whoosh_searcher:
            search_results = whoosh_searcher.search_page(whoosh_query, search_page,
                                                         pagelen=result_number,
                                                         terms=True)

            for document in search_results:
                # ranking number in the search result
                rank_counter += 1

                # converts the relevant information of all found audio files to a dictionary
                temp_dict = self._get_result_dict(rank_counter, document)
                result_tuple_list.append(temp_dict)

            # number of search hits
            result_hits = len(search_results)

        return result_tuple_list, result_hits

    def _get_result_dict(self, rank_counter, document):
        """Converts the information about the found audio file of the retrieval system to a tuple.

        """

        search_dict = document.fields()

        # file hash value
        file_hash_value = search_dict['file_id']

        # file location
        file_location = search_dict['file_location']

        # file name
        file_name = search_dict['file_name']

        # file type e.g. mp3
        file_type = search_dict['file_type']

        # location of the audio segment
        current_audio_segment_location = search_dict['audio_file_location']
        segment_file_name = ntpath.basename(current_audio_segment_location)
        stored_audio_segment_location = configuration.AUDIO_PROCESSING_RELATIVE_STORAGE_DICTIONARY + segment_file_name

        # location of the full audio file
        stored_file_location = ''.join([configuration.DATA_FILTERING_RELATIVE_STORAGE_DICTIONARY, file_hash_value, '.',
                                        file_type])

        # audio segment number
        audio_segment_number = search_dict['audio_file_part']

        # creation date of the audio file
        file_creation_date = self._result_formatter.format_creation_date(search_dict['file_creation_date'])

        # audio file duration
        audio_file_duration = self._result_formatter.milliseconds_to_duration(search_dict['audio_file_duration'])

        # file location list
        file_location_list = self._result_formatter.format_file_path(search_dict['file_location'])

        # audio segment duration
        file_part_duration = str(0)

        # relevant keywords list
        relevant_words_set = set(search_dict['important_words'].split())
        relevant_keywords_list = self._result_formatter.format_relevant_keywords(relevant_words_set,
                                                                                 self._most_relevant_term_dict)

        # recognized speech list
        found_search_terms = {term.decode('utf-8') for key, term in document.matched_terms() if key == "speech_text"}
        speech_text_list = search_dict['speech_text'].split()
        recognized_speech_list = self._result_formatter.format_recognized_speech(speech_text_list, found_search_terms,
                                                                                 relevant_words_set)

        # speech recognition precision
        speech_recognition_precision = self._result_formatter.get_speech_recognition_precision(speech_text_list)

        # annotated concept list
        annotated_concept_list = search_dict['important_concepts'].split()

        found_entry = (rank_counter,
                       file_location, stored_audio_segment_location, file_name, file_creation_date, audio_file_duration,
                       file_type,
                       file_location_list,
                       file_part_duration, relevant_keywords_list, annotated_concept_list, recognized_speech_list,
                       audio_segment_number,
                       stored_file_location, speech_recognition_precision, file_hash_value)

        return found_entry

    def get_concept_term_list(self, current_concept):
        """Returns a list of keywords about corresponding concept.

        """

        if current_concept:
            concept_set = self._rdf_mapper.get_term_set([current_concept])
            return_list = list(concept_set)
        else:
            return_list = []

        return return_list

    def extract_concept_set(self, result_list):
        """Extracts a set of concepts from the search result.

        """

        concept_counter = collections.Counter()

        for _rank_counter, _file_location, _audio_file_location, _file_name, _file_creation_date, _file_duration, \
            _file_type, _file_location_path, _file_part_duration, _important_words, found_concept_list, _speech_text, \
            _audio_file_part, _download_file_location, _recognition_precision, _file_id in result_list:
            concept_counter.update(found_concept_list)

        # only the most common concepts are used for the concept summary
        return_list = [concept for concept, counter in
                       concept_counter.most_common(configuration.SEARCH_RESULT_MAX_CONCEPTS_SUMMARY)]

        return return_list

from campus_wave import configuration
from model.data_interface.search_history import SearchHistory
from model.data_interface.search_result import SearchResult
from model.data_interface.search_term import SearchTerm
from model.data_processing.audio_processing import AudioProcessing
from model.data_processing.concept_mapping import ConceptMapping
from model.data_processing.data_filtering import DataFiltering
from model.data_processing.data_indexing import DataIndexing
from model.data_processing.information_extraction import InformationExtraction
from model.data_processing.keyword_ranking import KeywordRanking
from model.data_processing.similarity_computation import SimilarityComputation
from model.data_processing.speech_recognition import SpeechRecognition

global_similarity_computation = None
global_search_result = None
global_keyword_ranking = None
global_search_history = None
global_search_term = None
global_concept_mapping = None


def re_init_global_concept_mapping():
    """Creates a new global concept mapper reference.

    """

    global global_concept_mapping
    del global_concept_mapping

    get_global_concept_mapping()


def get_global_concept_mapping():
    """Returns a new global concept mapper reference.

    """

    global global_concept_mapping

    if not global_concept_mapping:
        concept_mapper = ConceptMapping()
        concept_mapper.load_rdf_files()

        global_concept_mapping = concept_mapper

        return global_concept_mapping
    else:
        return global_concept_mapping


def get_global_similarity_computation():
    """Returns a new global similarity computation reference.

    """

    global global_similarity_computation

    if not global_similarity_computation:
        visual_db = SimilarityComputation()
        visual_db.load_database()

        global_similarity_computation = visual_db

        return global_similarity_computation
    else:
        return global_similarity_computation


def get_global_search_result():
    """Returns a new global search result reference.

    """

    global global_search_result

    if not global_search_result:
        search_db = SearchResult()
        search_db.init_search()

        global_search_result = search_db

        return global_search_result
    else:
        return global_search_result


def get_global_keyword_ranking():
    """Returns a new global keyword ranking reference.

    """

    global global_keyword_ranking

    if not global_keyword_ranking:
        relevant_db = KeywordRanking()
        relevant_db.load_database()

        global_keyword_ranking = relevant_db

        return global_keyword_ranking
    else:
        return global_keyword_ranking


def get_global_search_term():
    """Returns a new global search term reference.

    """

    global global_search_term

    if not global_search_term:
        frequent_db = SearchTerm()
        frequent_db.load_database()

        global_search_term = frequent_db

        return global_search_term
    else:
        return global_search_term


def get_global_search_history():
    """Returns a new global search history reference.

    """

    global global_search_history

    if not global_search_history:
        history_db = SearchHistory()
        history_db.load_database()

        global_search_history = history_db

        return global_search_history
    else:
        return global_search_history


def update_concept_mapping():
    """Updates concept annotations, when the RDF files changed.

    """

    file_db = DataFiltering()
    file_db.load_database()
    file_dict = file_db.get_database()

    audio_db = AudioProcessing()
    audio_db.load_database()
    audio_dict = audio_db.get_database()

    # updates concepts annotations
    text_db = InformationExtraction()
    text_db.load_database()
    text_db.update_concept_mapping()
    text_db.store_database()
    text_dict = text_db.get_database()

    # stores the updated data entries in the database
    search_db = DataIndexing()
    search_db.update_database(file_dict, audio_dict, text_dict)


def start_full_data_processing():
    """Searches for new audio files on the hard disc and adds them into the database.

    """

    # filters all audio files form the hard disc
    file_db = DataFiltering()
    file_db.load_database()
    file_db.update_database()
    file_db.store_database()
    file_dict = file_db.get_database()

    # converts the audio files to wav format
    audio_db = AudioProcessing()
    audio_db.load_database()
    audio_db.update_database(file_dict)
    audio_db.store_database()
    audio_dict = audio_db.get_database()

    # performs the parallel speech recognition
    speech_db = SpeechRecognition()
    speech_db.load_database()
    speech_db.update_database_parallel(audio_dict)
    speech_db.store_database()
    speech_dict = speech_db.get_database()

    # extracts keywords and concepts form the recognized speech
    text_db = InformationExtraction()
    text_db.load_database()
    text_db.update_database(speech_dict, audio_dict, file_dict)
    text_db.store_database()

    # processes the word ranking and word similarity
    text_db.process_text_data()
    text_dict = text_db.get_database()

    # stores data entries in the database
    search_db = DataIndexing()
    search_db.update_database(file_dict, audio_dict, text_dict)


def get_similar_terms(term):
    """Returns a list of semantically related words.

    """

    visual_db = get_global_similarity_computation()

    result_list = visual_db.get_similar_terms(term)

    return result_list


def get_relevant_terms():
    """Returns a number of ranked lists of relevant keywords in the database.
    The list of keywords are grouped by semantic relation between keywords.

    """

    relevant_db = get_global_keyword_ranking()

    result_list = relevant_db.get_output_relevant_term_clusters(configuration.KEYWORD_RANKING_MAX_TERM_RESULTS,
                                                                configuration.KEYWORD_RANKING_MAX_RESULTS_PER_CLUSTER)

    return result_list


def get_relevant_bigrams():
    """Returns a ranked list of relevant bigrams in the database.

    """

    relevant_db = get_global_keyword_ranking()

    result_list = relevant_db.get_output_bigram_terms(configuration.KEYWORD_RANKING_MAX_BIGRAM_TERM_RESULTS)

    return result_list


def get_search_history():
    """Returns a list of keywords which were used in past queries.

    """

    history_db = get_global_search_history()

    result_list = history_db.get_search_history()

    return result_list


def get_search_terms():
    """Returns a list of keywords which were used very frequently in the past queries.

    """

    frequent_db = get_global_search_term()

    result_list = frequent_db.get_frequent_search_terms()

    return result_list


def upload_concept_file(file_object):
    """Stores new submitted RDF files on the hard disc.

    """

    concept_mapper = get_global_concept_mapping()

    upload_success = concept_mapper.upload_concept_file(file_object)

    return upload_success


def save_concept_file(string_content, file_name):
    """Modifies existing RDF files on the hard disk.

    """

    concept_mapper = get_global_concept_mapping()

    write_success = concept_mapper.save_concept_file(string_content, file_name)

    return write_success


def remove_concept_file(file_name):
    """Removes existing RDF files on the hard disk.

    """

    concept_mapper = get_global_concept_mapping()

    removal_success = concept_mapper.remove_concept_file(file_name)

    return removal_success


def get_concept_file_information(file_name):
    """Reads the content and the different concepts of the RDF file.

    """

    concept_mapper = get_global_concept_mapping()

    file_content, file_info = concept_mapper.get_file_info(file_name)

    return file_content, file_info


def get_concept_file_list():
    """Returns a list of all available RDF files on the hard disc.

    """

    concept_mapper = get_global_concept_mapping()

    concept_file_list = concept_mapper.get_file_list()

    return concept_file_list


def search_all_parameter(search_term, date_from, date_to, duration_from, duration_to,
                         search_path, page_number, result_number, search_concept, user_id, search_id):
    """Searches for audio files in the database.
    Performs a search request with different input parameters.

    """

    search_db = get_global_search_result()

    search_result_list, search_result_number = search_db.search_all_parameter(search_term, date_from, date_to,
                                                                              duration_from, duration_to,
                                                                              search_path, page_number, result_number,
                                                                              search_concept, user_id, search_id)

    # extracts the concepts of the search result
    found_concepts = search_db.extract_concept_set(search_result_list)

    # maps the found concepts to a list of keywords
    found_concept_terms = search_db.get_concept_term_list(search_concept)

    search_db.finalize_search()

    return search_result_list, search_result_number, found_concepts, found_concept_terms

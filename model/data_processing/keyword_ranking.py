import os
import json
import collections
import configuration
import math

from controller.html_formatter import HtmlFormatter


class KeywordRanking:
    """This class ranks the extracted keywords.

    """

    _temp_global_unigram_term_frequency = collections.Counter()
    _temp_global_bigram_term_frequency = collections.Counter()

    _temp_document_terms_len = dict()
    _temp_term_frequency_document = dict()

    _most_relevant_term_cluster = list()
    _most_relevant_unigram_terms = list()
    _most_relevant_bigram_terms = list()

    _html_formatter = HtmlFormatter()

    def _clear_data(self):
        """Cleans the data set.

        """

        self._temp_global_unigram_term_frequency.clear()
        self._temp_global_bigram_term_frequency.clear()

        self._temp_document_terms_len = dict()
        self._temp_term_frequency_document = dict()

        self._most_relevant_term_cluster = list()
        self._most_relevant_unigram_terms = list()
        self._most_relevant_bigram_terms = list()

    def _is_already_loaded(self):
        """Checks if the data set is already loaded.

        """

        if len(self._most_relevant_unigram_terms) > 0:
            return True
        else:
            return False

    def load_database(self):
        """Loads the all ordered keywords from the hard disc.
        The data set is stored as a JSON file.

        """

        if self._is_already_loaded():
            return True

        self._clear_data()

        # keywords
        if os.path.isfile(configuration.KEYWORD_RANKING_WEIGHT_STORAGE_FILE):
            with open(configuration.KEYWORD_RANKING_WEIGHT_STORAGE_FILE, 'r', encoding="utf8") as file:
                for one_line in file.readlines():
                    term, term_frequency, term_weight, term_score, term_cluster, term_concepts = json.loads(one_line)
                    term_triple = (term, term_frequency, term_weight, term_score, term_cluster, term_concepts)
                    self._most_relevant_unigram_terms.append(term_triple)
        else:
            open(configuration.KEYWORD_RANKING_WEIGHT_STORAGE_FILE, 'a').close()

        # bigrams
        if os.path.isfile(configuration.KEYWORD_RANKING_BIGRAM_TERM_STORAGE_FILE):
            with open(configuration.KEYWORD_RANKING_BIGRAM_TERM_STORAGE_FILE, 'r', encoding="utf8") as file:
                for one_line in file.readlines():
                    bigram, bigram_frequency, bigram_concepts = json.loads(one_line)
                    term_triple = (bigram, bigram_frequency, bigram_concepts)
                    self._most_relevant_bigram_terms.append(term_triple)
        else:
            open(configuration.KEYWORD_RANKING_BIGRAM_TERM_STORAGE_FILE, 'a').close()

    def store_database(self):
        """Stores the all ordered keywords to the hard disc.
        The data set is stored as a JSON file.

        """

        # keywords
        if not os.path.isfile(configuration.KEYWORD_RANKING_WEIGHT_STORAGE_FILE):
            open(configuration.KEYWORD_RANKING_WEIGHT_STORAGE_FILE, 'a').close()

        with open(configuration.KEYWORD_RANKING_WEIGHT_STORAGE_FILE, 'w', encoding="utf8") as file:
            for term, term_frequency, term_weight, term_score, term_cluster, \
                term_concepts in self._most_relevant_unigram_terms:
                line_list = [term, term_frequency, term_weight, term_score, term_cluster, term_concepts]
                json_content = json.dumps(line_list)
                file.write("%s\n" % json_content)

        # bigrams
        if not os.path.isfile(configuration.KEYWORD_RANKING_BIGRAM_TERM_STORAGE_FILE):
            open(configuration.KEYWORD_RANKING_BIGRAM_TERM_STORAGE_FILE, 'a').close()

        with open(configuration.KEYWORD_RANKING_BIGRAM_TERM_STORAGE_FILE, 'w', encoding="utf8") as file:
            for bigram, bigram_frequency, bigram_concepts in self._most_relevant_bigram_terms:
                line_list = [bigram, bigram_frequency, bigram_concepts]
                json_content = json.dumps(line_list)
                file.write("%s\n" % json_content)

    def update_relevant_unigram_terms(self, token_list, file_part, file_id):
        """Adds new words for the keyword ranking calculation.

        """

        # creates a unique segment id
        global_segment_id = str(file_part) + file_id

        token_set = set(token_list)
        token_set_len = len(token_set)

        # sets the minimum length of the document to a fixed value
        if token_set_len < configuration.KEYWORD_RANKING_MINIMAL_DOCUMENT_LEN:
            token_set_len = configuration.KEYWORD_RANKING_MINIMAL_DOCUMENT_LEN

        self._temp_document_terms_len[global_segment_id] = token_set_len

        # calculates a local frequency distribution of the words
        term_counter = collections.Counter()
        term_counter.update(token_list)

        for term, term_frequency in term_counter.most_common():

            if term in self._temp_term_frequency_document:
                self._temp_term_frequency_document[term].append((global_segment_id, term_frequency))
            else:
                self._temp_term_frequency_document[term] = list()
                self._temp_term_frequency_document[term].append((global_segment_id, term_frequency))

        # adds the words to a global frequency distribution
        self._temp_global_unigram_term_frequency.update(term_counter)

    def update_relevant_bigram_terms(self, bigram_term_list):
        """Adds new bigrams for the bigram ranking calculation.

        """

        # calculates a local frequency distribution of the bigrams
        term_counter = collections.Counter()
        term_counter.update(bigram_term_list)

        # adds the bigrams to a global frequency distribution
        self._temp_global_bigram_term_frequency.update(term_counter)

    def _sort_output_cluster_list(self, reduced_most_relevant_terms, max_cluster_number):
        """Stores the ordered word list into multiple cluster groups and sorts them.

        """

        # sorts the ranked keywords list according to their cluster group
        sorted_by_cluster = sorted(reduced_most_relevant_terms, key=lambda list_element: list_element[4],
                                   reverse=True)

        cluster_list = list()
        old_cluster = -2
        temp_list = list()
        len_list = len(sorted_by_cluster)

        for index, term_tuple in enumerate(sorted_by_cluster):

            term, term_frequency, term_weight, term_score, term_cluster, term_concepts = term_tuple

            if old_cluster != term_cluster or (index == len_list - 1):
                if temp_list:
                    # sorts the ordered words inside of the cluster
                    sorted_temp_list = sorted(temp_list, key=lambda list_element: list_element[3],
                                              reverse=True)

                    # reduces the number of keywords per cluster
                    reduced_sorted_temp_list = sorted_temp_list[0:max_cluster_number]
                    cluster_list.append(reduced_sorted_temp_list)

                old_cluster = term_cluster

                temp_list = list()
                temp_list.append((term, term_frequency, term_weight, term_score, term_cluster, term_concepts))
            else:
                temp_list.append((term, term_frequency, term_weight, term_score, term_cluster, term_concepts))

        self._most_relevant_term_cluster = cluster_list

    def _calculate_term_weight(self, term_frequency, min_frequency, max_frequency, font_scale):
        """Calculates term weight of a keyword.

        """

        # calculates the word weighting formula
        top_frequency = math.log(term_frequency - min_frequency + 1)
        lower_frequency = math.log(max_frequency - min_frequency + 1)

        return 1 + font_scale * (top_frequency / lower_frequency)

    def calculate_unigram_term_rank_list(self):
        """Calculates the rank value for every word.

        """

        most_common_list = self._temp_global_unigram_term_frequency.most_common(1)

        min_frequency = 1
        max_frequency = max(count for term, count in most_common_list)
        term_cluster = -1
        term_concept_list = list()

        frequency_dict = dict(self._temp_global_unigram_term_frequency)

        relevant_term_list = self._temp_term_frequency_document.keys()

        for term in relevant_term_list:

            term_score = 0

            for document_id, term_counter in self._temp_term_frequency_document[term]:
                # calculates the word ranking value
                document_len = self._temp_document_terms_len[document_id]
                score_document = math.log(term_counter + 1) / math.pow(document_len, 2)

                term_score += score_document

            term_frequency = frequency_dict[term]

            # calculates the word weight
            term_weight = self._calculate_term_weight(term_frequency, min_frequency, max_frequency,
                                                      configuration.KEYWORD_RANKING_MAX_WEIGHT_SCORE)

            term_tuple = (term, term_frequency, term_weight, term_score, term_cluster, term_concept_list)
            self._most_relevant_unigram_terms.append(term_tuple)

        # sorts the list of words by their ranking values
        self._most_relevant_unigram_terms = sorted(self._most_relevant_unigram_terms,
                                                   key=lambda list_element: list_element[3],
                                                   reverse=True)

    def calculate_bigram_term_rank_list(self):
        """Calculates rank values for every bigram.

        """

        self._most_relevant_bigram_terms = [(bigram, bigram_frequency) for bigram, bigram_frequency in
                                            self._temp_global_bigram_term_frequency.most_common()]

    def update_cluster_information(self, term_cluster_dict):
        """Merges clusters of the similarity computation and ordered words list to one data structure.

        """

        for index, term_tuple in enumerate(self._most_relevant_unigram_terms):

            term, term_frequency, term_weight, term_score, term_cluster, term_concepts = term_tuple

            if term in term_cluster_dict:
                term_cluster = term_cluster_dict[term]

                # updates the data structure of the word rank
                term_tuple = (term, term_frequency, term_weight, term_score, term_cluster, term_concepts)

                self._most_relevant_unigram_terms[index] = term_tuple

    def update_concept_information(self, term_concept_dict):
        """Merges concepts and ordered words list to one data structure.

        """

        for index, term_tuple in enumerate(self._most_relevant_unigram_terms):

            term, term_frequency, term_weight, term_score, term_cluster, term_concepts = term_tuple

            if term in term_concept_dict:
                found_concept_set = term_concept_dict[term]

                term_concepts = list(found_concept_set)

                # updates the data structure of the word rank
                term_tuple = (term, term_frequency, term_weight, term_score, term_cluster, term_concepts)

                self._most_relevant_unigram_terms[index] = term_tuple

        for index, term_tuple in enumerate(self._most_relevant_bigram_terms):

            term_bigram, bigram_frequency = term_tuple

            # first and scond word of the bigram
            first_term, second_term = term_bigram

            concept_set = set()

            if first_term in term_concept_dict:
                concept_set.update(term_concept_dict[first_term])

            if second_term in term_concept_dict:
                concept_set.update(term_concept_dict[second_term])

            # updates the data structure of the bigrams
            term_tuple = (term_bigram, bigram_frequency, list(concept_set))

            self._most_relevant_bigram_terms[index] = term_tuple

    def get_pure_relevant_term_list(self):
        """Returns a ranked list of words.

        """

        term_list = [term for term, term_frequency, term_weight, term_score, term_cluster, term_concepts in
                     self._most_relevant_unigram_terms]
        return term_list

    def get_relevant_term_dict(self):
        """Returns a dictionary (hash map) of ordered words with additional information.

        """

        return_dict = dict()

        for term, term_frequency, term_weight, term_score, term_cluster, \
            term_concepts in self._most_relevant_unigram_terms:
            return_dict[term] = (term_frequency, term_weight, term_score, term_cluster, term, term_concepts)

        return return_dict

    def get_relevant_term_tuples(self):
        """Returns a dictionary (hash map) of ordered unigrams with additional information.

        """

        return self._most_relevant_unigram_terms

    def get_output_relevant_term_clusters(self, max_term_number, max_cluster_number):
        """Returns list of cluster groups with the highest ranked words.

        """

        if not self._most_relevant_term_cluster:
            reduced_relevant_term_list = self._most_relevant_unigram_terms[0:max_term_number]
            self._sort_output_cluster_list(reduced_relevant_term_list, max_cluster_number)

        return self._most_relevant_term_cluster

    def get_output_bigram_terms(self, max_bigram_number):
        """Returns list of the highest ranked bigrams in the data set.

        """

        return_list = self._most_relevant_bigram_terms[0:max_bigram_number]
        return return_list

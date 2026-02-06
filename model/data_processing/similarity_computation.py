import json
import os

from campus_wave import configuration
import numpy
import sklearn


class SimilarityComputation:
    """This class computes the semantic relation between all words.

    """

    _last_color_counter = 0
    _temp_similarity_term_set = {}

    _temp_clustering_data_set = []
    _temp_term_cluster_dict = {}

    _similarity_terms_dict = {}

    def _clear_data(self):
        """Cleans the data set.

        """

        self._last_color_counter = 0
        self._temp_similarity_term_set = {}

        self._temp_clustering_data_set = []
        self._temp_term_cluster_dict = {}

        self._similarity_terms_dict = {}

    def _is_already_loaded(self):
        """Checks if the data set is already loaded.

        """

        return len(self._similarity_terms_dict) > 0

    def load_database(self):
        """Loads all words and the semantic related words from the hard disc.
        The data set is stored as a JSON file.

        """

        if self._is_already_loaded():
            return True

        self._clear_data()

        if os.path.isfile(configuration.SIMILARITY_COMPUTATION_SIMILAR_STORAGE_FILE):
            with open(configuration.SIMILARITY_COMPUTATION_SIMILAR_STORAGE_FILE, encoding="utf8") as file:
                for one_line in file.readlines():
                    term, term_list = json.loads(one_line)
                    self._similarity_terms_dict[term] = term_list
        else:
            open(configuration.SIMILARITY_COMPUTATION_SIMILAR_STORAGE_FILE, 'a').close()

    def store_database(self):
        """Stores all words and the semantic related words to the hard disc.
        The data set is stored as a JSON file.

        """

        if not os.path.isfile(configuration.SIMILARITY_COMPUTATION_SIMILAR_STORAGE_FILE):
            open(configuration.SIMILARITY_COMPUTATION_SIMILAR_STORAGE_FILE, 'a').close()

        with open(configuration.SIMILARITY_COMPUTATION_SIMILAR_STORAGE_FILE, 'w', encoding="utf8") as file:
            for key, value in self._similarity_terms_dict.items():
                line_list = [key, value]
                json_content = json.dumps(line_list)
                file.write(f"{json_content}\n")

    def update_visual_terms(self, token_list, file_part, file_id):
        """Adds new words for the similarity computation between words.

        """

        # creates a unique segment id
        global_segment_id = str(file_part) + file_id

        for token in token_list:

            if token in self._temp_similarity_term_set:
                self._temp_similarity_term_set[token].add(global_segment_id)
            else:
                self._temp_similarity_term_set[token] = set()
                self._temp_similarity_term_set[token].add(global_segment_id)

    def _calculate_term_similarity(self, first_term, second_term):
        """Calculates the semantic relation between two words.

         """

        # number of documents in which each word occurs
        first_set = self._temp_similarity_term_set[first_term]
        second_set = self._temp_similarity_term_set[second_term]

        # number of documents in which both word occurs
        intersection_set = first_set & second_set

        # number of documents in which each word occurs (OR)
        union_set = first_set | second_set

        intersection_len = len(intersection_set)
        union_len = len(union_set)

        return intersection_len / union_len

    def calculate_term_clusters(self, most_relevant_terms):
        """Calculates the different cluster groups of the highest ranked words.

         """

        # normalize the data set
        normalized_data_set = sklearn.preprocessing.normalize(self._temp_clustering_data_set)

        k_means = sklearn.cluster.SpectralClustering(n_clusters=configuration.KEYWORD_RANKING_CLUSTER_NUMBER,
                                                     affinity='rbf')

        # starts the clustering algorithm
        k_means.fit(normalized_data_set)

        # list of cluster groups
        label_array = k_means.labels_

        # merges the labels of the cluster groups with the words
        for index, label in enumerate(label_array):
            term = most_relevant_terms[index]

            self._temp_term_cluster_dict[term] = int(label)

    def get_term_cluster_dict(self):
        """Calculates the cluster groups of the highest ranked words.

         """

        return self._temp_term_cluster_dict

    def calculate_distance_list(self, term_clustering_element):
        """Converts the value of the semantic relation into a distance value.

         """

        return_list = []
        for score in term_clustering_element:
            if score == 1.0:
                return_list.append(0)
            else:
                # a higher semantic value means a lower distance
                return_list.append(1.0 / (score + 0.0001))

        return return_list

    def calculate_term_similarities(self, most_relevant_terms):
        """Calculates the semantic relation between the highest ranked words.

         """

        term_clustering_data_set = []

        if not self._temp_similarity_term_set:
            return True

        for important_term in most_relevant_terms:

            similar_term_list = []
            term_clustering_element = []

            for second_term in most_relevant_terms:
                # calculates the semantic relation between words
                similarity_value = self._calculate_term_similarity(important_term, second_term)

                similarity_tuple = (second_term, similarity_value)

                similar_term_list.append(similarity_tuple)
                term_clustering_element.append(similarity_value)

            # converts the similarity values into distances
            proximity_distance_list = self.calculate_distance_list(term_clustering_element)

            # the list of distance values is converted to a numpy array
            numpy_array = numpy.array(proximity_distance_list)

            # add the col to the distance matrix
            term_clustering_data_set.append(numpy_array)

            # sorts the similarity values according to their rank
            sorted_term_list = sorted(similar_term_list, key=lambda list_element: list_element[1], reverse=True)
            self._similarity_terms_dict[important_term] = sorted_term_list[
                                                          0:configuration.SIMILARITY_COMPUTATION_MAX_RESULTS * 2]

        self._temp_clustering_data_set = numpy.array(term_clustering_data_set)

    def get_similar_terms(self, input_term):
        """Returns a list of similar words.

         """

        result_list = []

        self._last_color_counter = 0

        if input_term in self._similarity_terms_dict:
            similar_terms = self._similarity_terms_dict[input_term]

            # reduces the number of similar terms
            reduced_similar_terms = similar_terms[0:configuration.SIMILARITY_COMPUTATION_MAX_RESULTS + 1]

            index = 0

            for term, rank in reduced_similar_terms:

                # the rank value of each keyword is squared for a better visual representation
                rank = (rank * rank) * 100
                if (term != input_term) and (rank > 0.0):
                    index += 1

                    result_tuple = (index, f'{rank:.2f}', term, term, self._get_next_color_value())
                    result_list.append(result_tuple)

        return result_list

    def get_similar_term_dict(self):
        """Returns a list of similar words.

         """

        return self._similarity_terms_dict

    def _get_next_color_value(self):
        """Calculates the new HSL colour for the next word.

         """

        if self._last_color_counter == configuration.SIMILARITY_COMPUTATION_MAX_RESULTS + 1:
            self._last_color_counter = 0

        degree_step_size = 360.0 / float(configuration.SIMILARITY_COMPUTATION_MAX_RESULTS)
        hsl_color_degree = (self._last_color_counter * int(degree_step_size)) + 1 * int(degree_step_size)

        self._last_color_counter += 1
        return f'hsl({hsl_color_degree}, 60%, 50%)'

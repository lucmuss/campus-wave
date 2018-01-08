import os
import configuration
import json
import collections


class SearchTerm:
    """This class stores all keywords which were used in the past search queries.

    """

    _frequent_search_terms = collections.Counter()
    _output_most_frequent_search_terms = []

    def load_database(self):
        """Loads the entered keywords from the hard disc.
        The data set is stored as a JSON file.

        """

        self._frequent_search_terms.clear()

        if os.path.isfile(configuration.SEARCH_TERM_STORAGE_FILE):
            with open(configuration.SEARCH_TERM_STORAGE_FILE, 'r', encoding="utf8") as file:
                temp_dict = {}
                for one_line in file.readlines():
                    word, counter = json.loads(one_line)
                    temp_dict[word] = counter
                self._frequent_search_terms.update(temp_dict)
        else:
            open(configuration.SEARCH_TERM_STORAGE_FILE, 'a').close()

    def store_database(self):
        """Stores the entered keywords to the hard disc.
        The data set is stored as a JSON file.

        """

        if not os.path.isfile(configuration.SEARCH_TERM_STORAGE_FILE):
            open(configuration.SEARCH_TERM_STORAGE_FILE, 'a').close()

        with open(configuration.SEARCH_TERM_STORAGE_FILE, 'w', encoding="utf8") as file:
            for item in self._frequent_search_terms.most_common():
                json_content = json.dumps(item)
                file.write("%s\n" % json_content)

    def update_search_terms(self, token_list):
        """Updates the data set with the new entered keywords.

        """

        self._frequent_search_terms.update(token_list)

    def get_frequent_search_terms(self):
        """Returns a list of keywords which were used very frequently in past queries.

        """

        # only the most common keywords are returned
        output_most_frequent_search_terms = self._frequent_search_terms.most_common(
            configuration.SEARCH_TERM_MAX_RESULTS)
        return output_most_frequent_search_terms

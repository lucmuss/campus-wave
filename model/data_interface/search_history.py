import json
import os
import time
import configuration

from controller import html_formatter


class SearchHistory:
    """This class stores keywords of the past search queries.

    """

    _search_history = []
    _output_sorted_search_history = []

    def load_database(self):
        """Loads the keywords from the hard disc.
        The data set is stored as a JSON file.

        """

        self._search_history = []

        if os.path.isfile(configuration.SEARCH_HISTORY_STORAGE_FILE):
            with open(configuration.SEARCH_HISTORY_STORAGE_FILE, 'r', encoding="utf8") as file:
                for one_line in file.readlines():
                    line_element = json.loads(one_line)
                    self._search_history.append(line_element)
        else:
            open(configuration.SEARCH_HISTORY_STORAGE_FILE, 'a').close()

    def store_database(self):
        """Stores the keywords to the hard disc.
        The data set is stored as a JSON file.

        """

        if not os.path.isfile(configuration.SEARCH_HISTORY_STORAGE_FILE):
            open(configuration.SEARCH_HISTORY_STORAGE_FILE, 'a').close()

        with open(configuration.SEARCH_HISTORY_STORAGE_FILE, 'w', encoding="utf8") as file:
            for item in self._search_history:
                json_content = json.dumps(item)
                file.write("%s\n" % json_content)

    def update_search_terms(self, token_list, user_id):
        """Updates the data set with new entered keywords.

        """

        current_timestamp = int(time.time())
        self._search_history.append((current_timestamp, user_id, token_list))

    def get_search_history(self):
        """Returns a list of keywords which were used in past queries.

        """

        formatter = html_formatter.HtmlFormatter
        result_list = []

        # sorts the entered keywords by their timestamp
        sorted_history_list = sorted(self._search_history, key=lambda list_element: list_element[0], reverse=True)

        for timestamp, user_id, token_list in sorted_history_list:
            formatted_date = formatter.timestamp_to_date(timestamp)
            result_list.append([formatted_date, token_list])

        return result_list[0:configuration.SEARCH_HISTORY_MAX_RESULTS]

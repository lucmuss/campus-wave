import datetime

from campus_wave import configuration


class HtmlFormatter:
    """This class formats the search result into a HTML representation.

    """

    @staticmethod
    def timestamp_to_date(timestamp):
        """Converts an unix timestamp into human readable date.

        For example: 12:30 01.04.1990
        """

        result_time = datetime.datetime.utcfromtimestamp(timestamp)
        return result_time.strftime('%H:%M - %d.%m.%Y')

    @staticmethod
    def milliseconds_to_duration(milliseconds):
        """Converts milliseconds into human readable duration.

        For example: 00:59:23
        """

        input_seconds = int(milliseconds / 1000)
        result_time = datetime.timedelta(seconds=input_seconds)

        days, seconds = result_time.days, result_time.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = (seconds % 60)

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def get_speech_recognition_precision(self, token_list):
        """Estimates the level of precision in percent of the recognized speech.

        For example: 69%
        """

        token_len = len(token_list)

        wrong_recognition_len = sum(
            1 for token in token_list if token == configuration.SPEECH_RECOGNITION_UNKNOWN_SPEECH_TERM)

        recognition_precision = 1.0 - (wrong_recognition_len / token_len)
        return_string = f"{recognition_precision * 100:.0f}%"
        return return_string

    def format_creation_date(self, timestamp):
        """Converts an unix timestamp into human readable date.

        For example: 01.04.1990
        """

        time_object = datetime.datetime.utcfromtimestamp(timestamp)

        date_string = time_object.strftime('%d.%m.%Y')

        return date_string

    def format_file_path(self, path_string):
        """Converts the file path into a list of multiple locations or dictionaries.

        """

        path_list = path_string.split('\\')
        path_list = path_list[:-1]

        return path_list

    def get_weight_class(self, term_weight):
        """Returns the corresponding CSS class for the word weight.

        """

        if 0 <= term_weight < 3:
            return "tag_normal"

        if 3 <= term_weight < 6:
            return "tag_medium"

        if 6 <= term_weight < 10:
            return "tag_big"

    def format_relevant_keywords(self, relevant_terms_set, most_relevant_term_dict):
        """Formats the relevant keywords in the search result.
        First keywords in the list are combined with a global ranking and weighting function.
        Second the keywords are sorted after their ranking value.

        """

        normal_term_rank_list = []

        for term in relevant_terms_set:
            if term in most_relevant_term_dict:
                term_frequency, term_weight, term_score, term_cluster, term, term_concepts = most_relevant_term_dict[
                    term]

                weight_class = self.get_weight_class(term_weight)
                normal_term_rank_list.append((term, term_score, term_weight, weight_class))
            else:
                normal_term_rank_list.append((term, 0, 0, "tag_normal"))

        normal_term_rank_list = sorted(normal_term_rank_list, key=lambda list_element: list_element[1],
                                       reverse=True)

        result_list = normal_term_rank_list[0:configuration.SEARCH_RESULT_MAX_IMPORTANT_TERMS]
        return result_list

    def format_recognized_speech(self, token_list, search_term_set, relevant_term_set):
        """Formats recognized speech in the search result.
        Keywords in the query are marked with a yellow background colour.
        Relevant words are displayed as HTML link.

        """

        result_list = []
        found_index = 0

        for index, token in enumerate(token_list):
            if token in search_term_set:
                found_index = index
                break

        found_half = int(configuration.SEARCH_RESULT_MAX_RECOGNIZED_WORDS / 2)

        if found_index <= found_half:
            start_index = 0
            off_set = found_half - found_index
        else:
            start_index = found_index - found_half
            off_set = 0

        end_index = found_index + found_half + off_set + 1
        temp_token_list = token_list[start_index:end_index]

        for token in temp_token_list:

            if token in search_term_set:
                result_list.append((token, 1))
            elif token in relevant_term_set:
                result_list.append((token, 2))
            elif token == configuration.SPEECH_RECOGNITION_UNKNOWN_SPEECH_TERM:
                result_list.append((configuration.SEARCH_RESULT_UNKNOWN_TOKEN, 0))
            else:
                result_list.append((token, 0))

        return result_list

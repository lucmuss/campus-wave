from campus_wave import configuration
import spacy


class PartOfSpeechTagging:
    """This class annotates the recognized speech with part of speech tags.

    """

    TT = "tree-tagger"
    SPACY = "spacy-tagger"

    def __init__(self, tagger):
        """Initializes the part of speech tagging algorithm.

        """

        if tagger == PartOfSpeechTagging.SPACY:
            self.tagger_name = PartOfSpeechTagging.SPACY
            self.__tagger = spacy.load('de', parser=False)
        else:
            raise Exception("Wrong tagger parameter.")

    def tag(self, text):
        """Annotates one sentence with a list of parts of speech.

        """

        tuple_list = []

        tags = self.__tagger(text)

        for word in tags:
            tuple_list.append((word.text, word.lemma, word.lemma_, word.tag, word.tag_, word.pos, word.pos_))

        return tuple_list

    def get_pos_list(self, tag_list):
        """Reduces the parts of speech list to list of tuples.

        """

        return_list = []

        for _text, _lemma, lemma_, _tag, tag_, _pos, pos_ in tag_list:
            return_list.append((lemma_, pos_))

        return return_list

    def filter_unigram_pos_list(self, uni_gram_pos_list):
        """Removes all non relevant words with predefined list of parts of speech.

        """

        return_list = []

        for lemma_, pos_ in uni_gram_pos_list:

            if self._is_correct_term(lemma_, pos_):
                return_list.append(lemma_)

        return return_list

    def filter_bigram_pos_list(self, bi_gram_pos_list):
        """Removes all non relevant bigrams with predefined list of parts of speech.

        """

        return_list = []

        for first_element, second_element in bi_gram_pos_list:

            first_term, first_pos_tag = first_element
            second_term, second_pos_tag = second_element

            if self._is_correct_term(first_term, first_pos_tag) and self._is_correct_term(second_term, second_pos_tag):
                return_list.append((first_term, second_term))

        return return_list

    def get_lemma_list(self, pos_list):
        """Returns a list of lemmatize words.

        """

        return_list = []

        for lemma_, pos_ in pos_list:
            return_list.append(lemma_)

        return return_list

    def remove_unknown_token(self, token_list):
        """Remove unknown words from the recognized speech.

        """

        return_list = []

        for token in token_list:
            # filters unknown words from the data set
            if token != configuration.SPEECH_RECOGNITION_UNKNOWN_SPEECH_TERM:
                return_list.append(token)

        return return_list

    def make_bigram_list(self, input_list):
        """Converts a sequence of words to a sequence of bigrams.

        """

        return zip(input_list, input_list[1:])

    def _is_correct_term(self, term, pos_tag):
        """Returns True if the parts of speech label is relevant.

        """

        return (pos_tag in configuration.INFORMATION_EXTRACTION_NOUN_TAGS) and (
            term != configuration.SPEECH_RECOGNITION_UNKNOWN_SPEECH_TERM) and term not in configuration.INFORMATION_EXTRACTION_FINAL_GERMAN_STOP_WORD_LIST

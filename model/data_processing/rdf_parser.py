import pyparsing


class RdfParser:
    """RDFParser is a parser to parse specified RDF files."""

    def __init__(self):
        """Initialize a new RDF parser with pre-defined grammar."""

        # grammar definition
        # literals
        self.__word = self.__prefix = self.__suffix = pyparsing.Word(pyparsing.alphanums)
        self.__colon = pyparsing.Literal(':')
        self.__a = pyparsing.Literal('a')
        self.__quoted_string = pyparsing.dblQuotedString.setParseAction(pyparsing.removeQuotes)
        self.__l_paren = pyparsing.Suppress('(')
        self.__r_paren = pyparsing.Suppress(')')
        self.__dot = pyparsing.Suppress('.')
        self.__comma = pyparsing.Suppress(',')
        self.__semicolon = pyparsing.Suppress(';')

        # composites
        self.__get_suffix = pyparsing.Suppress(self.__prefix + self.__colon) + self.__suffix
        self.__get_object = pyparsing.Optional(self.__l_paren) + pyparsing.OneOrMore(
            (self.__get_suffix | self.__quoted_string) +
            pyparsing.Optional(self.__comma)) + pyparsing.Optional(self.__r_paren)
        self.__is_a = (self.__get_suffix('subject') | self.__word) + self.__a('relation') + \
                      self.__get_suffix('object') + self.__dot
        self.__has_x = self.__get_suffix('subject') + self.__get_suffix('relation') + \
                       pyparsing.Group(self.__get_object)('object') + self.__dot

        # search term
        self.__search = pyparsing.Forward()
        self.__search << (self.__is_a | self.__has_x)

    def get_pattern_from_rdf(self, filename):
        """Extract all needed pattern from a rdf file.

        """

        data = self.read_in_rdf_file(filename)
        pattern_list = {}
        attribute_list = {}
        object_list = {}
        scale_list = {}

        for statements in data:
            subject, relation, relation_object = self.__search.parseString(statements)

            # filter relations
            if relation == 'hasPattern':
                pattern_list.update({subject: relation_object})
            elif relation == 'hasAttribute':
                attribute_list.update({subject: relation_object})
            elif relation == "hasObject":
                object_list.update({subject: relation_object})
            elif relation == "hasScale":
                scale_list.update({subject: relation_object})
            else:
                pass
        return pattern_list, attribute_list, object_list, scale_list

    def read_in_rdf_file(self, filename):
        """Reads the rdf file and returns a list of lines of the file content.

        """

        # checks the file extension
        if not filename.endswith(".rdf"):
            raise Exception("Invalid file format")

        cleaned_rdf = []
        with open(filename, encoding="utf-8") as file:
            data = file.read()

            # splits the whole content into multiple lines
            rdf_data = data.splitlines()

        for data in rdf_data:
            if data != '':
                cleaned_rdf.append(data)
        return cleaned_rdf

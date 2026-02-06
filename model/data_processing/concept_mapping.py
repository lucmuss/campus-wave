import os

from campus_wave import configuration

from model.data_processing.rdf_parser import RdfParser


class ConceptMapping:
    """This class reads all RDF file from the hard disc and extracts the concepts and the terms.

    """

    term_to_concept = {}
    concept_to_term = {}

    file_dict = {}
    file_list = []

    rdf_parser = RdfParser()

    def _generate_file_list(self):
        """Returns a list of RDF files and concepts.

        """

        self.load_rdf_files()
        for index, file_info in enumerate(self.file_dict.items()):
            file_name, concept_set = file_info

            self.file_list.append((index + 1, file_name, concept_set))

    def _add_empty_rdf_file(self, file_name):
        """Adds a new RDF file data entry to the data set.

        """

        if file_name not in self.file_dict:
            self.file_dict[file_name] = set()

    def _check_file_extension(self, file_name):
        """Returns True if the uploaded file has the file extension RDF.

        """

        return ('.' in file_name) and (
            file_name.rsplit('.', 1)[1].lower() in configuration.ADMINISTRATION_ALLOWED_FILE_TYPES)

    def upload_concept_file(self, file_object):
        """Stores submitted RDF files on the hard disc.

        """

        upload_success = False

        # checks if the filename is empty
        if file_object.filename != '':

            # checks if the file extension is correct
            if file_object and self._check_file_extension(file_object.filename):

                # creates the location of the RDF file
                file_path = configuration.INFORMATION_EXTRACTION_RDF_STORAGE + '\\' + file_object.filename

                # checks if the RDF file already exists in the hard disc
                if not os.path.isfile(file_path):
                    # stores the ile content to the hard disc
                    file_object.save(file_path)

                    # updates the RDF file list
                    self._generate_file_list()
                    upload_success = True
        return upload_success

    def save_concept_file(self, string_content, file_name):
        """Modifies existing RDF files on the hard disk.

        """

        write_success = False
        if file_name in self.file_dict:

            # creates the location of the RDF file
            file_path = configuration.INFORMATION_EXTRACTION_RDF_STORAGE + '\\' + file_name

            content_lines = string_content.splitlines()

            # checks if the RDF file already exists in the hard disc
            if os.path.isfile(file_path):
                with open(file_path, 'w', encoding="utf8") as file:

                    for line in content_lines:
                        # each line is written to the file
                        file.write(line + "\n")

                # updates the RDF file list
                self._generate_file_list()

                write_success = True
        return write_success

    def remove_concept_file(self, file_name):
        """Removes existing RDF files of the hard disk.

        """

        removal_success = False
        if file_name in self.file_dict:

            # creates the location of the RDF file
            file_path = configuration.INFORMATION_EXTRACTION_RDF_STORAGE + '\\' + file_name

            # checks if the RDF file already exists in the hard disc
            if os.path.isfile(file_path):
                # removes the RDF file
                os.remove(file_path)

                # updates the RDF file list
                self._generate_file_list()
                removal_success = True

        return removal_success

    def get_file_list(self):
        """Returns a list of RDF files in the hard disk.

        """

        if self.file_list:
            return self.file_list
        else:
            # updates the RDF file list
            self._generate_file_list()
            return self.file_list

    def _get_file_content(self, file_name):
        """Returns the content of the RDF file as string.

        """

        return_string = " "

        # creates the location of the RDF file
        file_path = configuration.INFORMATION_EXTRACTION_RDF_STORAGE + '\\' + file_name

        # checks if the RDF file already exists in the hard disc
        if os.path.isfile(file_path):
            with open(file_path, encoding="utf8") as file:
                # reads the content of the RDF file
                return_string = file.read()

        return return_string

    def get_file_info(self, file_name):
        """Reads the content and the different concepts of the RDF file.

        """

        # checks if the RDF file is in the data set
        if file_name in self.file_dict:

            concept_set = self.file_dict[file_name]

            # reads the content of the RDF file
            file_content = self._get_file_content(file_name)

            if concept_set:
                return_list = []

                for concept in concept_set:
                    # extracts the corresponding terms from the concepts
                    term_set = self.get_term_set([concept])
                    return_list.append((concept, term_set))

                return file_content, return_list
            else:
                return file_content, []
        else:
            return None, []

    def _add_concept_to_term(self, term, concept, file_name):
        """Extends the definition of a concept with the corresponding keyword.

        """

        if term in self.term_to_concept:
            self.term_to_concept[term].add(concept)
        else:
            self.term_to_concept[term] = set()
            self.term_to_concept[term].add(concept)

        if file_name in self.file_dict:
            self.file_dict[file_name].add(concept)
        else:
            self.file_dict[file_name] = set()
            self.file_dict[file_name].add(concept)

    def _add_term_to_concept(self, term, concept):
        """Extends the definition of a keyword with the corresponding concept.

        """

        if concept in self.concept_to_term:
            self.concept_to_term[concept].add(term)
        else:
            self.concept_to_term[concept] = set()
            self.concept_to_term[concept].add(term)

    def _extract_rdf_file(self, rdf_data, rdf_len, rdf_deep, concept_lookup_list, tree_path, file_name):
        """Helper method for extracting concepts of the RDF files.
        This method recursively extract the set of concepts from the RDF file.

        """

        if rdf_len > rdf_deep:
            current_dict = rdf_data[rdf_deep]

            if current_dict:
                copy_set = set(concept_lookup_list)
                for concept in copy_set:

                    concept_lookup_list.remove(concept)
                    data_values = current_dict[concept]

                    first_value = data_values[0]

                    if first_value.islower():

                        tree_path = list(tree_path)
                        tree_path.append(concept)

                        for term in data_values:
                            for local_concept in tree_path:
                                self._add_concept_to_term(term, local_concept, file_name)

                        for local_concept in tree_path:
                            for term in data_values:
                                self._add_term_to_concept(term, local_concept)

                        tree_path.remove(concept)
                    else:
                        for concept_value in data_values:
                            concept_lookup_list.add(concept_value)

                for concept_value in copy_set:
                    tree_path.append(concept_value)

                return self._extract_rdf_file(rdf_data, rdf_len, rdf_deep + 1, concept_lookup_list, tree_path,
                                              file_name)
            else:
                return self._extract_rdf_file(rdf_data, rdf_len, rdf_deep + 1, concept_lookup_list, tree_path,
                                              file_name)

    def _init_concept_database(self, rdf_data):
        """Helper method for initializing the data set.

        """

        init_value = list(rdf_data[1].keys())[0]
        init_set = set()
        init_set.add(init_value)

        return init_set

    def load_rdf_files(self):
        """Loads all RDF files from the hard disc.

        """

        self.term_to_concept = {}
        self.concept_to_term = {}

        self.file_dict = {}
        self.file_list = []

        for dir_path, _dir_names, files in os.walk(configuration.INFORMATION_EXTRACTION_RDF_STORAGE):

            for file_name in files:

                # creates the location of the RDF file
                file_path = os.path.join(dir_path, file_name)

                try:
                    # extracts the content of the RDF file
                    rdf_data = self.rdf_parser.get_pattern_from_rdf(file_path)
                except:
                    raise NameError('File: ' + file_name)

                if rdf_data:
                    init_set = self._init_concept_database(rdf_data)

                    rdf_data_len = len(rdf_data)
                    rdf_deep = 0

                    tree_path = []

                    self._add_empty_rdf_file(file_name)

                    # extracts the concepts and terms of the RDF file
                    self._extract_rdf_file(rdf_data, rdf_data_len, rdf_deep, init_set, tree_path, file_name)
                else:
                    self._add_empty_rdf_file(file_name)

    def get_term_mapping_dict(self):
        """Returns a dictionary (hash map) for mapping concepts and terms.

        """

        return self.term_to_concept

    def get_concept_mapping_dict(self):
        """Returns a dictionary (hash map) for mapping concepts and terms.

        """

        return self.concept_to_term

    def _get_terms(self, concept):
        """Returns a set of terms of the concept.

        """

        if concept in self.concept_to_term:
            return self.concept_to_term[concept]

        return set()

    def _get_concepts(self, term):
        """Returns a set of concepts of the term.

        """

        if term in self.term_to_concept:
            return self.term_to_concept[term]

        return set()

    def get_concept_set(self, term_list):
        """Returns a set of concepts.

        """

        return_set = set()
        for term in term_list:
            concept_set = self._get_concepts(term)
            return_set.update(concept_set)

        return return_set

    def get_term_set(self, concept_list):
        """Returns a set of terms.

        """

        return_set = set()
        for concept in concept_list:
            term_set = self._get_terms(concept)
            return_set.update(term_set)

        return return_set

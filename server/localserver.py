import contextlib
import datetime
import uuid

from campus_wave import configuration
import flask
from controller import model_controller

# starts a new web server
app = flask.Flask(__name__)

# initializes the secret key for the encryption of the session
app.secret_key = configuration.FLASK_SECRET_KEY


@app.route('/')
def index_page():
    """The index page of the web application.
    Adress: http://127.0.0.1:5000

    """

    # creates a unique id of the user
    set_user_id()

    return flask.redirect(flask.url_for('search_page'))


@app.route('/search', methods=['GET'])
def search_page():
    """The search page of the web application.
    Adress: http://127.0.0.1:5000/search

    """

    if flask.request.method == 'GET':

        # HTTP GET parameter of the search request
        search_term = flask.request.args.get('searchTerm', '')
        search_path = flask.request.args.get('searchPath', '')
        date_from = flask.request.args.get('dateFrom', '')
        duration_from = flask.request.args.get('durationFrom', '')
        search_concept = flask.request.args.get('searchConcept', '')
        duration_to = flask.request.args.get('durationTo', '')
        date_to = flask.request.args.get('dateTo', '')
        result_number = flask.request.args.get('resultNumber', '')
        page_number = flask.request.args.get('pageNumber', '')
        search_id = flask.request.args.get('searchId', '')

        # user id of the session
        user_id = get_current_user_id()

        if user_id and (search_id or search_term or search_path or (date_from and date_to) or search_concept):

            # filters the search parameters
            search_parameter = filter_search_parameter(search_term, date_from, date_to, duration_from, duration_to,
                                                       search_path,
                                                       page_number, result_number, search_concept, user_id, search_id)

            # performs a search request
            result_list, result_list_len, found_concepts, found_concept_terms = model_controller.search_all_parameter(
                **search_parameter)

            # performs a search request
            current_search_concepts = get_concept_list(search_concept)

            # calculates the maximum of pages of the search result
            max_search_pages = get_max_pages(result_list_len, search_parameter['result_number'])

            return_string = flask.render_template('pages/search_result_page.html',
                                                  configuration=configuration,
                                                  result_list=result_list,
                                                  result_number_len=result_list_len,
                                                  search_parameter=search_parameter,
                                                  found_concepts=found_concepts,
                                                  found_concept_terms=found_concept_terms,
                                                  current_search_concepts=current_search_concepts,
                                                  max_search_pages=max_search_pages)

            return return_string
        else:
            return_string = flask.render_template('pages/search_form_page.html', configuration=configuration)
            return return_string
    else:
        flask.abort(404)


@app.route('/help', methods=['GET'])
def help_page():
    """The help page of the web application.
    Adress: http://127.0.0.1:5000/help

    """

    if flask.request.method == 'GET':

        return_string = flask.render_template('pages/help_page.html')
        return return_string
    else:
        flask.abort(404)


@app.route('/about', methods=['GET'])
def about_page():
    """The information page of the web application.
    Adress: http://127.0.0.1:5000/about

    """

    if flask.request.method == 'GET':

        return_string = flask.render_template('pages/about_page.html')
        return return_string
    else:
        flask.abort(404)


@app.route('/logout', methods=['GET'])
def logout_page():
    """The logout page of the web application.
    Adress: http://127.0.0.1:5000/about

    """

    if flask.request.method == 'GET':

        # checks if the user is logged in
        if is_correct_login():
            # deletes the user session
            make_correct_logout()

        return flask.redirect(flask.url_for('login_page'))
    else:
        flask.abort(404)


@app.route('/execute', methods=['GET'])
def execute_page():
    """The administration page for changes in the database of the web application.
    Adress: http://127.0.0.1:5000/execute

    """

    if flask.request.method == 'GET':

        # HTTP GET parameter of the request
        action_type = flask.request.args.get('action', '')

        if action_type and action_type == 'update':

            # updates the concept information
            model_controller.update_concept_mapping()
        else:
            flask.abort(404)
    else:
        flask.abort(404)


@app.route('/edit', methods=['GET', 'POST'])
def edit_page():
    """The page for RDF file editing of the web application.
    Adress: http://127.0.0.1:5000/edit

    """

    if flask.request.method == 'POST':
        # rdf file editing page
        # checks if the user is logged in
        if is_correct_login():

            # HTTP POST parameters of the upload request
            file_name = flask.request.form['storeFile']
            file_content = flask.request.form['fileContent']

            if file_name and file_content:
                model_controller.save_concept_file(file_content, file_name)

                return flask.redirect(flask.url_for('edit_page', fileName=file_name))
            else:
                return flask.redirect(flask.url_for('login_page'))
        else:
            return flask.redirect(flask.url_for('login_page'))
    elif flask.request.method == 'GET':

        # removes rdf files
        if is_correct_login():

            # HTTP GET parameters of the request
            remove_file_name = flask.request.args.get('removeFile', '')
            normal_file_name = flask.request.args.get('fileName', '')

            if remove_file_name:
                # removes the rdf files in the hard disc
                model_controller.remove_concept_file(remove_file_name)

                return flask.redirect(flask.url_for('login_page'))

            if normal_file_name:

                # reads the content of the rdf files
                file_content, file_info = model_controller.get_concept_file_information(normal_file_name)

                if file_content:
                    return_string = flask.render_template('pages/concept_edit_page.html',
                                                          file_content=file_content, file_info=file_info,
                                                          file_name=normal_file_name)
                    return return_string
                else:
                    return flask.redirect(flask.url_for('login_page'))
            else:
                return flask.redirect(flask.url_for('login_page'))
        else:
            return flask.redirect(flask.url_for('login_page'))
    else:
        flask.abort(404)


@app.route('/admin', methods=['GET', 'POST'])
def admin_page():
    """The administration page of the web application.
    Adress: http://127.0.0.1:5000/admin

    """

    if flask.request.method == 'POST':
        # upload of new rdf files

        # checks if the user is logged in
        if is_correct_login():

            # upload of new rdf files
            if 'uploadFile' in flask.request.files:

                file_object = flask.request.files['uploadFile']

                # stores the rdf files in the hard disc
                file_upload_success = model_controller.upload_concept_file(file_object)

                if file_upload_success:
                    return flask.redirect(flask.url_for('login_page'))
                else:
                    return flask.redirect(flask.url_for('login_page'))
        else:
            return flask.redirect(flask.url_for('login_page'))
    elif flask.request.method == 'GET':
        # lists all rdf files

        # checks if the user is logged in
        if is_correct_login():

            # upload of new rdf files
            file_concept_list = model_controller.get_concept_file_list()

            return_string = flask.render_template('pages/concept_overview_page.html', file_list=file_concept_list)
            return return_string
        else:
            return flask.redirect(flask.url_for('login_page'))
    else:
        flask.abort(404)


@app.route('/visualize', methods=['GET'])
def visualize_page():
    """The word visualization page of the web application.
    Adress: http://127.0.0.1:5000/visualize

    """

    if flask.request.method == 'GET':

        # HTTP GET parameter of the request
        visualize_term = flask.request.args.get('searchTerm', '')

        if not visualize_term:
            return flask.redirect(flask.url_for('visualize_page', searchTerm=configuration.SIMILARITY_COMPUTATION_DEFAULT_TERM))

        # returns a list of similar words
        visual_term_list = model_controller.get_similar_terms(visualize_term)

        if not visual_term_list:
            return flask.redirect(flask.url_for('visualize_page', searchTerm=configuration.SIMILARITY_COMPUTATION_DEFAULT_TERM))

        counter_list = [str(counter) for index, counter, term, string_term, color in visual_term_list]
        term_list = [str(term) for index, counter, term, string_term, color in visual_term_list]
        color_list = [str(color) for index, counter, term, string_term, color in visual_term_list]

        counter_string = ';'.join(counter_list)
        color_string = ';'.join(color_list)
        term_string = ';'.join(term_list)

        return_string = flask.render_template('pages/visualisation_page.html', visualize_list=visual_term_list,
                                              counter_string=counter_string,
                                              color_string=color_string, term_string=term_string,
                                              visualize_term=visualize_term)
        return return_string
    else:
        flask.abort(404)


@app.route('/bigram_statistic', methods=['GET'])
def statistic_bigram_page():
    """The bigram ranking of the web application.
    Adress: http://127.0.0.1:5000/bigram_statistic

    """

    if flask.request.method == 'GET':

        # returns a list of the most relevant bigrams
        bigram_term_list = model_controller.get_relevant_bigrams()

        return_string = flask.render_template('pages/relevant_bigram_page.html',
                                              bigram_list=bigram_term_list)
        return return_string
    else:
        flask.abort(404)


@app.route('/unigram_statistic', methods=['GET'])
def statistic_page():
    """The word ranking page of the web application.
    Adress: http://127.0.0.1:5000/unigram_statistic

    """

    if flask.request.method == 'GET':

        # returns a list of the highest ranked words
        relevant_term_list = model_controller.get_relevant_terms()

        return_string = flask.render_template('pages/relevant_unigram_page.html',
                                              relevant_list=relevant_term_list)
        return return_string
    else:
        flask.abort(404)


@app.route('/frequent', methods=['GET'])
def frequent_page():
    """The keyword ranking page of the web application.
    Adress: http://127.0.0.1:5000/frequent

    """

    if flask.request.method == 'GET':

        # returns a list of frequently used search terms
        frequent_term_list = model_controller.get_search_terms()

        return_string = flask.render_template('pages/frequent_page.html', frequent_list=frequent_term_list)
        return return_string
    else:
        flask.abort(404)


@app.route('/history', methods=['GET'])
def history_page():
    """The search history page of the web application.
    Adress: http://127.0.0.1:5000/history

    """

    if flask.request.method == 'GET':

        # returns a list of keywords of the past search queries
        history_term_list = model_controller.get_search_history()

        return_string = flask.render_template('pages/history_page.html', history_list=history_term_list)
        return return_string
    else:
        flask.abort(404)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    """The login page of the web application.
    Adress: http://127.0.0.1:5000/visualize

    """

    if flask.request.method == 'GET':

        # checks if the user is logged in
        if is_correct_login():
            return flask.redirect(flask.url_for('admin_page'))

        return_string = flask.render_template('pages/login_page.html')

        return return_string
    elif flask.request.method == 'POST':

        # HTTP GET parameter of the request
        admin_password = flask.request.form.get('password')

        # checks if the password is correct
        if admin_password.strip() == configuration.ADMINISTRATION_PASSWORD:
            # stores the password in the session
            flask.session['password'] = flask.request.form.get('password')

            return flask.redirect(flask.url_for('admin_page'))

        return flask.redirect(flask.url_for('login_page'))
    else:
        flask.abort(404)


def set_user_id():
    """Creates a unique user id in the session.

    """

    # the session is stored permanently
    flask.session.permanent = True

    flask.session['userid'] = str(uuid.uuid4())


def get_current_user_id():
    """Returns the user id of the session.

    """

    user_id = ""

    # checks if the user id is already created
    if 'userid' in flask.session:
        user_id = flask.session['userid']
    else:
        set_user_id()

    return user_id


def is_correct_login():
    """Returns the user id of the session.

    """

    # checks if the password is already stored in the session
    if 'password' in flask.session:

        # checks if the password is correct
        if flask.session['password'] == configuration.ADMINISTRATION_PASSWORD:
            return True  #

    return False


def make_correct_logout():
    """Logs the user out of the system.

    """

    # checks if the password is already stored in the session
    if 'password' in flask.session:
        # remove the password form the session
        flask.session['password'] = ''


def get_max_pages(result_list_len, result_number):
    """Calculates the maximum number of pages of the search result.

    """

    max_pages, reminder = divmod(result_list_len, result_number)
    return max_pages + 1


def get_concept_list(search_concepts):
    """Returns a list of concepts.

    """

    if search_concepts and (',' in search_concepts):
        return search_concepts.splitt(',')
    else:
        return list(search_concepts)


def filter_search_parameter(search_term, date_from, date_to, duration_from, duration_to, search_path,
                            page_number, result_number, search_concept, user_id, search_id):
    """Initializes the GET parameters of the search request.

    """

    # default values of the GET parameters
    search_term_default = None
    duration_from_default = None
    duration_to_default = None
    date_to_default = None
    date_from_default = None
    page_number_default = 1
    result_number_default = configuration.SEARCH_RESULT_DEFAULT_RESULT_NUMBER
    search_path_default = None
    search_concept_default = None
    user_id_default = None
    search_id_default = None

    if search_term:
        search_term_default = search_term

    if search_concept:
        search_concept_default = search_concept

    # convert the audio duration to milliseconds
    if duration_from and (duration_from != configuration.SEARCH_RESULT_DEFAULT_DURATION_FROM):
        with contextlib.suppress(BaseException):
            duration_from_default = int(duration_from) * 1000

    # convert the audio duration to milliseconds
    if duration_to and (duration_to != configuration.SEARCH_RESULT_DEFAULT_DURATION_TO):
        with contextlib.suppress(BaseException):
            duration_to_default = int(duration_to) * 1000

    # converts the creation date to a timestamp
    if date_to and (date_to != configuration.SEARCH_RESULT_DEFAULT_TIMESTAMP_TO):
        with contextlib.suppress(BaseException):
            date_to_default = int(datetime.datetime.strptime(date_to, "%d.%m.%Y").timestamp())

    # converts the creation date to a timestamp
    if date_from and (date_from != configuration.SEARCH_RESULT_DEFAULT_TIMESTAMP_FROM):
        with contextlib.suppress(BaseException):
            date_from_default = int(datetime.datetime.strptime(date_from, "%d.%m.%Y").timestamp())

    if page_number:
        with contextlib.suppress(BaseException):
            page_number_default = int(page_number)

    if result_number:
        with contextlib.suppress(BaseException):
            result_number_default = int(result_number)

    if search_path:
        search_path_default = search_path

    if user_id:
        user_id_default = user_id

    if search_id:
        search_id_default = search_id

    # dictionary (hashmap) of all search parameter
    search_parameter = {'search_term': search_term_default,
                        'date_from': date_from_default,
                        'date_to': date_to_default,
                        'duration_from': duration_from_default,
                        'duration_to': duration_to_default,
                        'search_path': search_path_default,
                        'page_number': page_number_default,
                        'result_number': result_number_default,
                        'search_concept': search_concept_default,
                        'user_id': user_id_default,
                        'search_id': search_id_default}

    return search_parameter

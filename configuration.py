import multiprocessing
import os
import nltk

from whoosh.fields import Schema, TEXT, KEYWORD, ID, NUMERIC
from whoosh.analysis import RegexTokenizer, LowercaseFilter

# Defines the main location of the application
GLOBAL_WORKING_PATH = os.path.dirname(__file__)

# Defines the maximum number of audio files in all steps of the data processing
GLOBAL_MAX_FILES = 1000000

# Defines the secret key of the web server flask for the session encryption
FLASK_SECRET_KEY = '\xde\x80\xb7\xa9\xb27\x16\xe4\x83\x0ch\xde\xb87n\x01\xa7j\x86/\xf7{#\xb5'

# Defines the maximum number of audio files in the indexing phase of the data processing
DATA_INDEXING_MAX_FILES = GLOBAL_MAX_FILES

# Defines the index name of the whoosh framework
DATA_INDEXING_WHOOSH_INDEX_NAME = "campus_wave"

# Defines the folder of the index of the retrieval system
DATA_INDEXING_WHOOSH_INDEX_LOCATION = GLOBAL_WORKING_PATH + r"\server\static\model\search_index"

# Defines a new tokenizer for the retrieval system whoosh
DATA_INDEXING_WHOOSH_ANALYZER = RegexTokenizer() | LowercaseFilter()

# Defines a list of data attributes for the indexing process of the retrieval system
DATA_INDEXING_WHOOSH_SEARCH_FIELDS = ['speech_text', 'important_words', 'file_location', 'file_creation_date',
                                      'audio_file_duration', 'important_concepts', 'file_id']

# Defines a list of data attributes of the index structure of the retrieval system
DATA_INDEXING_WHOOSH_SCHEME = Schema(
    file_id=KEYWORD(stored=True, scorable=True),
    file_location=TEXT(stored=True, phrase=True),
    file_name=ID(stored=True),
    file_type=ID(stored=True),
    file_creation_date=NUMERIC(stored=True),

    audio_file_name=ID(stored=True, unique=True),
    audio_file_location=ID(stored=True),
    audio_file_duration=NUMERIC(stored=True),
    audio_file_part=NUMERIC(stored=True),

    speech_text=TEXT(analyzer=DATA_INDEXING_WHOOSH_ANALYZER, stored=True),
    important_words=KEYWORD(stored=True, scorable=True),
    important_concepts=KEYWORD(stored=True, scorable=True)
)

# Defines the location of the JSON file after the information extraction phase
INFORMATION_EXTRACTION_STORAGE_FILE = GLOBAL_WORKING_PATH + r"\server\static\model\text_database_storage.json"

# Defines the maximum number of audio file of the information extraction phase
INFORMATION_EXTRACTION_MAX_FILES = GLOBAL_MAX_FILES

# Defines a list of german stop words
INFORMATION_EXTRACTION_GERMAN_STOP_WORD_LIST = set(nltk.corpus.stopwords.words('german'))

# Defines a list of german adjectives
INFORMATION_EXTRACTION_GERMAN_MORE_STOP_WORDS = set(list(
    ['eigenes', 'sofort', 'beste', 'ehrlich', 'absolut', 'b', 'freien', 'möchten', 'alt', 'eins', 'tun', 'zurück', 'a',
     'echte', 'falls', 'herzlich', 'i', 'neun', 'aktuelle', 'inneren', 'gesagt', 'weitere', 'darauf', 'viel', 'froh',
     'n', 'älteren', 'leichte', 'laut', 'interessante', 'lang', 'teil', 'größte', 'besonderes', 'vielen', 'drei',
     'lustig', 'wirklich', 'erster',
     'letzteren', 'kurz', 'erfährt', 'schnell', 'statt', 'eigene', 'dürfen', 'offene', 'klein', 'hält', 'fertig',
     'schon', 'vorsichtig',
     'selben', 'jungen', 'nn', 'ne', 'hälfte', 'gemeinsame', 'eigentlich', 'ps', 'schön', 'bedeutet', 'unglaublich',
     'extrem', 'c', 'damals',
     'wäre', 'umfassend', 'ebene', ' and ', 'x', 'bereit', 'kommen', 'darf', 'sieben', 'ungefähr', 'falsch',
     'schlimmer', 'gleichzeitig', 'völlig', 'gibt',
     'echten', 'alte', 'kleinsten', 'daher', 'gutes', 'liegt', 'sechs',
     'vier', 'voller', 'rund', 'vorbei', 'einfache', 'seid', 'kleinen', 'bewusst', 'halben', 'warum', 'ab', 'nähe',
     'letzten', 'intensiv', 'vierte', 'möchte', 'teuer', 'voll', 'j', 'weiteres', 'fast', 'schlechter', 'maß',
     'anscheinend', 'acht',
     'neuen', 'nein', 'einfachen', 'unmittelbar', 'früher', 'schöner', 'positive', 'ältere', 'falschen', 'besten',
     'kleine',
     'ernsthaft', 'bestes', 'müssen', 'vorstellen', 'anstatt', 'tätig', 'höher', 'zusammen', 'abschließend',
     'plötzlich',
     'schlechte', 'später', 'neue', 'schönes', 'großen', 'stärker', 'offen', 'gesamte', 'geben', 'langsam', 'eng',
     'leider', 'dritte',
     'wahrscheinlich', 'frei', 'sinnlos', 'halten', 'dauer', 'folgendes', 'einfach', 'neues', 'zweite', 'ähnliche',
     'modernen',
     'f', 'definitiv', 'aktive', 'schönen', 'unmöglich', 'letztere', 'größer', 'mehr', 'dritter', 'effektiver',
     'weniger',
     'normale', 'weiteren', 'mal', 'sollten', 'frisch', 'richtigen', 'mittleren', 'bekannt', 'aufgenommen', 'wobei',
     'zweitens', 'einzelne', 'ja',
     'mehrfach', 'erste', 'geht', 'direkte', 'neuer', 'drittel', 'klar', 'genannten',
     'o', 'of', 'kurzen', 'künftigen', 'aktiv', 'schöne', 'erst', 'denen', 'weiterer', 'übrigen', 'dar', 'ersten',
     'persönlich', 'erachtens', 'letzte', 'langer', 'zehn', 'zusätzlich', 'passend', 'guter', 'nahe', 'gegenteil',
     'groß', 'wahren', 'fällen', 'sagt', 'arme', 'häufig', 'weiß', 'gehen', 'wahr', 'komplette', 'fünf', 'hoch',
     'hilfreich', 'unserer', 'dass', 'findet', 'jetzigen', 'früh', 'saß', 'ähnliches',
     'seit', 'wo', 'schlecht', 'erstes',
     'gebracht', 'mögliche', 'e', 'worden', 'feste', 'zweiter', 'hal', 'einseitig',
     'obwohl', 'nehmen', 'klug', 'entweder', 'höhe', 'leicht', 'verständlich', 'gab', 'folgende', 'exakt', 'zwei',
     'fünfte', 'letzter', 'viele', 'guten', 'gut', 'to', 'weit', 'neu', 'gute',
     'ähm', 'kleines', 'ernst', 'genau', 'fall', 'richtig', 'alten', 'sicher', 'möglich', 'direkt', 'sinne', 'weise',
     'wichtigen', 'deutlich', 'letztendlich', 'einzelnen', 'ganz',
     'relativ', 'öffentlichen', 'politischen', 'grunde', 'alter', 'entfernt', 'gesamten', 'bisschen', 'junge',
     'verschiedenen', 'wichtige'
        , 'langen', 'erneut', 'enthaltenen', 'positiv', 'erhalten', 'sofern', 'gleiche', 'lassen', 'großes', 'ganzes',
     'wichtiger', 'wurde', 'hart', 'klaren',
     'immer', 'lange', 'notwendig', 'sinnvoll', 'ähnlich', 'täglich', 'schwierig', 'besseren', 'verhelfen', 'kleiner',
     'momentan',
     'zufrieden', 'offensichtlich', 'bestimmten', 'enthaltenen', 'klare', 'finden', 'künftig', 'erfolgreich',
     'schnellen', 'stark',
     'bereichen', 'hoffentlich', 'kommenden', 'traurig', 'bestimmte', 'verantwortlich', 'leichter', 'heutigen', 'heute',
     'morgen', 'gestern', 'herzlichen', 'normalen',
     'harten', 'eindeutig', 'allgemeinen', 'wunderbare', 'wunderbar', 'besonderen', 'besondere', 'wichtigsten',
     'wenngleich', 'vergangenen', 'wichtiges', 'komplett', 'selbstverständlich', 'öffentliche', 'gutem', 'beginn'
        , 'allgemein', 'maximal', 'stellen', 'bevor', 'normal', 'schwarzen', 'brauchen', 'kurze', 'lässt', 'endlich',
     'natürlich',
     'zusammenhang', 'offenen', 'betrifft', 'vernünftig', 'wunderbar', 'bessere', 'einverstanden', 'höheren', 'kalt',
     'warm', 'setzen',
     'glücklich', 'willkomenen', 'ähnlichen', 'genauer', 'vergessenen', 'innerhalb', 'nächstes', 'gemeinsamen',
     'dankbar', 'danke', 'roten',
     'interessant', 'verstärkt', 'schwarze', 'zweitens', 'vollkommen', 'harte', 'zahlreiche', 'neueste', 'folgenden',
     'sowie', 'weitgehend',
     'wirklichen', 'aktuellen', 'anwesend', 'möglichen', 'sichtbar', 'allmählich', 'laufenden', 'gegenüber', 'täglichen'
        , 'vielfältigen', 'sehen', 'aufmerksam', 'halb', 'gemacht', 'ärmsten', 'vielfältig', 'verfügt', 'spontan',
     'ausdrücklich', 'zahlreichen', 'erklärt', 'lauter', 'treffen', 'jährlich', 'eigentlichen', 'hauptsächlich',
     'außerordentlich', 'heftig', 'inhaltlich', 'falsche', 'bekommen', 'bekannte', 'führt', 'einziges', 'kurzem',
     'verlassen',
     'starke', 'direkten', 'negativ', 'nett', 'grundlegend', 'automatisch', 'fähig', 'gespannt', 'breiten', 'ruhig',
     'zweites'
        , 'begeistert', 'größten', 'wichtigste', 'korrekt', 'enthält', 'schlicht', 'große', 'ganzen', 'eigenen',
     'zweiten', 'gleichen',
     'helfen', 'tatsächlich', 'gleichen', 'dringend', 'ganze', 'wichtig', 'komma', 'vehement', 'effektive',
     'besser', 'effektiv', 'nächsten', 'gehört', 'unzureichend', 'nächste', 'ständig', 'gemeinsam', 'm', 'and',
     'offenbar',
     'wirft', 'vorhanden', 'enthalten', 'letztes', 'richtige', 'dritten', 'the', 'einzigen', 'betont', 'öffentlich',
     'null', 'tief', 'w', 'unerwartet', 'großer', 'länger', 'fehlerhafte', 's', 'wesentlichen', 'höhere',
     'verschiedene', 'möglichkeiten', 'derartige', 'l', 'alternative', 'freie', 'unabhängig', 'gegenwärtig', 'r',
     'gehören', 'unendliche', 'ernsthafte', 'z', 'aktiven', 'anschließend', 'reale', 'dabei', 'grundsätzlich',
     'wenig', 'umhin', 'steht', 'schneller', 'nötig', 'naiv', 'erforderlich', 'wertvolle', 'jüngsten', 'nachdem',
     'dient', 'dafür', 'genügend', 'vorab', 'eventuell', 'bemüht', 'nämlich', 'näher', 'tut',
     'zuständig', 'persönliche', 'unfähig', 'entsprechend', 'entfernte', 'geplante', 'vollständig', 'zufällig',
     'geltenden', 'ehemaligen', 'äh', 'fehlende', 'oft', 'unfair', 'grundlegende', 'hohen', 'unhöflich', 'freiwillig',
     't', 'bereits', 'erinnern', 'höchste', 'erheblich', 'interne', 'heiße', 'eventuelle', 'gegenwärtigen',
     'überwiegend',
     'lediglich', 'dramatische', 'verfügen', 'damaligen', 'geeignete', 'überraschend', 'stets', 'unverzichtbar',
     'gleich', 'per', 'gäbe', 'kurzfristig', 'stärke', 'halbe', 'wer', 'verbesserte', 'etwa', 'indirekt', 'umfassenden',
     'seltsam', 'niemand', 'kleinste', 'besonders', 'hervorheben', 'auffällig', 'schweren', 'ha', 'handelt',
     'wertvollen',
     'zulässig', 'langfristig', 'ewig', 'klares', 'jetzige', 'gänzlich', 'gemeinsames', 'schwieriger', 'konnte',
     'ebenfalls'
        , 'zukünftige', 'entfernten', 'denkt', 'wirkt', 'aktuelles', 'erwähnte', 'leichtfertig', 'aktiver',
     'stirbt', 'regelmäßig', 'flexibler', 'gehabt', 'liegenden', 'öffentlicher', 'verhindern',
     'flexibler', 'gehabt', '	liegenden', 'verbindlich', 'verhindern', 'fortfahren', 'verehrten',
     'angemessene', 'vereinbar', 'verstärkte', 'entwickelt', 'natürlichen', 'allein', 'dürfte', 'hoher',
     'geeigneten', 'bringt', 'vertraut', 'getan', 'gleichsam', 'angeblich', 'leichten', 'schlechtes', 'erwähnten',
     'einsetzen', 'hoffe', 'grob', 'sagte', 'unendlichen', 'pfeift', 'unklar', 'gemäß', 'altes', 'schnelle'
        , 'effizient', 'bestimmt', 'veränderte', 'sinnvolle', 'hinaus', 'anfällig', 'schwierige', 'unverzüglich',
     'sichere', 'größeren', 'erwartet', 'einzelner', 'genug', 'überall', 'endgültigen', 'zukünftig'
        , 'zwingend', 'langem', 'zusätzliche', 'allgemeine', 'eigener', 'p', 'wesentliche', 'super', 'eigentliche',
     'helfende',
     'starken', 'ebenso', 'nächster', 'einfacher', 'speziell', 'eingeschränkter', 'erhoffte', 'größere'
        , 'durfte', 'fällt', 'neuesten', 'stellt', 'dahingehend', 'denke', 'erklärte', 'langweilig',
     'finde', 'davon', 'schlimm', 'prüfen', 'erhalt', 'mehrere', 'größe', 'schlechten', 'heißt'
        , 'effizienter', 'vielfältige', 'weiterhin', 'total', 'erfreut', 'führen', 'lächerlich', 'endgültige',
     'veröffentlicht', 'gegenseitig', 'generell', 'ständigen', 'höchsten', 'nachdrücklich', 'bringen'
        , 'anfänglich', 'eröffnen', 'g', 'ernste', 'erhebliche', 'erfolgt', 'vielleicht', 'ausreichend', 'festgelegt',
     'genannte', 'entschieden', 'engen', 'jeweiligen', 'fort', 'angemessen', 'betroffenen', 'heftige', 'künftige',
     'einzig', 'breite', 'wirksam', 'heftigen', 'außerhalb', 'zunehmend', 'positiven', 'ferner', 'einziger',
     'hohe', 'v', 'höchste', 'erinnern', 't', 'lediglich', 'riesige', 'laufend', 'seltener', 'gegenwärtige',
     'unterschiede', 'strenge', 'kostenlos', 'wesentlicher', 'fehlenden', 'harmlos', 'westliche',
     'bedeutende', 'niedrig', 'zeitlich', 'gewaltige', 'entsetzt', 'gesellschaftliche', 'ermutigend',
     'gesellschaftlichen', 'nachhaltigen', 'erfolgreichen', 'auffallend', 'stärkere', 'fester', 'anwendbar', 'häufiger',
     'gleichnamigen', 'fester', 'anwendbar', 'häufiger', 'gleichnamigen', 'absoluten', 'gleicher', 'übertrieben',
     'seltener', 'kostenlos', 'wesentlicher', 'fehlenden', 'harmlos', 'westliche', 'niedrig', 'stärkere',
     'gleichnamigen', 'gleicher', 'übertrieben', 'günstig', 'detaillierte', 'massive', 'vergeblich', 'dunklen',
     'korrekte', 'lädt', 'stehende', 'älteste', 'kalte', 'dicht', 'reichsten', 'hunderte', 'ernster',
     'fortwährend', 'knapp', 'besseres', 'harter', 'enorm', 'erweiterten', 'vollem', 'wachsende',
     'leer', 'interessiert', 'verletzten', 'echter', 'negative', 'billig', 'vermeintliche',
     'vereinfachten', 'flexible', 'legale', 'schwierigen', 'bekanntes', 'schlimmsten', 'verrückt', 'damalige',
     'entsprechende', 'machbar', 'geeignet', 'schädlich', 'heiß', 'schrecklich', 'entsprechenden', 'sinnvoller',
     'reichlich', 'veränderten', 'stärksten', 'kosteneffektiv', 'dramatisch', 'externe',
     'übrig', 'innere', 'scheinbar', 'enormen', 'verschiedensten', 'gewisser', 'ständige',
     'zusätzlichen', 'erkennbar', 'permanent', 'weißen', 'la', 'entwickelten', 'verehrter', 'konkreten',
     'sauber', 'bestehenden', 'denkbar', 'schlimmste', 'verfügbar', 'gelassen', 'öfter',
     'veraltet', 'festen', 'offizielle', 'scharfe', 'offener', 'annähernd', 'derzeitige',
     'vernünftigen', 'gefragt', 'weiße', 'zuständigen', 'laufende', 'unterschiedlichen', 'großteil',
     'entscheidende', 'dauerhaft', 'friedliche', 'abbruch', 'geschehen', 'mühsam'
        , 'gewaltigen', 'flexibel', 'wirksame', 'absolute', 'verheugen', 'fleißig', 'weite',
     'verbindliche', 'erfolgreiche', 'ehemalige', 'vielzahl', 'unterschiedlich'
        , 'ursprünglich', 'anhaltende', 'sogenannte', 'jüngste', 'entdeckt',
     'klassischen', 'erhöhte', 'gerecht', 'junger', 'kritisch'
        , 'handvoll', 'kompliziert', 'fehlerhaft', 'schwachen', 'persönlichen', 'veröffentlichte'
        , 'konsequent', 'kommende', 'gefährliche', 'billiger', 'vorhandenen', 'kritische',
     'erstmalig', 'privaten', 'menschlichen', 'anerkannten', 'extreme', 'fairen', 'enorme', 'erhöht', 'besorgt'
        , 'gelegentlich', 'verzweifelt', 'verhängnisvollen', 'zweifellos', 'unterschiedliche', 'wunderschönen'
        , 'geplanten', 'fahrverhalten', 'wertvoll', 'vernünftige', 'notwendige', 'spannend', 'einstimmig',
     'sogenannten', 'einheitlichen', 'ordentlich', 'erfreulich', 'entferntesten', 'zentralen', 'individuelle'
        , 'wahnsinnig', 'enge', 'moderne', 'ausführlich', 'achten', 'beteiligten'
        , 'intelligente', 'endgültig', 'befinden', 'bekannten', 'entscheidend', 'perspektiven',
     'tiefer', 'unentdeckt', 'gefährlich', 'einheitliche', 'vereinigten', 'externen',
     'praktisch', 'internen', 'intensive', 'fit', 'verantwortlichen', 'perspektive'
        , 'sorgfältig', 'notwendigen', 'unerlässlich', 'abhängig', 'gewisse', 'vereinten',
     'veröffentlichten', 'unerwähnt', 'wesentlich', 'unverändert', 'selten', 'effektiven',
     'möglichkeit', 'perfekt', 'unendlich', 'einzige']))

# Defines a list of german adjectives and stopwords
INFORMATION_EXTRACTION_FINAL_GERMAN_STOP_WORD_LIST = INFORMATION_EXTRACTION_GERMAN_STOP_WORD_LIST | \
                                                     INFORMATION_EXTRACTION_GERMAN_MORE_STOP_WORDS

# Defines the folder of the RDF files in the hard disc
INFORMATION_EXTRACTION_RDF_STORAGE = GLOBAL_WORKING_PATH + r"\server\static\rdf"

# Defines all relevant parts of speech tags of the keyword extraction phase
INFORMATION_EXTRACTION_NOUN_TAGS = ['NOUN', 'PROPN', 'ADJ', 'X']

# Defines a list of non relevant file names in the file path
INFORMATION_EXTRACTION_PATH_WRONG_KEYWORDS = set(value for value in ['mp', 'd', 'recin'])

# Defines a list of chars which are removed in the file path
INFORMATION_EXTRACTION_PATH_REPLACE_DICT = {'\\': ' ', '.': ' ', '_': ' ', '-': ' ', '~': ' ', '': ' ', ':': ' ',
                                            ',': ' ',
                                            '&': ' ', '(': ' ', ')': ' ', '#': ' ', '0': ' ', '1': ' ', '2': ' ',
                                            '3': ' ',
                                            '4': ' ', '5': ' ', '6': ' ', '7': ' ', '8': ' ', '9': ' ', }

# Defines the location of the data set (JSON file) after the speech recognition process
SPEECH_RECOGNITION_JSON_STORAGE_FILE = GLOBAL_WORKING_PATH + r"\server\static\model\speech_database_storage.json"

# Defines the Hidden Markov Model of the speech recognition framework sphinx
SPEECH_RECOGNITION_POCKET_SPHINX_HMM = GLOBAL_WORKING_PATH + \
                                       r"\server\static\sphinx_model\model_parameters\voxforge.cd_ptm_5000"

# Defines the Language Model model of the speech recognition framework sphinx
SPEECH_RECOGNITION_POCKET_SPHINX_LM = GLOBAL_WORKING_PATH + r"\server\static\sphinx_model\etc\voxforge.lm.DMP"

# Defines the Dictionary of the speech recognition framework sphinx
SPEECH_RECOGNITION_POCKET_SPHINX_DICT = GLOBAL_WORKING_PATH + r"\server\static\sphinx_model\etc\voxforge.dic"

# Defines a list of parameter of the framework sphinx in the speech recognition process
SPEECH_RECOGNITION_POCKET_SPHINX_CONFIG = {
    'hmm': SPEECH_RECOGNITION_POCKET_SPHINX_HMM,
    'lm': SPEECH_RECOGNITION_POCKET_SPHINX_LM,
    'dict': SPEECH_RECOGNITION_POCKET_SPHINX_DICT,
    'audio_device': None,
    'remove_noise': True,
    'remove_silence': True,
    'round_filters': True,
}

# Defines the first probability threshold in filtering process of wrong recognized words
SPEECH_RECOGNITION_FIRST_PROBABILITY_THRESHOLD = - 20000

# Defines the second probability threshold in filtering process of wrong recognized words
SPEECH_RECOGNITION_SECOND_PROBABILITY_THRESHOLD = - 14000

# Defines the maximum number of audio files in the speech recognition process
SPEECH_RECOGNITION_MAX_FILES = GLOBAL_MAX_FILES

# Defines the number of audio files which are processed in one processing step in the speech recognition process
SPEECH_RECOGNITION_CALCULATION_BATCH_NUMBER = 25

# Defines the number of cores of the parallel speech recognition process
SPEECH_RECOGNITION_CALCULATION_CORES = multiprocessing.cpu_count() - 1

# Defines a char for wrongly recognized words of the speech recognition process
SPEECH_RECOGNITION_UNKNOWN_SPEECH_TERM = 'u'

# Defines list of meta information of the speech recognition framework sphinx which are mapped to defined set chars
SPEECH_RECOGNITION_WRONG_TERMS_DICT = {'<sil>': '', '<s>': '.', '</s>': '.'}

# Defines the words to seconds ratio for the advanced classification of speech data
SPEECH_RECOGNITION_MINIMAL_TOKENS_SECONDS_RATIO = 1.4

# Defines the default duration of one audio segment in the audio processing phase
AUDIO_PROCESSING_PART_SIZE_MILLISECONDS = 60 * 1000

# Defines the overlap duration between two audio segments in the audio processing phase
AUDIO_PROCESSING_PART_SIZE_OVERLAP = 2 * 1000

# Defines the minimum duration of one audio file in the audio processing phase
AUDIO_PROCESSING_MIN_DURATION = 8 * 1000

# Defines the maximum duration of one audio file in the audio processing phase
AUDIO_PROCESSING_MAX_DURATION = 60 * 60 * 1000

# Defines the back up folder of all audio segments in the audio processing phase
AUDIO_PROCESSING_STORAGE_DICTIONARY = GLOBAL_WORKING_PATH + r"\server\static\data\audio_database"

# Defines the backup folder of all audio segments of the audio processing phase
AUDIO_PROCESSING_RELATIVE_STORAGE_DICTIONARY = "/static/data/audio_database/"

# Defines the location of the data set (JSON file) after the audio processing phase
AUDIO_PROCESSING_STORAGE_FILE = GLOBAL_WORKING_PATH + r"\server\static\model\audio_database_storage.json"

# Defines the maximum number of audio files of the audio processing phase
AUDIO_PROCESSING_MAX_FILES = GLOBAL_MAX_FILES

# Defines the number of channels of the audio file of the audio processing phase
AUDIO_PROCESSING_CHANNELS = 1

# Defines the maximum sound volume (dBFS) of the audio file of the audio processing phase
AUDIO_PROCESSING_OPTIMAL_LOUDNESS = -20

# Defines the sampling frequency of the audio file of the audio processing phase
AUDIO_PROCESSING_SAMPLE_RATE = 16000

# Defines the frame resolution (Bytes) of the audio file of the audio processing phase
AUDIO_PROCESSING_FRAME_WIDTH = 2

# Defines the audio format of the audio file of the audio processing phase
AUDIO_PROCESSING_DEFAULT_FILE_TYPE = 'wav'

# Defines a correct list of audio format extensions of the data filtering phase
DATA_FILTERING_SUPPORTED_FILE_TYPES = ['wav', 'mp3']

# Defines a list of correct file names for the classification of all relevant audio files of the data filtering phase
DATA_FILTERING_INCLUDED_FILE_NAMES = ['beitrag', 'umfrage', 'sendung', 'service', 'interview',
                                      'nachrichten', 'abmischung', 'aufnahme',
                                      'transition', 'mensa',
                                      'opener', 'diskussion', 'halbzeit',
                                      'mixdown', 'o-ton', 'vortrag', 'beiträge', 'vtipps',
                                      'hochschulgruppe', 'kommentar', 'nachgefragt']

# Defines a list of incorrect dir names for the classification of all relevant audio files of the data filtering phase
DATA_FILTERING_EXCLUDED_FILE_PATHS = [r"soundeffekte zum basteln", r"\Unknown Artist\Unknown Album",
                                      r"\Scheinwerfer\Musik", r"\Archiv\Musik", r"\Musik\A", r"\Musik\Formate",
                                      r"\Musik\Hot Rotation", r"\Musik\Lauschrausch", r"\Musik\Musikarchiv",
                                      r"\Musik\Interpreten", r"\iTunes Music\Music",
                                      r"\Ressorts\Musik\Musik", r"\Musik von Maxi\iTunes"]

# Defines a list of incorrect file names for the classification of all relevant audio files of the data filtering phase
DATA_FILTERING_EXCLUDED_FILE_NAMES = ['bob moses', 'instrumental', 'james blunt', 'blumentopf',
                                      'cd0track', 'chasing stars', 'david guetta', 'depeche mode',
                                      'dj_bloxx', 'backstreet boys', 'fatboy slim', 'glassbyrd',
                                      'hq_20140', 'party hits', 'james brown', 'kill bill', 'madsen',
                                      'maroon 5', 'taio cruz', 'robbie williams', 'rock of ages', 'wayne kirkpatrick',
                                      'samuel harfst', 'seeed', 'spongebob', 'supervision', '!llflow', 'green day',
                                      'labrassbanda',
                                      'queen', 'sdp ', 'shakira', 'sido ', 'Track']

# Defines the minimum file size (bytes) of a relevant audio file in the data filtering phase
DATA_FILTERING_MIN_FILE_SIZE = 838860

# Defines the maximum file size (bytes) of a relevant audio file of the data filtering phase
DATA_FILTERING_MAX_FILE_SIZE = 102914560

# Defines the folder of the indexing process of the data filtering phase
DATA_FILTERING_START_DICTIONARY = "D:\\"

# Defines the maximum number of audio files of the data filtering phase
DATA_FILTERING_MAX_FILES = GLOBAL_MAX_FILES

# Defines the location of the data set (JSON file) after the file filtering phase
DATA_FILTERING_STORAGE_FILE = GLOBAL_WORKING_PATH + r"\server\static\model\file_database_storage.json"

# Defines the number of bytes for the calculation of the file id (hash value) of the file filtering phase
DATA_FILTERING_MD5_HASH_BYTES = 8192 * 4

# Defines the back up folder of all audio files of the file filtering phase
DATA_FILTERING_STORAGE_DICTIONARY = GLOBAL_WORKING_PATH + r"\server\static\data\file_database"

# Defines the relative path of the back up folder of all audio files
DATA_FILTERING_RELATIVE_STORAGE_DICTIONARY = "/static/data/file_database/"

# Defines maximum number of concepts of the concept summary of the search result
SEARCH_RESULT_MAX_CONCEPTS_SUMMARY = 16

# Defines maximum number of keywords of each entry in the search result
SEARCH_RESULT_MAX_IMPORTANT_TERMS = 28

# Defines maximum number of recognized words of each entry of the search result
SEARCH_RESULT_MAX_RECOGNIZED_WORDS = 80

# Defines the char of wrongly recognized words of each entry of the search result
SEARCH_RESULT_UNKNOWN_TOKEN = '~'

# Defines maximum number of entries in the search result
SEARCH_RESULT_DEFAULT_RESULT_NUMBER = 25

# Defines the default value of the creation date search in the search result
SEARCH_RESULT_DEFAULT_TIMESTAMP_TO = "31.12.2017"

# Defines the default value of the creation date search in the search result
SEARCH_RESULT_DEFAULT_TIMESTAMP_FROM = "01.01.2000"

# Defines the default value (seconds) of the duration search in the search result
SEARCH_RESULT_DEFAULT_DURATION_FROM = '1'

# Defines the default value (seconds) of the duration search in the search result
SEARCH_RESULT_DEFAULT_DURATION_TO = '3600'

# Defines number of keywords which were used in past queries
SEARCH_HISTORY_MAX_RESULTS = 60

# Defines the location of the data set (JSON file) of the entered keywords
SEARCH_HISTORY_STORAGE_FILE = GLOBAL_WORKING_PATH + r"\server\static\model\search_history_storage.json"

# Defines the location of the data set (JSON file) of the keyword ranking
KEYWORD_RANKING_WEIGHT_STORAGE_FILE = GLOBAL_WORKING_PATH + r"\server\static\model\relevant_terms_storage.json"

# Defines the location of the data set (JSON file) of the bigram ranking
KEYWORD_RANKING_BIGRAM_TERM_STORAGE_FILE = GLOBAL_WORKING_PATH + r"\server\static\model\relevant_bigram_terms_storage.json"

# Defines the maximum number of words which are displayed in the keyword ranking page
KEYWORD_RANKING_MAX_TERM_RESULTS = 2000

# Defines the maximum number of bigrams which are displayed in the bigram ranking page
KEYWORD_RANKING_MAX_BIGRAM_TERM_RESULTS = 100

# Defines the maximum number of words in the cluster groups in the keyword ranking page
KEYWORD_RANKING_MAX_RESULTS_PER_CLUSTER = 20

# Defines the number of cluster groups in the keyword ranking page
KEYWORD_RANKING_CLUSTER_NUMBER = 6

# Defines the maximum weight of the keywords in the keyword ranking page
KEYWORD_RANKING_MAX_WEIGHT_SCORE = 8

# Defines the minimal document length in the keyword ranking page
KEYWORD_RANKING_MINIMAL_DOCUMENT_LEN = 10

# Defines the location of the data set (JSON file) of the most frequently used keywords
SEARCH_TERM_STORAGE_FILE = GLOBAL_WORKING_PATH + r"\server\static\model\frequent_searches_storage.json"

# Defines the maximum number of words which are displayed in the search term page
SEARCH_TERM_MAX_RESULTS = 60

# Defines the default term of the semantic similarity page
SIMILARITY_COMPUTATION_DEFAULT_TERM = 'passau'

# Defines the maximum number of keywords which are used for the similarity computation
SIMILARITY_COMPUTATION_MOST_RELEVANT_TERMS_FOR_SIMILARITY = 2000

# Defines the maximum number of words in the semantic similarity page
SIMILARITY_COMPUTATION_MAX_RESULTS = 12

# Defines the location of the data set (JSON file) of the similarity computation
SIMILARITY_COMPUTATION_SIMILAR_STORAGE_FILE = GLOBAL_WORKING_PATH + r"\server\static\model\term_similarity_storage.json"

# Defines password of the administration page
ADMINISTRATION_PASSWORD = "studiocamera"

# Defines the allowed file extensions of the rdf files
ADMINISTRATION_ALLOWED_FILE_TYPES = ['rdf', 'rdfs']

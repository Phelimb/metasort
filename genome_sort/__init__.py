from os.path import join as join_path
from os import environ
from os import rename

import requests

_ALLOWED_EXTENSIONS = set(['fastq'])
_ONECODEX_APIKEY = environ['ONE_CODEX_API_KEY']
_BASE_API_URL = "https://beta.onecodex.com/api/v0/"
_UPLOAD_FOLDER = '/tmp'


def change_file_name(filename,sample_id):
    filepath = join_path(_UPLOAD_FOLDER, filename)
    rename(filepath, filepath.replace(filename.rsplit('.', 1)[0],sample_id))


def is_allowed_file(filename):
    is_valid_filename = '.' in filename
    has_valid_extension = filename.rsplit('.', 1)[1] in _ALLOWED_EXTENSIONS
    is_allowed_file = is_valid_filename and has_valid_extension
    return is_allowed_file


def upload_genome_file(filename):
    absolute_filename = join_path(
        _UPLOAD_FOLDER,
        filename
    )
    files = {'file': open(absolute_filename, 'rb')}
    response = requests.post(
        _BASE_API_URL + "upload",
        auth=(_ONECODEX_APIKEY, '',),
        files=files,
        allow_redirects=True,
    )
    return response.json()['sample_id']


def get_analyses():
    response = _get_request("analyses")
    return response.json()


def get_analysis_table_from_id(analysis_id):
    response = _get_request("analyses/{}/table".format(analysis_id))
    return response.json()


def _get_request(sub_url):
    response = requests.get(
        _BASE_API_URL + sub_url,
        auth=(_ONECODEX_APIKEY, ''),
        allow_redirects=True,
    )
    return response


def format_analyses(analyses):
    formatted_analyses = []
    for analysis in analyses:
        if analysis['analysis_status'] == 'Success':
            css_class = 'success'
        elif analysis['analysis_status'] == 'Pending':
            css_class = 'secondary disabled'
        elif analysis['analysis_status'] == 'Failed':
            css_class = 'alert'
        else:
            css_class = 'disabled'

        formatted_analysis = {
            'id': analysis['id'],
            'css_class': css_class,
            'sample_filename': analysis['sample_filename'],
        }
        formatted_analyses.append(formatted_analysis)
    return formatted_analyses


class AnalysisNotFound(Exception):
    pass


def get_sample_id_from_analysis_id(analysis_id):
    pass


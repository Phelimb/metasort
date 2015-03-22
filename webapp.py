from os.path import join as join_path
from os import environ
from os import listdir
import os

import requests
from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask import send_from_directory
from werkzeug import secure_filename
from src import sort

_APP = Flask(__name__)

_ALLOWED_EXTENSIONS = set(['fastq'])
_UPLOAD_FOLDER = '/tmp'
_APP.config['UPLOAD_FOLDER'] = _UPLOAD_FOLDER
_ONECODEX_APIKEY = environ['ONE_CODEX_API_KEY']
_BASE_API_URL = "https://beta.onecodex.com/api/v0/"


@_APP.route('/')
def index():
    files = []
    for file in listdir(_UPLOAD_FOLDER):
        if file.endswith(".fastq"):
            files.append(file)

    analyses = _get_analyses()
    analyses = [ana for ana in analyses if ana['reference_name'] == "One Codex Database"]
    analyses.reverse()
    formatted_analyses = _format_analyses(analyses)
    response = render_template(
        'index.html',
        analyses=formatted_analyses,
    )
    return response


@_APP.route('/upload_file', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file and _is_allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(join_path(_APP.config['UPLOAD_FOLDER'], filename))
        return redirect('/uploads/%s' % filename)
    else:
        return '<p>File error</p>'

@_APP.route('/analysis/<analysis_id>/<tax_id>')
def download_species_data(analysis_id,tax_id):
    uploads = join_path(_APP.config['UPLOAD_FOLDER'],analysis_id)
    return send_from_directory(directory=uploads, filename=tax_id+".fastq")

@_APP.route('/analysis/<analysis_id>')
def analysis(analysis_id):
    data = _get_analysis_table_from_id(analysis_id)
    response = render_template(
        'show_analysis.html',
        analysis_id=analysis_id,
        analysis_data=data,
    )
    return response

# @_APP.route('/sort_sequence/<analysis_id>')
# def sort_sequence(analysis_id):
#     data = _get_analysis_table_from_id(analysis_id)
#     FastqSorter(fasta_file_path,readlevel_assignment_tsv_file_path, analysis_id = "")
#     response = render_template(
#         'show_analysis.html',
#         analysis_id=analysis_id,
#         analysis_data=data,
#     )
#     return response    

  


@_APP.route('/uploads/<filename>')
def uploaded_file(filename):
    sample_id = _upload_genome_file(filename)
    _change_file_name(filename,sample_id)
    return redirect(url_for('index'))

def _change_file_name(filename,sample_id):
    filepath = join_path(_APP.config['UPLOAD_FOLDER'], filename)
    os.rename(filepath, filepath.replace(filename.rsplit('.', 1)[0],sample_id))


def _is_allowed_file(filename):
    is_valid_filename = '.' in filename
    has_valid_extension = filename.rsplit('.', 1)[1] in _ALLOWED_EXTENSIONS
    is_allowed_file = is_valid_filename and has_valid_extension
    return is_allowed_file


def _upload_genome_file(filename):
    absolute_filename = join_path(
        _APP.config['UPLOAD_FOLDER'],
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


def _get_analyses():
    response = _get_request("analyses")
    return response.json()


def _get_analysis_table_from_id(analysis_id):
    response = _get_request("analyses/{}/table".format(analysis_id))
    return response.json()


def _get_request(sub_url):
    response = requests.get(
        _BASE_API_URL + sub_url,
        auth=(_ONECODEX_APIKEY, ''),
        allow_redirects=True,
    )
    return response


def _format_analyses(analyses):
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


if __name__ == '__main__':
    _APP.run(host='0.0.0.0', debug=True)


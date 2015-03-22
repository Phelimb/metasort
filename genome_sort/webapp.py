from os.path import join as join_path
from os import listdir

from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask import send_from_directory
from werkzeug import secure_filename

from genome_sort import change_file_name
from genome_sort import get_analyses
from genome_sort import get_analysis_table_from_id
from genome_sort import get_sample_id_from_analysis_id
from genome_sort import is_allowed_file
from genome_sort import upload_genome_file
from genome_sort import format_analyses


APP = Flask(__name__)

_UPLOAD_FOLDER = '/tmp'
APP.config['UPLOAD_FOLDER'] = _UPLOAD_FOLDER


@APP.route('/')
def index():
    files = []
    for file in listdir(_UPLOAD_FOLDER):
        if file.endswith(".fastq"):
            files.append(file)

    analyses = get_analyses()
    analyses = [ana for ana in analyses if ana['reference_name'] == "One Codex Database"]
    analyses.reverse()
    formatted_analyses = format_analyses(analyses)
    response = render_template(
        'index.html',
        analyses=formatted_analyses,
    )
    return response


@APP.route('/upload_file', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file and is_allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(join_path(APP.config['UPLOAD_FOLDER'], filename))
        return redirect('/uploads/%s' % filename)
    else:
        return '<p>File error</p>'

@APP.route('/analysis/<analysis_id>/<tax_id>')
def download_species_data(analysis_id,tax_id):
    uploads = join_path(APP.config['UPLOAD_FOLDER'],analysis_id)
    return send_from_directory(directory=uploads, filename=tax_id+".fastq")

@APP.route('/analysis/<analysis_id>')
def analysis(analysis_id):
    data = get_analysis_table_from_id(analysis_id)
    response = render_template(
        'show_analysis.html',
        analysis_id=analysis_id,
        analysis_data=data,
    )
    return response

@APP.route('/sort_sequence/<analysis_id>')
def sort_sequence(analysis_id):
    sample_id = get_sample_id_from_analysis_id(analysis_id)
    fasta_file_path = join_path(APP.config['UPLOAD_FOLDER'],sample_id,'.fastq')
    readlevel_assignment_tsv_file_path = join_path(APP.config['UPLOAD_FOLDER'],"read_data_" + analysis_id,'.tsv')
    sorter = FastqSorter(fasta_file_path,readlevel_assignment_tsv_file_path, analysis_id = analysis_id)
    sorter.sort()
    sorter.write_sorted_files(out_dir = join_path(APP.config['UPLOAD_FOLDER'],analysis_id) )
    return redirect('/analysis/%s' % analysis_id)

@APP.route('/uploads/<filename>')
def uploaded_file(filename):
    sample_id = upload_genome_file(filename)
    change_file_name(filename,sample_id)
    return redirect(url_for('index'))

from os.path import join as join_path
from os import listdir
import os
import json
import glob 

from flask import Flask
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask import send_from_directory
from werkzeug import secure_filename

from metasort import change_file_name
from metasort import get_analyses
from metasort import get_analysis_table_from_id
from metasort import get_analysis_from_id
from metasort import get_sample_id_from_analysis_id
from metasort import is_allowed_file
from metasort import upload_genome_file
from metasort import format_analyses
from metasort import process_analysis
from metasort import get_taxon_to_species_dict

from sort import FastqSorter
APP = Flask(__name__)
APP.secret_key = 'saldjsaldjlsdlsjdal'

_UPLOAD_FOLDER = '/tmp'
APP.config['UPLOAD_FOLDER'] = _UPLOAD_FOLDER


@APP.route('/')
def index():
    # flash('Hello World', 'alert')
    # flash('Hello World', 'info')
    # flash('Hello World', 'success')
    # flash('Hello World', 'warning')
    files = []
    for file in listdir(_UPLOAD_FOLDER):
        if file.endswith((".fastq",".fq",".fa",".fasta")):
            files.append(file)

    analyses = get_analyses()    
    user_sample_list = request.cookies.get('samples',None)
    if user_sample_list is not None:
        user_sample_list = user_sample_list.split(",")
    else:
        user_sample_list = []
    analyses = [ana for ana in analyses if ana['reference_name'] == "One Codex Database" and get_sample_id_from_analysis_id(ana["id"]) in user_sample_list]
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
        filename = _change_file_ext_to_long(filename)
        file.save(join_path(APP.config['UPLOAD_FOLDER'], filename))
        return redirect('/uploads/%s' % filename)
    else:
        return '<p>File error</p>'

def _change_file_ext_to_long(filename):
    ext = filename.rsplit('.', 1)[1]
    if ext == "fq":
        filename = filename.replace("fq","fastq")
    elif ext == "fa":
        filename =filename.replace("fa","fasta")
    return filename

@APP.route('/analysis/<analysis_id>/<tax_id>')
def download_species_data(analysis_id,tax_id):
    uploads = join_path(APP.config['UPLOAD_FOLDER'],analysis_id)
    species = get_taxon_to_species_dict()[tax_id]
    filename = os.path.basename(glob.glob(uploads + "/*")[0])
    ext = filename.rsplit('.', 1)[1]
    return send_from_directory(directory=uploads, filename=filename,
                                attachment_filename="%s.%s" % (species,ext),
                                as_attachment = True)

@APP.route('/analysis/<analysis_id>')
def analysis(analysis_id):
    if not os.path.exists(join_path(APP.config['UPLOAD_FOLDER'],analysis_id)):
        return redirect("/sort_sequence/%s" % analysis_id)
    data = get_analysis_table_from_id(analysis_id)
    response = render_template(
        'show_analysis.html',
        analysis_id=analysis_id,
        analysis_data=data,
    )
    return response

@APP.route('/sort_sequence/<analysis_id>')
def sort_sequence(analysis_id):
    analysis = get_analysis_from_id(analysis_id)
    if analysis['analysis_status'] != "Success":
         flash('Please wait until analysis is complete (button will turn green)', 'alert')
         return redirect('/')
    else:
        sample_id = get_sample_id_from_analysis_id(analysis_id)
        process_analysis(analysis_id)
        fasta_file_path =  glob.glob(join_path(APP.config['UPLOAD_FOLDER'],sample_id + "*"))[0]
        readlevel_assignment_tsv_file_path = join_path(APP.config['UPLOAD_FOLDER'],"read_data_" + analysis_id + '.tsv')           
        sorter = FastqSorter(fasta_file_path,readlevel_assignment_tsv_file_path, analysis_id = analysis_id)
        sorter.sort()
        sorter.write_sorted_files(out_dir = join_path(APP.config['UPLOAD_FOLDER'],analysis_id) )
        return redirect('/analysis/%s' % analysis_id)

@APP.route('/uploads/<filename>')
def uploaded_file(filename):
    sample_id = upload_genome_file(filename)
    response = redirect(url_for('index'))
    user_sample_list = request.cookies.get('samples',"")
    response.set_cookie('samples',user_sample_list + "," + sample_id)
    change_file_name(filename,sample_id)    
    return response

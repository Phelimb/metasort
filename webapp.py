from os.path import join as join_path

from flask import Flask
from flask import request
from flask import redirect
from flask import url_for
from flask import render_template
from werkzeug import secure_filename
from flask import send_from_directory


APP = Flask(__name__)

ALLOWED_EXTENSIONS = set(['fastq'])
UPLOAD_FOLDER = '/tmp'
APP.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@APP.route('/')
def index():
    return render_template('index.html')

def _is_allowed_file(filename):
    is_valid_filename = '.' in filename
    has_valid_extension = filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
    is_allowed_file = is_valid_filename and has_valid_extension
    return is_allowed_file


@APP.route('/upload_file', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file and _is_allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(join_path(APP.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('index'))
    else:
        return '<p>File error</p>'


if __name__ == '__main__':
    APP.run(host='0.0.0.0', debug=True)


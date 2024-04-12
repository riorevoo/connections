from flask import Flask, request, jsonify, send_file
import time
import sys
import os
from io import StringIO
from flask_cors import CORS


sys.path.append(os.getcwd() + '/finalized_backend')
from Functions import CreateGraph, AddNodes, Vis, Networkx, MergeGraph, FilterGraph, SubGraph, SemanticGraph
from parse import parseData, Save
from SemanticScholarFuncs import AuthorSearch

app = Flask(__name__, static_url_path='/lib/bindings')
CORS(app, origins=['http://localhost:3000'], methods=['GET', 'POST'], allow_headers=['Content-Type'])


# It will contain the current command run and all the previous commands ran for that instance of the site
@app.route('/compile', methods=['POST'])
def compile_code():
    code = request.json['code']

    #parts = code.strip().split('\n')
    
    output = StringIO()  # Create StringIO object to capture output
    sys.stdout = output   # Redirect stdout to StringIO object
    
    start_time = time.time()
    try:
        # Execute code with custom function
        exec(code)
        runtime = time.time() - start_time
        output_str = output.getvalue()  # Get contents of StringIO object
        return jsonify({'output': output_str, 'runtime': runtime, 'error': None})
    except Exception as e:
        runtime = time.time() - start_time
        return jsonify({'output': None, 'runtime': runtime, 'error': str(e)})
    finally:
        sys.stdout = sys.__stdout__  # Reset stdout to its original value

@app.route('/get_graph', methods=['GET'])
def get_graph():
    var_name = request.args.get('varName')
    filepath = f"{os.getcwd()}/{var_name}.html"
    # return ERROR HERE for if graph name is not contained
    if os.path.exists(filepath):
        return send_file(filepath, mimetype='text/html')
    else:
        return jsonify({'output': None, 'error': f"No graph with the name {var_name} exists."})
    
@app.route('/save_graph', methods=['GET'])
def save_graph():
    var_name = request.args.get('varName')
    filepath = f"{os.getcwd()}/csv_list/{var_name}.csv"
    # return ERROR HERE for if graph name is not contained
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True, download_name=f'{var_name}.csv', mimetype='text/csv')
    else:
        return jsonify({'output': None, 'error': f"No graph with the name {var_name} exists."})
    
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return {'error': 'No file part'}, 400
    file = request.files['file']
    csv_name = request.form['csvName']
    # Do something with the file, e.g., save it to disk
    # errorChecking and check for errors before saving, change name of csv file
    csv = f'{os.getcwd()}/csv_list/{csv_name}'
    file.save(csv)
    try:
        parseData(csv)
    except Exception as e:
        return jsonify({'output': None, 'error': str(e)})
    return {'message': 'File uploaded successfully'}, 200

if __name__ == '__main__':
    app.run(debug=True)
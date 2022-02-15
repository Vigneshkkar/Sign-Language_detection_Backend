from flask import Blueprint, request, jsonify, send_from_directory
from flask_cors import cross_origin
from flaskr.db import get_all_records, save_documents
from bson import json_util
import json

dataset_v1 = Blueprint(
    'dataset_v1', 'dataset_v1', url_prefix='/api/v1/dataset')


@dataset_v1.route('/', methods=['GET'])
def api_get_root():
    data = [doc for doc in get_all_records()]
    response = {
        "data": data
    }
    return jsonify(json.loads(json_util.dumps(data)))


@dataset_v1.route('/savedata', methods=['POST'])
@cross_origin()
def api_save_data():
    payload = request.get_json()
    result = save_documents(payload['word'].lower(), payload['data'])

    return jsonify(success=result), 200 if result else 500

@dataset_v1.route('/static/<path:path>')
@cross_origin()
def send_js(path):
    return send_from_directory('static', path)
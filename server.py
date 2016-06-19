import os
import flask
import data
import pdb
from flask import request
from pymongo import MongoClient
app = flask.Flask(__name__)

# Setting up uploads
UPLOAD_FOLDER = 'images/'
ALLOWED_EXTENSIONS = set(['jpeg'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mongo_address = 'mongodb://omkar:photos123@ds037175.mlab.com:37175/photos'
client = MongoClient(mongo_address)
db = client.photos


@app.route('/')
def hello_world():
    return 'P H O T O S'


@app.route('/register', methods=['POST'])
def register():
    # get body of request
    request_body = request.get_json()

    users = db.users
    user_object = users.find_one({'number': request_body['number']})

    if not user_object:
        # Register user
        user_id = data.getNextId("userid")

        # Sanitize phone number
        number = data.sanitize_string(request_body['number'])

        user_object = {
            '_id': user_id,
            'name': request_body['name'],
            'number': number,
            'contacts': [],
            'photos': [],
            'owed_images': [],
            'events': []
        }

        users.insert_one(user_object)

    return flask.jsonify(user_object)


@app.route('/upload_contacts', methods=['POST'])
def upload_contacts():
    request_data = request.get_json()

    users = db.users
    user_id = int(request_data['user_id'])
    user = users.find_one({'_id': user_id})
    contacts_list = request_data['contacts']

    for contact in contacts_list:
        number = data.sanitize_string(contact['number'])
        name = contact['name']

        # Check that data exists
        if not (number or name):
            continue

        # Check that data is not a duplicate
        for cont in user['contacts']:
            if number == cont['number']:
                continue

        contact_id = data.getNextId("contactid")

        contact_object = {
            '_id': contact_id,
            'name': name,
            'number': number
        }

        user['contacts'].append(contact_object)

    users.update_one({'_id': user_id}, {'$set': user}, upsert=True)

    return flask.jsonify({
        'success': True
    })


@app.route('/get_events', methods=['POST'])
def get_events():
    user_id = request.get_json()['user_id']
    return flask.jsonify(data.get_user_events(int(user_id)))


@app.route('/upload_metadata', methods=['POST'])
def upload_metadata():
    metadata = request.get_json()

    # get collections
    users = db.users
    images = db.images

    # create image object
    image_id = metadata['identifier'].replace("/", "-")

    image_object = images.find_one({'identifier': image_id})
    if image_object:
        return flask.jsonify({"success": True})

    image_object = {
        'user_id': int(metadata['user_id']),
        'identifier': metadata['identifier'],
        'latitude': metadata['latitude'],
        'longitude': metadata['longitude'],
        'timestamp': metadata['timestamp'],
        'file': None,
        '_id': data.getNextId("imageid")
    }

    # add image to user
    user_id = image_object['user_id']
    user = users.find_one({'_id': user_id})
    if user:
        # add the blank image to the database
        user['photos'].append(image_id)
        images.insert_one(image_object)
        users.update_one({'_id': user_id}, {'$set': user}, upsert=True)

        # find a matching event for the metadata
        event = data.find_matching_event(image_object)
        user = users.find_one({'_id': user_id})
        if event['_id'] not in user['events']:
            user['events'].append(event['_id'])
        users.update_one({'_id': user_id}, {'$set': user}, upsert=True)

        should_upload = bool(image_id in user['owed_images'])
        return flask.jsonify({"success": True, 'upload': True})
    else:
        return flask.jsonify({"success": False, 'error': 'User not found.'})

    return flask.jsonify({"success": True})


@app.route('/upload_image', methods=['POST'])
def upload_image():
    file = request.files['file']
    identifier = file.filename.replace("/", "-")[:-4]
    filename = os.path.join(app.config['UPLOAD_FOLDER'], identifier)
    file_obj = db.images.find_one({"identifier": identifier})

    if file_obj is not None:
        if file_obj["file"] is None:
            # Let's save the file
            print "Saving file to " + filename
            file.save(filename)
            file_obj["file"] = filename
            db.images.update_one({'identifier': identifier}, {'$set': file_obj}, upsert=True)
            return flask.jsonify({
                "filename": filename,
                "success": True
            })
        else:
            # We already have the file saved, no need to upload it again
            return flask.jsonify({
                "filename": filename,
                "success": False,
                "message": "That image has already been uploaded! I don't want to upload it twice."
            })
    else:
        # We don't know what file the client is talking about.
        return flask.jsonify({
            "filename": filename,
            "success": False,
            "message": "Coldn't find the existing file object for this image!"
        })


@app.route('/get_owed_images', methods=['POST'])
def get_owed_images():
    metadata = request.get_json()
    users = db.users
    user_id = metadata['user_id']
    user = users.find_one({'_id': user_id})
    return user['owed_images']


@app.route('/images/<filename>')
def get_file(filename):
    filepath = "images/" + filename

    if os.path.isfile(filepath):
        resp = flask.make_response(open(filepath).read())
        resp.content_type = "image/jpeg"
        return resp
    else:
        return flask.jsonify({
            "error": "That file doesn't exist! :("
        })


if __name__ == "__main__":
    app.run(debug=True)

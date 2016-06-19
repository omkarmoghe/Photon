import os, flask, data, random, pdb
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
    return 'Hello, World!'


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
        number = request_body['number'].strip().replace("-","")

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

    contact_data  = request.get_json()
    users = db.users
    user_id = contact_data['user_id']
    user = users.find_one({'_id': user_id})

    for contact in contact_data:
        number = contact['number'].strip().replace("-","")
        name = contact_data['name']

        #Check that data exists
        if not number or name:
            continue

        #Check that data is not a duplicate
        for cont in user['contacts']:
            if number == cont['number']:
                continue

        contact_id = data.getNextId("contactid")

        contact_object = {
             '_id': contactid,
             'name': name,
             'number': number
        }

        user['contacts'].append(contact_object)

    # write back user object to database

    return flask.jsonify({
        'success': True
    })


@app.route('/get_events', methods=['POST'])
def get_events():
    user_id = request.form['user_id']
    return flask.jsonify(data.get_user_events(user_id))


@app.route('/upload_metadata', methods=['POST'])
def upload_metadata():
    metadata = request.get_json()

    # get collections
    users = db.users
    images = db.images

    # create image object
    image_id = data.getNextId("imageid")
    print image_id
    image_object = {
        'user_id': int(metadata['user_id']),
        'latitude': metadata['latitude'],
        'longitude': metadata['longitude'],
        'timestamp': metadata['timestamp'],
        'file': None,
        '_id': image_id
    }

    # add image to user
    user_id = image_object['user_id']
    print type(user_id)
    user = users.find_one({'_id': user_id})
    if user:
        # add the blank image to the database
        user['photos'].append(image_id)
        images.insert_one(image_object)

        # find a matching event for the metadata
        event = data.find_matching_event(image_object)
        user['events'].append(event['_id'])
    else:
        return flask.jsonify({"success": False, 'error': 'User not found.'})

    return flask.jsonify({"success": True})


@app.route('/upload_image', methods=['POST'])
def upload_image():
    file = request.files['file']
    filename = file.filename
    print "Saving file to images/"+filename
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    return flask.jsonify({
        "filename": filename,
        "success": True
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
    resp = flask.make_response(open("images/"+filename).read())
    resp.content_type = "image/jpeg"
    return resp



if __name__ == "__main__":
    app.run(debug=True)

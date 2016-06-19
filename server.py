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
    request_body = request.form

    users = db.users
    user_object = users.find_one({'number': request_body['number']})

    if not user_object:
        # Register user
        user_id = data.getNextId("userid")
        user_object = {
            '_id': user_id,
            'name': request_body['name'],
            'number': request_body['number'],
            'contacts': [],
            'photos': []
        }

        users.insert_one(user_object)

    return flask.jsonify(user_object)

@app.route('/upload_contacts', methods=['POST'])
def upload_contacts():
    data = request.form
    return flask.jsonify({
        'success': True
    })

@app.route('/get_events', methods=['POST'])
def get_events():
    user_id = request.form['user_id']
    return flask.jsonify(data.get_user_events(user_id))


@app.route('/upload_metadata', methods=['POST'])
def upload_metadata():
    metadata = request.form

    # get collections
    users = db.users
    images = db.images

    # create image object
    image_id = 1  # TODO: get unique id
    image_object = metadata
    image_object['file'] = None
    image_object['_id'] = image_id

    # add image to user
    user_id = image_object['user_id']
    user = users.find_one({'_id': user_id})
    if not user:
        return flask.jsonify({"success": False, 'error': 'User not found.'})
    else:
        user['photos'].append(image_id)

    return flask.jsonify({"success": True})

@app.route('/upload_image', methods=[])
def upload_image():
    file = request.files['file']
    filename = ''.join(random.choice('0123456789ABCDEF') for i in range(8))
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return flask.jsonify({
        "filename": filename,
        "success": True
    })






if __name__ == "__main__":
    app.run()

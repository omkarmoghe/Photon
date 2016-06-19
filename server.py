import os, flask, data, random
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

@app.route('/reg_user')
def reg_user():
    # Register user
    user_object = {
        contacts: [],
        photos: []
    }
    user_id = 1
    return flask.jsonify({
        'user_id': user_id
    })

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
    metadata = request.form['metadata']

    # See if there is a relevant event that this should be added to

    return flask.jsonify({"success"}: True)

@app.route('/upload_image', methods=[])
def upload_image():
    file = request.files['file']





if __name__ == "__main__":
    app.run()

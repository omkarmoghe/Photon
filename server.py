import flask
import data
app = flask.Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/reg_user')
def reg_user():
    # Register user
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



if __name__ == "__main__":
    app.run()

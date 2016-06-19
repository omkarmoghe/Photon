# set up mongo
from pymongo import MongoClient
mongo_address = 'mongodb://omkar:photos123@ds037175.mlab.com:37175/photos'
client = MongoClient(mongo_address)
db = client.photos

# Returns the next incremented ID for the given sequenceName (e.g userid, imageid).
def getNextId(sequenceName):
    sequenceDoc = db.counters.find_and_modify({
        'query': {'_id': sequenceName},
        'update': {'$inc': {'sequence_value': 1}},
        'new': True
    })
    return sequenceDoc.sequence_value

# TODO: MAGIC!
def get_user_events(user_id):
    return []

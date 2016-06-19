# set up mongo
from pymongo import MongoClient
from math import sin, cos, atan2, sqrt

mongo_address = 'mongodb://omkar:photos123@ds037175.mlab.com:37175/photos'
client = MongoClient(mongo_address)
db = client.photos


# Returns the next incremented ID for the given sequenceName (e.g userid, imageid).
def getNextId(sequenceName):
    sequenceDoc = db.counters.find_and_modify(
        {'_id': sequenceName},
        {'$inc': {'sequence_value': 1}},
        new=True
    )
    return sequenceDoc['sequence_value']


# TODO: MAGIC!
def get_user_events(user_id):
    pass


def find_matching_event(image_object):
    images = db.images
    events = db.events
    users = db.users

    img_latitude = image_object['latitude']
    img_longitude = image_object['longitude']
    img_timestamp = image_object['timestamp']
    img_id = image_object['_id']

    event_object = None

    matching_events = db.events.find()
    for event in matching_events:
        event_images = event['images']
        for event_image_id in event_images:
            event_image = images.find_one({'_id': event_image_id})
            
            if within_distance((img_latitude, img_longitude), (event_image['latitude'], event_image['longitude'])):
                if len(event_images) == 1:
                    last_image = images.find_one({'_id': event_images[0]})
                    print type(last_image)
                    last_owner = users.find_one({'_id': last_image['user_id']})
                    last_owner['owed_images'].append(last_image['_id'])
                event_images.append(img_id)
                img_user = users.find_one({'_id': image_object['user_id']})
                img_user['owed_images'].append(img_id)

                event_object = event
                break

    if not event_object:
        event_object = {
            '_id': getNextId('eventid'),
            'images': [img_id]
        }
        events.insert_one(event_object)

    return event_object


def within_distance(loc1, loc2):
    lat1, lon1 = float(loc1[0]), float(loc1[1])
    lat2, lon2 = float(loc2[0]), float(loc2[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    d = 3961 * c

    return d < 1

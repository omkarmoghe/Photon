# set up mongo
import geocoder
import datetime
import time
from pymongo import MongoClient
from math import sin, cos, atan2, sqrt

mongo_address = 'mongodb://omkar:photos123@ds037175.mlab.com:37175/photos'
client = MongoClient(mongo_address)
db = client.photos


# Returns the next incremented ID for the given sequenceName (e.g userid,
# imageid).
def getNextId(sequenceName):
    sequenceDoc = db.counters.find_and_modify(
        {'_id': sequenceName},
        {'$inc': {'sequence_value': 1}},
        new=True
    )
    return sequenceDoc['sequence_value']


# TODO: MAGIC!
def get_user_events(user_id):
    events_payload = list()

    users = db.users
    events = db.events
    images = db.images

    user = users.find_one({'_id': user_id})
    if not user:
        return {'error': 'user not found'}

    contacts = user['contacts']

    events_list = user['events']
    for event_id in events_list:
        event = events.find_one({'_id': int(event_id)})
        if event:
            image_list = event['images']

            # list with images containing real info
            images_payload = list()
            for image_id in image_list:
                image = images.find_one({'identifier': image_id})
                if image['file']:
                    if image_id in user['photos']:
                        image['owner'] = user['name']
                        images_payload.append(image)
                    else:
                        owner = users.find_one({'_id': int(image['user_id'])})
                        for contact in contacts:
                            if owner['number'] == contact['number']:
                                image['owner'] = owner['name']
                                images_payload.append(image)

            event['images'] = images_payload
            events_payload.append(event)

    events_payload.sort(key=lambda e: e['created_at'], reverse=False)
    return events_payload


def find_matching_event(image_object):
    images = db.images
    events = db.events
    users = db.users

    img_latitude = image_object['latitude']
    img_longitude = image_object['longitude']
    img_timestamp = image_object['timestamp']
    img_id = image_object['identifier']

    event_object = None

    matching_events = db.events.find()
    for event in matching_events:
        event_images = event['images']
        for event_image_id in event_images:
            event_image = images.find_one({'identifier': event_image_id})

            if within_distance((img_latitude, img_longitude), (event_image['latitude'], event_image['longitude']),
                               int(img_timestamp), int(event_image['timestamp'])):
                if len(event_images) == 1:
                    last_image = images.find_one(
                        {'identifier': event_images[0]})
                    last_owner = users.find_one({'_id': last_image['user_id']})
                    last_owner['owed_images'].append(last_image['identifier'])
                    users.update_one({'_id': last_owner['_id']}, {
                                     '$set': last_owner}, upsert=True)

                if img_id not in event_images:
                    event_images.append(img_id)

                img_user = users.find_one({'_id': image_object['user_id']})
                if img_id not in img_user['owed_images']:
                    img_user['owed_images'].append(img_id)
                    users.update_one({'_id': img_user['_id']}, {
                                     '$set': img_user}, upsert=True)

                event_object = event
                break

        if event_object:
            break

    if not event_object:
        g = get_location_title(img_latitude, img_longitude)
        event_object = {
            '_id': getNextId('eventid'),
            'images': [img_id],
            'title': g.city,
            'created_at': time.time()
        }

    events.update_one({'_id': event_object['_id']}, {
                      '$set': event_object}, upsert=True)

    return event_object


def within_distance(loc1, loc2, timestamp1, timestamp2):
    lat1, lon1 = float(loc1[0]), float(loc1[1])
    lat2, lon2 = float(loc2[0]), float(loc2[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    d = 3961 * c

    time1 = datetime.datetime.fromtimestamp(timestamp1)
    time2 = datetime.datetime.fromtimestamp(timestamp2)
    time_delta = time1 - time2
    t = abs(time_delta.seconds) / 60
    print t

    return d <= .2 and t <= 120


def get_location_title(lat, lon):
    try:
        location = geocoder.google([lat, lon], method='reverse')
    except Exception as e:
        print str(e)

    if not location:
        location = "Near ({}, {})".format(lat, lon)

    return location


def sanitize_string(data):
    return data.strip().replace('-', '').replace('(', '').replace(')', '')

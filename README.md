# ![Photon](http://i.imgur.com/iHp9j1V.png)

## What is Photon?
Photon automatically takes photos from your camera roll and intelligently shares the right photos with the right. We use geotagging, time, and contacts to seamlessly create photostreams of your group's photos. Only direct friends with contacts get access, because we understand the importance of privacy.

By using photo metadata to determine which images should be uploaded, Photon is quick, efficient, and hassle-free. The goal is for Photon to be out of the way, automatically syncing photos taken during group trips without any user action. Photon works with your favorite photo app, so you don't have to change a thing.

## Inspiration
Sharing photos is a pain in the ass. You shouldn't have to scroll through a list and hand pick the relavent images to share with the right contacts. You shouldn't have to upload every image to figure out which ones belong to an event. All you should have to do is take a picture. 

## Nerd Stuff
Photon's backend is built on a Python stack using Flask and MongoDB. The datbase is hosted on MLab. The iOS client is built on Swift and Objective-C.

### Building
Create a `secrets.py` file in the root directory with the following MLab database user credentials:

```Python
MLAB_USER = <DATA_BASE_USER>
MLAB_PW = <DATA_BASE_USER_PASSWORD>
```
---
##### Photon was originally develped by the [MHacks](https://github.com/mhacks) team at [a16z's](http://a16z.com/) [Battle of the Hacks 3.0](http://battleofthehacks3.devpost.com/). 

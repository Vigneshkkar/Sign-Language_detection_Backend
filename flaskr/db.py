from flask import current_app, g
from werkzeug.local import LocalProxy
from flask_pymongo import PyMongo
import datetime


def get_db():
    """
    Configuration method to return db instance
    """
    db = getattr(g, "_database", None)

    if db is None:

        db = g._database = PyMongo(current_app).db
       
    return db


# Use LocalProxy to read the global db instance with just `db`
db = LocalProxy(get_db)

def get_all_records():
    return db.words.find()
#     return db.words.aggregate([
#     # {
#     #     "$unwind": "$videos"
#     #     },
#    {
#       "$lookup":
#          {
#             "from": "PoseValues",
#             "localField": "word",
#             "foreignField": "word",
#             "as": "all_vids"
#         }
#    }
#     ])

def save_documents(word, data):
    try:
        # db.PoseValues.update_one({"word": word}, {"$push": {"data": data}}, upsert=True)
        formatted = [{"word":word, "data": row} for row in data]
        result = db.PoseValues.insert_many(formatted)
        # print(result.inserted_ids)
        db.words.update_one({"word": word}, {"$push": {"videos": result.inserted_ids}}, upsert=True)
    except Exception as e:
        print(e)
        return False
        
    return True

def get_words_count():
    return db.PoseValues.aggregate([
    {"$group" : {"_id":"$word", "count":{"$sum":1}}}
])
from flask_restful import reqparse
from pymongo.mongo_client import MongoClient
import db_secret

client = MongoClient(
    "mongodb+srv://" + db_secret.secret_id + ":"
    + db_secret.secret_key +
    "@cluster0.6se1s.mongodb.net/myFirstDatabase?" +
    "retryWrites=true&w=majority"
    )
db = client['kirjasto-backend']
collection = db['comments']


def get_comments():
    retrieved = list(collection.find({}, {'_id': False}))
    return retrieved, 200


def get_comments_by_book_id(book_id):

    correct_book_id = True
    numbers = "0123456789"

    for letter in book_id:
        if letter not in numbers:
            correct_book_id = False
    if correct_book_id:
        retrieved_ID = list(
            collection.find({'Book_ID': book_id}, {'_id': False})
            )
        return retrieved_ID, 200
    return (
        'error: Not a valid Book ID !' +
        'Book ID must be an int and the book must exist!',
        400
        )


def post_comment(user_id, comment, book_id, comment_id):

    collection.insert_one({
        'User_ID': user_id,
        'Comment': comment,
        'Book_ID': book_id,
        'Comment_ID': comment_id
    })


def delete_comments_by_id(comment_id):
    """Function that deletes comment by comment id."""

    correct_book_id = True
    numbers = "0123456789"

    for letter in comment_id:
        if letter not in numbers:
            correct_book_id = False
    if correct_book_id:
        parser = reqparse.RequestParser()
        parser.add_argument('comment_id', required=False)
        parser.add_argument('comment', required=False)
        parser.add_argument('book_id', required=False)
        parser.add_argument('user_id', required=False)

        args = parser.parse_args()
        retrieved_ID = list(
            collection.find(
                {'Comment_ID': comment_id},
                {'_id': False}
                )
            )

        for data in retrieved_ID:
            if data["Comment_ID"] == comment_id:
                collection.find_one_and_delete(
                    {"Comment_ID": comment_id},
                    {
                        'User_ID': args['user_id'],
                        'Comment': args['comment'],
                        'Book_ID': args['book_id'],
                        'Comment_ID': args['comment_id']
                        }
                        )

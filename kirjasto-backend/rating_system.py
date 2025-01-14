"""rating_system.py: Contains Rating class."""

from pymongo.mongo_client import MongoClient
import db_secret
from tests import is_rating_acceptable, is_book_id_inside_book_collection, is_user_name_inside_user_collection, is_object_int

client = MongoClient(
    "mongodb+srv://" + db_secret.secret_id + ":"
    + db_secret.secret_key +
    "@cluster0.6se1s.mongodb.net/myFirstDatabase?" +
    "retryWrites=true&w=majority"
    )
db = client['kirjasto-backend']
book_collection = db['books']
user_collection = db['users']
rating_collection = db['ratings']
retrieved_book_collection = list(book_collection.find({}, {'_id': False}))
retrieved_user_collection = list(user_collection.find({}, {'_id': False}))
retrieved_rating_collection = list(rating_collection.find({}, {'_id': False}))


class RatingSystem:
    """
    Class that contain functions
    that are necessary to make rating system work as intended.
    """

    def __init__(self):
        self.books = retrieved_book_collection
        self.users = retrieved_user_collection
        self.user_ratings = retrieved_rating_collection

#Needed?
    def get_retrieved_book_collection(self):
        """
        Function that returns a dictionary called self.books
        that contains retrieved book collection.
        """

        return self.books

    def get_retrieved_book_by_id(self, book_id):
        """
        Function that returns book from the database
        depending on the id.
        """

        
        retrieved = list(
            book_collection.find({'Book_ID': int(book_id)}, {'_id': False})
            )
        return retrieved
       

    def get_retrieved_user_collection(self):
        """
        Function that returns a dictionary called self.users
        that contains retrieved user collection.
        """

        return self.users

    def get_retrieved_user_by_username(self, user_name):
        """
        Function that returns user data from the database
        depending on the username.
        """
        retrieved = list(
            user_collection.find({'Username': user_name}, {'_id': False})
            )

        if len(retrieved) > 0:
            return retrieved
          

    def get_retrieved_rating_collection(self):
        """
        Function that returns a dictionary called self.user_ratings
        that contains retrieved rating collection.
        """

        return self.user_ratings

    def get_retrieved_ratings_by_username(self, user_name):
        """Function that returns all of user's ratings."""

        correct_user_name = False

        for rating in retrieved_rating_collection:
            if rating["Username"] == user_name:
                correct_user_name = True
        if correct_user_name:
            retrieved = list(
                rating_collection.find(
                    {'Username': str(user_name)}, {'_id': False}
                    )
                )
            if len(retrieved) > 0:
                return retrieved
        

    def get_retrieved_rating_by_username_and_id(self, user_name, book_id):
        """Function that returns user's ratings on a book."""

        correct_id = True
        correct_username = False
        numbers = "0123456789"

        for letter in book_id:
            if letter not in numbers:
                correct_id = False
        for rating in retrieved_rating_collection:
            if rating["Username"] == user_name:
                correct_username = True
        if correct_id and correct_username:
            retrieved = list(
                rating_collection.find(
                    {
                        'Username': user_name,
                        'Book_ID': int(book_id)
                        }, {'_id': False}
                    )
                )
            return retrieved

    def has_the_user_already_rated_this_book(self, user_name, book_id):
        """Function that checks whether a user has already rated the book."""

        for rating in self.user_ratings:
            if rating["Username"] == user_name and \
                    rating["Book_ID"] == book_id:
                return True
        return False

    # Everytime a rating is replaced also the ObjectID is replaced
    # Maybe not a problem but good to know
    # Therefore when the rating is added to the dictionary
    # it doesn't have ObjectID so the question is:
    # should the rating be stored in the dictionary from database?

    def replace_user_rating(self, user_name, book_id, new_rating):
        """Function that replaces old rating with a new one."""

        for rating in self.user_ratings:
            if rating["Username"] == user_name and \
                    rating["Book_ID"] == int(book_id):
                rating["Rating"] = int(new_rating)

    # replace doesn't work
    def give_rating(self, user_name, book_id, rating):
        """
        Function that saves user's rating,
        user id, rated book's id and rating
        to a list called self.user_ratings.
        """

        if is_rating_acceptable(rating) is False or is_user_name_inside_user_collection(user_name) is False or is_book_id_inside_book_collection(book_id) is False or is_object_int(rating):
            return "Something went wrong."

        new_rating = {
            "Username": user_name,
            "Book_ID": int(book_id),
            "Rating": int(rating)
            }

        if self.has_the_user_already_rated_this_book(user_name, book_id):
            rating_collection.replace_one(
                self.get_reimbursable_user_rating(new_rating),
                new_rating
                )
            self.replace_user_rating(user_name, book_id, new_rating)
        else:
            self.user_ratings.append(new_rating)
            rating_collection.insert_one(new_rating)

        self.update_books_dictionary_ratings()

        for book in self.books:
            book_collection.replace_one(self.get_reimbursable_book(book), book)

        self.update_users_dictionary_rating()

        for user in self.users:
            book_collection.replace_one(self.get_reimbursable_user(user), user)

    def delete_rating(self, user_name: int, book_id):
        """Function that deletes a rating and updates data after."""

        for rating in self.user_ratings:
            if rating["Username"] == user_name and \
                    rating["Book_ID"] == book_id:
                rating_collection.remove(rating)
                self.user_ratings.remove(rating)

        # Needs to be updated some other way
        # since now Object_id will be added aswell
        self.update_books_dictionary_ratings()
        self.update_users_dictionary_rating()

    def get_books_rating_data(self, book_id):
        """
        Function that returns single books rating
        and the amount that the book has been rated.
        """

        count = 0
        rating_sum = 0
        for rating in self.user_ratings:
            if rating["Book_ID"] == int(book_id):
                count += 1
                rating_sum += rating["Rating"]
        if rating_sum == 0:
            return (0, 0)
        else:
            return (rating_sum / count, count)

    def get_users_mean_score(self, user_name):
        """
        Function that returns single user's mean score
        and the amount that the user has rated books.
        """

        count = 0
        rating_sum = 0
        for rating in self.user_ratings:
            if rating["Username"] == user_name:
                if rating["Username"]:
                    count += 1
                    rating_sum += int(rating["Rating"])
        if rating_sum == 0:
            return (0, 0)
        else:
            return (rating_sum / count, count)

    def update_books_dictionary_ratings(self):
        """Function that updates ratings in the dictionary called books."""

        for rating in self.books:
            book_id = rating["Book_ID"]
            rating["Rating"] = (
                f"{self.get_books_rating_data(book_id)[0]} "
                f"out of 5 ({self.get_books_rating_data(book_id)[1]} "
                f"ratings)"
                )

    def update_users_dictionary_rating(self):
        """Function that updates mean score in the dictionary called users."""

        for score in self.books:
            user_name = score["Book_ID"]
            score["Mean_score"] = (
                f"{self.get_users_mean_score(user_name)[0]} "
                f"out of 5 ({self.get_users_mean_score(user_name)[1]} "
                f"ratings)"
                )

    def get_reimbursable_book(self, book):
        """
        Function that returns book
        that was originally from the books collection
        if the parameter is the new version of the old book.
        """

        for retrieved_book in retrieved_book_collection:
            if retrieved_book["Book_ID"] == book["Book_ID"]:
                return retrieved_book

    def get_reimbursable_user(self, user):
        """
        Function that returns user
        that was originally from the users collection
        if the parameter is the new version of the old user.
        """

        for retrieved_user in retrieved_user_collection:
            if retrieved_user["Username"] == user["Username"]:
                return retrieved_user

    def get_reimbursable_user_rating(self, rating):
        """
        Function that returns user_rating
        that was originally from the user_ratings collection
        if the parameter is the new version of the old user_rating.
        """

        for retrieved_rating in retrieved_rating_collection:
            if retrieved_rating["Username"] == rating["Username"]:
                return retrieved_rating

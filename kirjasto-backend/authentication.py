from flask import Flask, jsonify, request, session, redirect
from passlib.hash import pbkdf2_sha256
from app import collection
import uuid

class User:

    def start_session(self, user):
        del user['password']
        session['logged_in'] = True
        session['user'] = user
        #return jsonify(user), 200
        return user, 200

    def signup(self):

        #If meanscore is needed then just add it here
        
        # Create the user object
        user = {
            "_id": uuid.uuid4().hex,
            "user_name": request.form.get('name'),
            "email": request.form.get('email'),
            "password": request.form.get('password'),
            #Changed to small letter
            "mean_score": 0
        }

        # Encrypt the password
        user['password'] = pbkdf2_sha256.encrypt(user['password'])

        # Check for existing email address
        if collection.find_one({ "email": user['email']}):
            return { "error": "Email address already in use" }, 400

        if collection.insert_one(user):
            return self.start_session(user)

        return { "error": "Signup failed"}, 400

    def signout(self):
        session.clear()
        return redirect('/')

    def login(self):

        user = collection.find_one({
            "email": request.form.get('email')
        })

        if user and pbkdf2_sha256.verify(request.form.get('password'), user['password']):
            return self.start_session(user)

        return { "error": "Invalid login credentials" }, 401
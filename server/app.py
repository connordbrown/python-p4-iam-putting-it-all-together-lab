#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        username = request.json.get('username')
        password = request.json.get('password')
        image_url = request.json.get('image_url')
        bio = request.json.get('bio')

        new_user = User(
            username=username,
            image_url=image_url,
            bio=bio
        )
        # password encrypted by setter
        new_user.password_hash = password

        try:
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            return new_user.to_dict(), 201
        except IntegrityError:
            return {'error': '422: Unprocessable Entity'}, 422

class CheckSession(Resource):
    def get(self):
        if user := User.query.filter(User.id == session.get('user_id')).first():
            return user.to_dict(), 200
        return {'error': '401: Unauthorized'}, 401

class Login(Resource):
    def post(self):
        user = User.query.filter(User.username == request.json.get('username')).first()
        if user and user.authenticate(request.json.get('password')):
            session['user_id'] = user.id
            return user.to_dict()
        return {'error': '401: Unauthorized'}, 401

class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session['user_id'] = None
            return {}, 204
        return {'error': '401: Unauthorized'}, 401

class RecipeIndex(Resource):
    def get(self):
        if session.get('user_id'):
            user = User.query.filter(User.id == session.get('user_id')).first()
            recipes = [r.to_dict() for r in user.recipes]
            return recipes, 200
        return {'error': '401: Unauthorized'}, 401
    
    def post(self):
        if session.get('user_id'):
            new_recipe = Recipe(
                title = request.json.get('title'),
                instructions = request.json.get('instructions'),
                minutes_to_complete = request.json.get('minutes_to_complete'),
                user_id = session.get('user_id')
            )
            try:
                db.session.add(new_recipe)
                db.session.commit()
                return new_recipe.to_dict(), 201
            except IntegrityError:
                return {'error': '422: Unprocessable Entity'}, 422
        return {'error': '401: Unauthorized'}, 401

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
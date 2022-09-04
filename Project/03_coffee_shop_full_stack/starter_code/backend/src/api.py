import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks", methods=['GET'])
@requires_auth('get:drinks')
def retrieve_drinks(jwt):
    try:
        drinks = Drink.query.order_by(Drink.id).all()
        drink_lists = [drink.short() for drink in drinks]

        return jsonify(
            {
                "success": True,
                "drinks": drink_lists
            }
        ), 200
    except:
        abort(404)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks-detail", methods=['GET'])
@requires_auth('get:drinks-detail')
def retrieve_drinks_detail(jwt):
    try:
        drinks = Drink.query.order_by(Drink.id).all()
        drink_lists = [drink.long() for drink in drinks]

        return jsonify(
            {
                "success": True,
                "drinks": drink_lists
            }
        )
    except:
        abort(404)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks", methods=['POST'])
@requires_auth('post:drinks')
def create_drinks(jwt):
    body = request.get_json()

    title = body.get("title")
    recipe = body.get("recipe")
    try:
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()

        # drinks = Drink.query.order_by(Drink.id).all()

        return jsonify(
            {
                "success": True,
                "drinks": [drink.long()]
            }
        ), 200

    except:
        abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks/<int:id>", methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(jwt, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    # drink.title = 'Black Coffee'
    if drink:
        try:
            body = request.get_json()

            title = body.get('title', None)
            recipe = body.get('recipe', None)

            if title:
                drink.title = title
            if recipe:
                drink.recipe = json.dumps(recipe)
            drink.update()
            return jsonify({
                'success': True,
                'drinks': [drink.long()]
            }), 200
        except:
            abort(422)
    else:
        abort(404)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks/<int:id>", methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(jwt, id):
    get_drink = Drink.query.get(id)

    if get_drink:
        try:
            get_drink.delete()

            return jsonify({
                'success': True,
                'deleted_drink': id
            }), 200

        except:
            abort(422)

    else:
        abort(404)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "server error"
    }), 500


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def auth_error(err):
    return jsonify({
        "success": False,
        "error": err.status_code,
        "message": err.error
    })

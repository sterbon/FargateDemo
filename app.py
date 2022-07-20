
import hashlib
import datetime
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
import settings as st

app = Flask(__name__)
jwt = JWTManager(app)

#App configurations 
app.config['JWT_SECRET_KEY'] = st.SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)

#Connection to MongoDB Atlas
client = MongoClient("mongodb://sterbon:{}@ac-yoynksr-shard-00-00.y34oreq.mongodb.net:27017,ac-yoynksr-shard-00-01.y34oreq.mongodb.net:27017,ac-yoynksr-shard-00-02.y34oreq.mongodb.net:27017/?ssl=true&replicaSet=atlas-ny5zcp-shard-0&authSource=admin&retryWrites=true&w=majority".format(st.DATABASE_PASSWORD))
db = client.test
db = client["demo"]
users_collection = db["users"]

@app.route("/api/v1/health", methods=["GET"])
def health():
	return jsonify({'msg': 'Service healthy'}), 200

@app.route("/api/v1/users", methods=["POST"])
def register():
	'''
	POST Endpoint for registering a new user to the database using username and password
	'''
	try:
		new_user = request.get_json()
		new_user["password"] = hashlib.sha256(new_user["password"].encode("utf-8")).hexdigest() # encrpt password
		doc = users_collection.find_one({"username": new_user["username"]}) # check if user exist
		if not doc:
			users_collection.insert_one(new_user)
			return jsonify({'msg': 'User created successfully'}), 201
		else:
			return jsonify({'msg': 'Username already exists'}), 409

	except Exception:
		return jsonify({'msg': 'Unable to process request'}), 500

@app.route("/api/v1/login", methods=["POST"])
def login():
	'''
	POST Endpoint for loging in the user using password based authentication, stored in the database. 
	Thereafter rerturning JWT access token for further queries
	'''
	try:
		login_details = request.get_json() # store the json body request
		user_from_db = users_collection.find_one({'username': login_details['username']})  # search for user in database

		if user_from_db:
			encrpted_password = hashlib.sha256(login_details['password'].encode("utf-8")).hexdigest()
			if encrpted_password == user_from_db['password']:
				access_token = create_access_token(identity=user_from_db['username']) # create jwt token
				return jsonify( access_token=access_token), 200

		return jsonify({'msg': 'The username or password is incorrect'}), 401

	except Exception:
		return jsonify({'msg': 'Unable to process request'}), 500

@app.route("/api/v1/user", methods=["GET"])
@jwt_required()
def profile():
	'''
	GET Endpoint for getting data of logged in user
	'''
	try:
		current_user = get_jwt_identity() # Get the identity of the current user
		user_from_db = users_collection.find_one({'username' : current_user})
		if user_from_db:
			del user_from_db['_id'], user_from_db['password'] # delete data we don't want to return
			return jsonify({'profile' : user_from_db }), 200
		else:
			return jsonify({'msg': 'Profile not found'}), 404

	except Exception:
		return jsonify({'msg': 'Unable to process request'}), 500

if __name__ == '__main__':
	app.run(debug=True)
from Flask import * 
from flask-restful import *
from pymongo import *
import bcrypt
import spacy 


app = Flask(__name__)
api = Api(app)

client = MongoClient("mongo://27017")

db = client.SimilarityDB
users = db["Users"]

def UserExist(username):
    if users.find({"Username":username}).count() == 0:
        return False
    else:
        return True


class Register(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]
        if UserExist(username):
            return  jsonify({
                "Message": "Invalid Username",
                "status" : 301
            })
        
        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        users.insert({
            "Username": username,
            "Password"; password,
            "Token": 6
        })

        return jsonify({
            "Message": "Successfully signed up",
            "status" : 200
        })

class Detect(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]

        text1 = postedData['text1']
        text2 = postedData['text2']

        if not UserExist(username):
            return jsonify({
                "status": 301,
                "message": "user does not exit"
            })


api.add_resource(Register,'/registers')

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
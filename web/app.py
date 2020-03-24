from flask import * 
from flask_restful import *
from pymongo import *
import bcrypt
import spacy 


app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")

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
            "Password": hashed_pw,
            "Token": 6
        })

        return jsonify({
            "Message": "Successfully signed up",
            "status" : 200
        })


def verifyPw(username,password):
    if not UserExist(username):
        return False
    hashed_pw = users.find({"Username":username})[0]['Password']

    if bcrypt.hashpw(password.encode('utf8'),hashed_pw) == hashed_pw:
        return True
    else:
        return False


def countToken(username):
    return users.find({
        "Username":username
    })[0]["Token"]

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
        correct_pw = verifyPw(username,password)

        if not correct_pw:
            return jsonify({
                "Status": 302,
                "message": "Invalid password" 
            })
        num_tokens = countToken(username)
        if num_tokens<=0:
            return jsonify({
                "status": 303,
                "message": "Not enough token"
            })

        # now checking similarity
        nlp = spacy.load("en_core_web_sm")
        
        text1  = nlp(text1)
        text2  = nlp(text2)

        # ratio 0 to 1 to check the similarity
        ratio = text1.similarity(text2)

        current_token = countToken(username)

        users.update({
            "Username":username
        },{
            "$set":{
                "Token":current_token-1
            }
        })
        return jsonify({
            "status": 200,
            "Similarity ratio": ratio,
            "message": "Similarity score"
        })



class Refill(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["admin_pass"]

        refill = postedData["refill"]


        if not UserExist(username):
            return jsonify({
                "status": 301,
                "message": "user does not exit"
            })
        correct_pw = 'abc123'

        if  not correct_pw == password:
            return jsonify({
                "Status": 304,
                "message": "Invalid Admin password" 
            })
        current_token = countToken(username)

        users.update({
            "Username":username
        },{
            "$set":{
                "Token":current_token+refill
            }
        })

        return jsonify({
            "status":200,
            "message":"Refill Successfully"
        })
        

api.add_resource(Register,'/registers')
api.add_resource(Detect,'/detect')
api.add_resource(Refill,'/refill')

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
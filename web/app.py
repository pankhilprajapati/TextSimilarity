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
            retJson = {
                "Message": "Invalid Username",
                "status" : 301
            }
            return  jsonify(retJson)
        
        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        users.insert({
            "Username": username,
            "Password"; password,
            "Token": 6
        })
        
        retJson = {
            "Message": "Successfully signed up",
            "status" : 200
        }
        return jsonify(retJson)


api.add_resource(Register,'/registers')

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
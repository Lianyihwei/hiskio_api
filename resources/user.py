from flask_restful import Resource, reqparse
import pymysql
from flask import jsonify, make_response
import traceback
from server import db
from models import UserModel
from dotenv import load_dotenv
import os
load_dotenv()

parser = reqparse.RequestParser()
parser.add_argument("name")
parser.add_argument("gender")
parser.add_argument("birth")
parser.add_argument("note")

#註解掉的部份是使用非sqlalchemy方式對資料庫進行CRUD功能

class User(Resource):
    def db_init(self):
        db = pymysql.connect(os.getenv("DB_HOST"),os.getenv("DB_USER"),os.getenv("DB_PASSWORD"),os.getenv("DB_SCHEMA"))
        cursor = db.cursor(pymysql.cursors.DictCursor)
        return db, cursor
    
    def get(self, id):
        db, cursor = self.db_init()
        sql = "Select * From api.users Where id = '{}' and deleted is not True".format(id)
        cursor.execute(sql)
        db.commit()
        user = cursor.fetchone()
        db.close()

        return jsonify({"data": user})

    def patch(self, id):
        # db, cursor = self.db_init()
        arg = parser.parse_args()
        # user = {
        #     "name": arg["name"],
        #     "gender": arg["gender"],
        #     "birth": arg["birth"],
        #     "note": arg["note"],
        # }
        # query = []
        # for key, value in user.items():
        #     if value != None:
        #         query.append(key + "=" + "'{}'".format(value))
        # query = ",".join(query)
        # sql = """
        #     UPDATE `api`.`users` SET {} WHERE (`id` = '{}');
        #     """.format(query, id)
        user = UserModel.query.filter_by(id=id, deleted=None).first()
        if arg["name"] != None:
            user.name = arg["name"]

        response = {}
        try:
            # cursor.execute(sql)
            db.session.commit()
            response["msg"] = "success"
        except:
            traceback.print_exc()
            response["msg"] = "failed"
        # db.commit()
        # db.close()
        return jsonify(response)

    def delete(self, id):
        # db, cursor = self.db_init()
        # sql = """
        #     UPDATE `api`.`users` SET deleted = True WHERE (`id` = '{}');
        # """.format(id)
        user = UserModel.query.filter_by(id=id, deleted=None).first()

        response = {}
        try:
            # cursor.execute(sql)
            db.session.delete(user)
            db.session.commit()
            response["msg"] = "success"
        except:
            traceback.print_exc()
            response["msg"] = "failed"
        
        # db.commit()
        # db.close()
        return jsonify(response)

class Users(Resource):
    def db_init(self):
        db = pymysql.connect("localhost", "root", "passWord854", "api")
        cursor = db.cursor(pymysql.cursors.DictCursor)
        return db, cursor
    def get(self):
        # 下面這段是一般連結sql的restful方式語法
        # db, cursor = self.db_init()
        # arg = parser.parse_args()
        # sql = 'Select * From api.users where deleted is not True'
        # if arg["gender"] != None:
        #     sql += ' and gender = "{}"'.format(arg['gender'])
        # cursor.execute(sql)
        # db.commit()
        # users = cursor.fetchall()
        # db.close()

        # 這一段開始是使用SQLAlchemy方式連結sql的語法
        users = UserModel.query.filter(UserModel.deleted.isnot(True)).all()
        return jsonify({'data': list(map(lambda user: user.serialize(), users))})
    
    def post(self):
        # db, cursor = self.db_init()
        arg = parser.parse_args()
        user = {
            "name": arg["name"],
            "gender": arg["gender"] ,
            "birth": arg["birth"] ,
            "note": arg["note"],
        }
        # sql = """
        #     INSERT INTO `api`.`users` (`name`, `gender`, `birth`,`note`) VALUES ('{}', '{}', '{}','{}');
        # """.format(user["name"], user["gender"], user["birth"], user["note"])

        response = {}
        status_code = 200
        try:
            # cursor.execute(sql)
            new_user = UserModel(name=user["name"], gender=user["gender"], birth=user["birth"], note=user["note"])
            db.session.add(new_user)
            db.session.commit()
            response["msg"] = "success"
        except:
            status_code = 400
            traceback.print_exc()
            response["msg"] = "failed"
        
        # db.commit()
        # db.close()
        return make_response(jsonify(response), status_code)
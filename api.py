from flask import Flask, request
from flask_restful import Resource, Api
import requests
import scanner

# make var image names
# image = 'examples/mm.png'
# answer, gray = scanner.process(image)
# print(answer)
# scanner.imshow()
app = Flask(__name__)
api = Api(app)

# save uploaded img in s3 -> in rails?
# call scanner.process on saved img 
# return grading to rails app

# todos = {}

# class TodoSimple(Resource):
# 	def get(self, todo_id):
# 		return {todo_id : todos[todo_id]}

# 	def put(self, todo_id):
# 		todos[todo_id] = request.form['data']
# 		return {todo_id: todos[todo_id]}

class GradeImage(Resource):
	methods = ["POST"]
	def post(stringy):
		result, _ = scanner.process(image_path)
		return stringy # flask.jsonify(**result)

api.add_resource(GradeImage, '/<string:stringy>')

if __name__ == '__main__':
	app.run(debug=True)

# import code; code.interact(local=dict(globals(), **locals()))	
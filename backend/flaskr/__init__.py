import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

import sys
#sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


#from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

####start of models ###
import os
from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy
import json

database_name = "trivia"
database_path = 'postgres://zruxi@localhost:5432/' + database_name

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    #db = SQLAlchemy(app)
    db.init_app(app)
    db.create_all()

'''
Question

'''
class Question(db.Model):
  __tablename__ = 'questions'

  id = Column(Integer, primary_key=True)
  question = Column(String)
  answer = Column(String)
  category = Column(String)
  difficulty = Column(Integer)

  def __init__(self, question, answer, category, difficulty):
    self.question = question
    self.answer = answer
    self.category = category
    self.difficulty = difficulty

  def insert(self):
    db.session.add(self)
    db.session.commit()

  def update(self):
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  def format(self):
    return {
      'id': self.id,
      'question': self.question,
      'answer': self.answer,
      'category': self.category,
      'difficulty': self.difficulty
    }

'''
Category

'''
class Category(db.Model):
  __tablename__ = 'categories'

  id = Column(Integer, primary_key=True)
  type = Column(String)

  def __init__(self, type):
    self.type = type

  def format(self):
    return {
      'id': self.id,
      'type': self.type
    }

####end of models ###

def paginate(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def formatt(data):
    # format the data
    data = [datum.format() for datum in data]

    return data


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    setup_db(app)

    '''
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, PUT, POST, DELETE, OPTIONS')
        #response.headers.add('Access-Control-Allow-Origin', '*')
        return response


    '''
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    '''
    @app.route('/api/categories')
    def retrieve_categories():
        all_categories = Category.query.order_by(Category.id).all()
        if len(all_categories) == 0:
            abort(404)
        try:
            categories = paginate(request, categories)
            categories = formatt(categories)
            return jsonify({
                'success': True,
                'categories': categories
            }), 200
        except:
            abort(400)


    '''
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
    '''
    @app.route('/api/questions')
    def retrieve_questions():
        categories = Category.query.order_by(Category.id).all()
        questions = Question.query.all()

        if len(questions) == 0:
            abort(404)
        elif len(categories) == 0:
            abort(404)

        try:
            questions = formatt(questions)
            data = paginate(request, questions)

            if len(questions) < 1:
                abort(404)
            else:
                return jsonify({
                    'count': len(questions),
                    'questions': data,
                    'categories': formatt(categories),
                    'success': True
                }), 200
        except:
            abort(400)

    '''
    @TODO:
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    '''


    '''
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    '''
    @app.route('/api/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.filter(
            Question.id == question_id).one_or_none()
        if question is None:
            abort(404)

        try:
            question.delete()
            categories = Category.query.order_by(Category.id).all()
            questions = Question.query.all()
            questions = formatt(questions)
            questions = paginate(request, questions)

            return jsonify({
                'count': len(questions),
                'questions': questions,
                'categories': formatt(categories),
                'success': True
            })
        except:
            abort(400)

    '''TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    '''

    '''
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.
    '''
    @app.route('/api/questions', methods=['POST'])
    def post_question():
        error = False
        # Declare and empty data dictionary to hold all retrieved variables
        data = request.get_json()

        # set question variable equal to corresponding model class,
        # ready for adding to the session
        question = Question(
            question=data.get('question', None),
            answer=data.get('answer', None),
            difficulty=data.get('difficulty', None),
            category=data.get('category', None)
        )

        if not question.question:
            abort(404)

        try:
            db.session.add(question)
            # commit final changes and flash newly added venue on success
            db.session.commit()
        except:
            error = True
            # log error message to the console for easy debbugging
            print(sys.exc_info())
            abort(400)

        categories = Category.query.order_by(Category.id).all()
        questions = Question.query.all()
        questions = formatt(questions)
        questions = paginate(request, questions)

        return jsonify({
            'count': len(questions),
            'questions': questions,
            'categories': formatt(categories),
            'success': True
        }), 200


    '''
    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    '''

    '''
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.
    '''
    @app.route('/api/questions/search', methods=['POST'])
    def search_question():
        try:
            # get the search term
            term = request.get_json().get('searchTerm', None)

            # query the database for like results and send the response
            questions = Question.query.filter(
                Question.question.like('%'+term+'%')).all()
            questions = formatt(questions)

            if(questions is None):
                abort(404)

            return jsonify({
                'total_questions': len(questions),
                'questions': questions,
                'success': True
            }), 200
        except:
            abort(400)

    '''
    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    '''

    '''
    @TODO:
    Create a GET endpoint to get questions based on category.
    '''
    @app.route('/api/categories/<int:category_id>/questions', methods=['GET'])
    def search_questions_by_category(category_id):
        questions = Question.query.filter_by(category=category_id).all()
        try:
            # query the database for like results and send the response
            questions = formatt(questions)
            questions = paginate(request, questions)

            if len(questions) == 0:
                abort(404)

            return jsonify({
                'total_questions': len(questions),
                'questions': questions,
                'success': True
            }), 200
        except:
            abort(400)

    '''
    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''


    '''
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.
    '''
    @app.route('/api/quizzes', methods=['POST'])
    def random_questions():
        previous_questions = request.get_json().get('previous_questions')
        quiz_category = request.get_json().get('quiz_category')

        try:
            if(quiz_category['id'] == 0):
                questions_by_category = Question.query.all()
            else:
                questions_by_category = Question.query.filter_by(
                    category=quiz_category['type']['id']).all()

            # Inspired by Okebunmi Odunayo
            # https://github.com/OdunayoOkebunmi/Trivia/blob/develop/backend/flaskr/__init__.py#L159
            random_num = random.randint(0, len(questions_by_category)-1)
            question = questions_by_category[random_num]

            selected = False
            count = 0

            while selected is False:
                if(question.id in previous_questions):
                    random_num = random.randint(
                        0, len(questions_by_category)-1)
                    question = questions_by_category[random_num]
                else:
                    selected = True
                # if count == len(questions_by_category):
            count += 1
            question = question.format()

            return jsonify({
                'success': True,
                'question': question
            }), 200
        except:
            abort(422)
    '''
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    '''

    '''
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    return app

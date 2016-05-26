from flask import Flask
from flask import request
from algo import answer_question

application = Flask(__name__)

@application.route('/', methods=['GET'])
def question_bot():
    try:
        print request.args
        question = request.args.get('question')
        if question:
            return answer_question(question)
        else:
            return "Hi, I'm Max Verstappen. Do you have a question for me?"
    except:
        return "Hi, I'm Max Verstappen. Do you have a question for me?"

if __name__ == '__main__':
    application.run()
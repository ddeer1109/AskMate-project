import csv
import os
import pathlib


QUESTIONS_DATA_FILE_PATH = os.getenv('DATA_FILE_PATH') if 'DATA_FILE_PATH' in os.environ else f"{pathlib.Path(__file__).parent.absolute()}/sample_data/question.csv"
ANSWER_DATA_FILE_PATH = os.getenv('DATA_FILE_PATH') if 'DATA_FILE_PATH' in os.environ else f"{pathlib.Path(__file__).parent.absolute()}/sample_data/answer.csv"
QUESTIONS_DATA_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
ANSWERS_DATA_HEADER = ['id', 'submission_time', 'vote_number', 'message', 'image']
ANSWERS_DATA_HEADER_FILE = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']

def save_all_questions(question):
    # def save_user_story(story):
    #     with open(DATA_FILE_PATH, 'a', newline='') as csv_file:
    #         csv_writer = csv.DictWriter(csv_file, fieldnames=DATA_HEADER, delimiter=',', quotechar='|')
    #         csv_writer.writerow(story)
    with open(QUESTIONS_DATA_FILE_PATH, 'a', newline='') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=QUESTIONS_DATA_HEADER, delimiter=',', quotechar='"')
        csv_writer.writerow(question)

def get_all_questions():
    questions = []

    with open(QUESTIONS_DATA_FILE_PATH) as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',', quotechar='"')
        for row in csv_reader:
            questions.append(row)

        return questions


def get_all_answers():
    answers = []

    with open(ANSWER_DATA_FILE_PATH) as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',', quotechar='"')
        for row in csv_reader:
            answers.append(row)

        return answers

def get_data(PATH, FILENAME, data):
    with open(PATH + '/sample_data/' + FILENAME, 'r') as csv_file:
            data = csv.reader(csv_file)
            rows = list(data)
    return rows

# def add_data(PATH, FILENAME, data):
#     with open(PATH + '/sample_data/' + FILENAME, 'a', newline='') as csv_file:
#         writer = csv.DictWriter(csv_file, fieldnames=ANSWERS_DATA_HEADER, delimiter=',', quotechar='"')
#         writer.writerow(data)
#     # print(PATH, FILENAME, data)


def save_all_answers(answer):
    with open(ANSWER_DATA_FILE_PATH, 'a', newline='') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=ANSWERS_DATA_HEADER_FILE, delimiter=',', quotechar='"')
        csv_writer.writerow(answer)
from datetime import datetime
import time
from data_handler import get_all_questions, get_all_answers


def get_formatted_headers(headers):
    return [header.replace("_", " ").capitalize() for header in headers]


def sort_data_by_time(entries_list):
    new_list = sorted(entries_list, key=lambda k: k['submission_time'])

    return [convert_timestamp(entry) for entry in new_list]

def sort_data_by_sorting_key(entries_list, sorting_key):
    sorting_key = dict(sorting_key)

    order_by = sorting_key['order_by']
    order_direction = sorting_key['order_direction']
    print(order_by)
    print(order_direction)


    new_list = sorted(entries_list, key=lambda k: k[sorting_key['order_by']])
    return [convert_timestamp(entry) for entry in new_list]


def convert_timestamp(entry):

    time_stamp = int(entry["submission_time"])
    dt_object = datetime.fromtimestamp(time_stamp)
    entry["submission_time"] = dt_object

    return entry


def get_question_by_id(question_id):

    questions = get_all_questions()

    for question in questions:
        if question["id"] == question_id:
            return convert_timestamp(question)


def get_answers_for_question(question_id):
    answers = get_all_answers()

    question_answers = []

    for answer in answers:
        if answer["question_id"] == question_id:
            question_answers.append(convert_timestamp(answer))

    return question_answers


def filter_data(dict_data, headers):
    filtered_data = []

    for entry in dict_data:
        filtered_entry = {}
        for header in headers:
            filtered_entry[header] = entry[header]
        filtered_data.append(filtered_entry)

    return filtered_data

def get_next_id():
    questions = get_all_questions();
    next_id = 0
    for question in questions:
        question_id = int(question['id'])
        if question_id >= next_id:
            next_id = question_id

    return next_id + 1


def get_next_answer_id():
    answers = get_all_answers()
    next_id = 0
    for answer in answers:
        answer_id = int(answer['id'])
        if answer_id >= next_id:
            next_id = answer_id
    return next_id +1

def get_current_timestamp():
    return int(time.time())

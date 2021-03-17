from flask import Flask, render_template, request, redirect, url_for, session
# from flask import flash
import data_manager, client_manager, util
from os import environ
from functools import wraps

app = Flask(__name__)
PATH = app.root_path

app.config['SECRET_KEY'] = environ.get('SECRET_KEY')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if client_manager.get_logged_user_id() is None:
            return render_template("login.html", message="You have to be logged in to perform this action.")
        return f(*args, **kwargs)
    return decorated_function


#
#          ------>> DISPLAY AND INSERTING <<------
#

@app.route("/")
def get_five_question():
    """Services redirection to main page with loaded list of the 5 latest questions."""
    questions = data_manager.get_five_questions()
    return render_template('list.html', questions=questions, sorted=False)


@app.route("/list")
def get_list_of_questions():
    """Services redirection to main page with loaded list of all questions."""
    if len(request.args) == 0:
        questions = data_manager.get_all_data()
    else:
        questions = data_manager.get_all_data_by_query(request.args.get('order_by'),
                                                       request.args.get('order_direction'))

    return render_template('list.html', questions=questions, sorted=True)


@app.route("/search")
def get_entries_by_search_phrase():
    search_phrase = request.args.get('q')

    questions, questions_with_answers = data_manager.get_entries_by_search_phrase(search_phrase)
    highlighted_questions_id = [question['id'] for question in questions_with_answers]
    return render_template("list.html",
                           searched=True,
                           questions=questions + questions_with_answers,
                           questions_id_with_highlighted_answers=highlighted_questions_id)


@app.route("/question/<question_id>")
def display_question(question_id):
    """Services redirection to specific question page."""

    data_manager.update_views_count(question_id)

    question = data_manager.get_question_by_id(question_id)
    answers = data_manager.get_answers_for_question(question_id)
    tags = data_manager.get_tags_for_question(question_id)
    comments = data_manager.get_comments_for_question(question_id)

    return render_template("question.html",
                           question=question,
                           answers=answers,
                           tags=tags,
                           comments=comments
                           )


@app.route("/add-question")
@login_required
def display_add_question():
    """Services redirection to displaying interface of adding question"""
    # if session.get('logged_user', None):
    return render_template("add_question.html")
    # else:
    #     return render_template("login.html", message="You have to be logged in to add questions or answers")



@app.route("/add-question", methods=['POST'])
@login_required
def add_question():
    """Services posting question."""
    question_id = data_manager.add_new_entry(
        table_name='question',
        form_data=request.form,
        request_files=request.files,
        user_id=client_manager.get_logged_user_id()
        )

    # data_manager.add_user_question_activity(session['user_id'], question_id)

    return redirect(url_for('display_question', question_id=question_id))


@app.route("/question/<question_id>/add-answer")
@login_required
def display_add_answer(question_id):
    """Services redirection to displaying interface of adding answer."""
    # if session.get('logged_user', None):
    return render_template("add_answer.html")
    # else:
    #     return render_template("login.html", message="You have to be logged in to add questions or answers")


@app.route("/question/<question_id>/add-answer", methods=["POST"])
@login_required
def new_answer(question_id):
    """Services posting answer."""

    answer_id = data_manager.add_new_entry(
        table_name='answer',
        form_data=request.form,
        request_files=request.files,
        question_id=question_id,
        user_id=client_manager.get_logged_user_id())

    # data_manager.add_user_answer_activity(session['user_id'], answer_id)

    return redirect(f'/question/{question_id}')


@app.route("/answer/<answer_id>/add-comment")
@login_required
def add_answer_comment(answer_id):
    return render_template('add_answer_comment.html', answer_id=answer_id)


@app.route("/answer/<answer_id>/add-comment", methods=['POST'])
@login_required
def post_answer_comment(answer_id):
    message = request.form['message']

    redirection_id = data_manager.add_comment(message, 'answer', answer_id, client_manager.get_logged_user_id())

    return redirect(url_for('display_question', question_id=redirection_id))


@app.route("/question/<question_id>/add-comment")
@login_required
def display_add_comment(question_id):
    return render_template('add_comment.html')


@app.route("/question/<question_id>/add-comment", methods=["POST"])
@login_required
def post_question_comment(question_id):
    data_manager.add_comment(request.form['message'], 'question', question_id, client_manager.get_logged_user_id())
    return redirect(f'/question/{question_id}')


@app.route("/question/<question_id>/new-tag")
@login_required
def display_new_tag(question_id):
    all_tags = data_manager.get_all_tags()
    return render_template('new_tag.html',
                           question_id=question_id,
                           all_tags=all_tags
                           )


@app.route("/question/<question_id>/new-tag", methods=['POST'])
@login_required
def add_new_tag(question_id):
    data_manager.add_new_tag_to_db(request.form['tag'])
    return redirect(url_for('display_new_tag', question_id=question_id))


@app.route("/question/<question_id>/new-tag-question", methods=['POST'])
@login_required
def add_new_tag_to_question(question_id):
    print(request.form['tag_id'])
    message = data_manager.add_new_tag_to_question(question_id, request.form['tag_id'])
    return redirect(url_for('display_question', question_id=question_id))


#
#          ------>> DELETIONS <<------
#


@app.route("/question/<question_id>/delete")
@login_required
def delete_question(question_id):
    if client_manager.get_post_if_permitted(question_id, 'question'):
        data_manager.delete_question(question_id)
        return redirect('/')
    else:
        return render_template("login.html", message="You don't have permission to perform this action")



@app.route("/question/<question_id>/tag/<tag_id>/delete")
@login_required
def delete_single_tag_from_question(question_id, tag_id):
    if client_manager.get_post_if_permitted(question_id, 'question'):
        data_manager.remove_single_tag_from_question(question_id, tag_id)
        return redirect(url_for('display_question', question_id=question_id))
    else:
        return render_template("login.html", message="You don't have permission to perform this action")



@app.route("/answer/<answer_id>/delete")
@login_required
def delete_answer(answer_id):
    """Services deleting answer."""
    if client_manager.get_post_if_permitted(answer_id, 'answer'):
        redirection_id = data_manager.delete_answer_by_id(answer_id)
        return redirect(url_for('display_question', question_id=redirection_id))
    else:
        return render_template("login.html", message="You don't have permission to perform this action")


@app.route("/comment/<comment_id>/delete")
@login_required
def delete_comment(comment_id):
    if client_manager.get_post_if_permitted(comment_id, 'comment'):
        redirection_id = data_manager.delete_comment_by_id(comment_id)
        return redirect(url_for('display_question', question_id=redirection_id))
    else:
        return render_template("login.html", message="You don't have permission to perform this action")

#
#          ------>> EDITIONS <<------
#


@app.route("/question/<question_id>/edit")
@login_required
def edit_question(question_id):
    """Services displaying edition of question and posting edited version."""
    if client_manager.get_post_if_permitted(question_id, 'question'):
        question = data_manager.get_single_question(question_id)
        return render_template('edit_question.html', question_id=question_id, question=question)
    else:
        return render_template("login.html", message="You don't have permission to perform this action")


@app.route("/question/<question_id>/edit", methods=['POST'])
@login_required
def save_edited_question(question_id):
    title = request.form['title']
    message = request.form['message']

    data_manager.save_edited_question(question_id, title, message)

    return redirect(url_for('display_question', question_id=question_id))


@app.route("/answer/<answer_id>/edit")
@login_required
def display_answer_to_edit(answer_id):
    """Services displaying edition of answer and posting edited version."""
    if client_manager.get_post_if_permitted(answer_id, 'answer'):
        answer = data_manager.get_answer(answer_id)
        return render_template('edit_answer.html', answer_id=answer_id, answer=answer)
    else:
        return render_template("login.html", message="You don't have permission to perform this action")



@app.route("/answer/<answer_id>/edit", methods=['POST'])
@login_required
def save_edited_answer(answer_id):
    redirection_id = data_manager.save_edited_answer(answer_id, request.form['message'])

    return redirect(url_for('display_question', question_id=redirection_id))


@app.route("/<entry_type>/<entry_id>/<vote_value>", methods=["POST"])
@login_required
def vote_on_post(entry_id, vote_value, entry_type):
    """Services voting on questions and answers"""
    if client_manager.get_post_if_permitted(entry_id, entry_type):
        redirection_id = data_manager.vote_on_post(entry_id, vote_value, entry_type)
        return redirect(url_for('display_question', question_id=redirection_id))
    else:
        return render_template("login.html", message="You don't have permission to perform this action")


@app.route("/comment/<comment_id>/edit")
@login_required
def display_comment_edit(comment_id):
    if client_manager.get_post_if_permitted(comment_id, 'comment'):
        comment = data_manager.get_comment_by_id(comment_id)
        return render_template('edit_comment.html',
                               message=comment['message'],
                               comment_id=comment_id)
    else:
        return render_template("login.html", message="You don't have permission to perform this action")


@app.route("/comment/<comment_id>/edit", methods=["POST"])
@login_required
def edit_comment(comment_id):
    new_message = request.form['message']
    redirection_id = data_manager.update_comment(comment_id, new_message)

    return redirect(url_for('display_question', question_id=redirection_id))


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def post_login():
    login = request.form['login']
    password = request.form['password']

    if data_manager.is_authenticated(login, password):
        user = data_manager.get_users_session_data(login)
        client_manager.set_session(user['login'], user['id'])

        return redirect(url_for('get_five_question'))

    return render_template('login.html', message="Incorrect Login or Password")


@app.route('/logout')
def logout():
    client_manager.drop_session()
    return redirect(url_for('get_five_question'))


@app.route('/registration')
def display_registration():
    return render_template('registration.html')


@app.route('/registration', methods=['POST'])
def registration():
    login = request.form.get('login')
    password = request.form.get('password')

    response = data_manager.process_registration(login, password)

    if response:
        return render_template('registration.html', message=response)
    else:
        return render_template('login.html', registration_message="You've been registered")


@app.route('/users')
@login_required
def users():
    # if session.get('logged_user', None):
    users = data_manager.get_users()
    return render_template("users.html", users=users)
    # else:
    #     return render_template("login.html", message="You have to be logged in to see users")


@app.route('/user/<user_id>')
@login_required
def user_page(user_id):
    # if session.get('logged_user', None):
    user = data_manager.get_user_data(user_id)
    questions = data_manager.get_questions_of_user(user_id)
    answers = data_manager.get_answers_of_user(user_id)
    comments = data_manager.get_comments_of_user(user_id)
    return render_template("user_page.html",
                           user=user,
                           questions=questions,
                           answers=answers,
                           comments=comments)
    # else:
    #     return render_template("login.html", message="You have to be logged in to see users")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(
        host='127.0.0.1',
        port=5050,
        debug=True)


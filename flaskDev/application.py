from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, make_response
from flask_session import Session
from passlib.hash import pbkdf2_sha256 as pwd_context
from tempfile import mkdtemp
import os
import re

from helpers import *

# configure application
app = Flask(__name__)

# For testing , do this. Once testing complete , change it back to default.
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# custom filter
app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///codepanda.db")


@app.route('/')
def index():
    return render_template("login.html")


@app.route('/submission', methods=['GET', 'POST'])
@login_required
def submission():
    user_curr = db.execute("SELECT * FROM users WHERE id=:id", id=session["user_id"])
    name_curr = user_curr[0]["username"]
    if request.method == 'POST':
        fullFilename = request.form.get('filename').strip() + request.form.get('extension').strip()
        code = request.form.get('code')

        # return make_response("<h1>{}</h1><br /><h3>{}</h3>".format(fullFilename, code))
        """
            Reminder:- I will implement this later.
            Add functionality to check for the existance of a file with the
            filename the user types.
            I am not sure as yet what i wanna do when that happens but
            i am pretty sure , i need to think about that.
        """
        file = open('submissions/' + fullFilename, 'w')
        file.write(code)
        file.close()

        if request.form.get('extension') == '.py':
            os.system('./submissions/pyScript.sh ' + fullFilename)
        elif request.form.get('extension') == '.c':
            os.system('./submissions/cScript.sh ' + fullFilename)
        elif request.form.get('extension') == '.java':
            try:
                match = re.search(r'(public\s)?\s*class\s+(.+)\s*{', code)
                className = match.group(2)
            except:
                return make_response("Error occured while compiling")

            # print(className)
            os.system('./submissions/javaScript.sh ' + fullFilename + ' ' + className)
        else:
            return "The extension is not supported as yet!."

        file = open('submissions/result.txt', 'r')
        output = file.read()
        output.replace('\n', '<br />')
        file.close()

        # os.system('./submissions/cleanerScript.sh')

        return render_template("success.html", name=name_curr, result=output)

    return render_template("submission.html", name=name_curr)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return make_response("Must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return make_response("Must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return make_response("Invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # flashing Messages
        flash("Log in Successfull")

        # redirect user to home page
        return redirect(url_for('submission'))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""

    session.clear()

    if request.method == "POST":

        if not request.form.get("username"):
            return make_response("Missing Username!")

        elif not request.form.get("password"):
            return make_response("Missing Password!")

        elif not request.form.get("repassword"):
            return make_response("Missing Confirm Password!")

        elif request.form.get("password") != request.form.get("repassword"):
            return make_response("<h3>Error: Password don't match</h3>")

        hash = pwd_context.hash(request.form.get("password"))

        # Storing the user into database
        result = db.execute("INSERT INTO users (username,hash) VALUES(:username, :hash)", username=request.form.get("username"), hash=hash)

        if not result:
            return make_response("Username is already taken")

        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # logging the user in.
        session["user_id"] = rows[0]["id"]

        # flashing Messages
        flash("Registaration Successfull")

        # redirecting to index.html
        return redirect(url_for("submission"))

    else:
        return render_template("register.html")


@app.route("/changepassword", methods=["GET", "POST"])
@login_required
def changepassword():

    user_curr = db.execute("SELECT * FROM users WHERE id=:id", id=session["user_id"])
    name_curr = user_curr[0]["username"]

    if request.method == "POST":

        if not request.form.get("password"):
            return make_response("<h3>Missing Password!</h3>")

        elif not request.form.get("repassword"):
            return make_response("Missing Confirm Password!")

        elif request.form.get("password") != request.form.get("repassword"):
            return make_response("Password don't match")
        else:
            hash = pwd_context.hash(request.form.get("password"))
            db.execute("UPDATE users SET hash = :hash WHERE id = :id", hash=hash, id=session["user_id"])
            flash("Password Changed Successfully!")
            return redirect(url_for("logout"))
    else:
        return render_template("changepassword.html", name=name_curr)


if __name__ == '__main__':
    app.run(debug=True)

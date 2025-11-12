import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


def get_updated_stocks():
    stock_info = db.execute("SELECT * FROM portfolio WHERE user_id = :user_id",
                            user_id=session["user_id"])
    my_list = []
    symbols = []

    account_value = 0
    total_account_value = 0
    total_stock_value = 0

    for stock in stock_info:
        all_stocks = {
            "symbol": stock["symbol"].upper(),
            "shares": stock["shares"],
            "price": float(stock["price"]),
            "total": float(round(stock["price"] * stock["shares"], 2))
        }
        my_list.append(all_stocks)
        total_stock_value += stock["price"] * stock["shares"]
        symbols.append(stock["symbol"])

    user_cash = db.execute("SELECT cash FROM users WHERE id = :id",
                           id=session["user_id"])[0]["cash"]
    user_cash = round(user_cash, 2)

    total_account_value += round(user_cash + total_stock_value, 2)

    return my_list, user_cash, total_account_value, symbols


def get_transaction_list():

    transaction_list = db.execute(
        "SELECT * FROM transactions WHERE user_id = ?", session["user_id"])
    my_list = []

    for transaction in transaction_list:
        trans_info = {
            "symbol": transaction["symbol"].upper(),
            "shares": transaction["shares"],
            "price": transaction["price"],
            "date": transaction["date"]
        }
        my_list.append(trans_info)

    return my_list


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    try:
        stocks, user_cash, total_account_value, _ = get_updated_stocks()

        return render_template("index.html", stocks=stocks, cash=user_cash, total=total_account_value,)

    except IndexError:
        return render_template("login.html")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "POST":

        symbol = request.form.get("symbol").upper()

        if not symbol:
            return apology("No stock entered", 400)

        stock_info = lookup(symbol)

        if stock_info == None:
            return apology("Invalid Symbol", 400)

        shares = request.form.get("shares")

        if not shares:
            return apology("Missing shares", 400)

        try:
            shares = int(request.form.get("shares"))
        # If shares entered isn't a number
        except ValueError:
            return apology("Invalid Shares", 400)

        if shares < 1:
            return apology("Can't buy less than 1 share", 400)

        price = stock_info["price"]
        user_cash = db.execute("SELECT cash FROM users WHERE id = :id",
                               id=session["user_id"])[0]["cash"]

        if user_cash < (price * shares):
            return apology("Not enough cash", 400)

        db.execute("UPDATE users SET cash = cash - ? WHERE id = ?",
                   price * shares, session["user_id"])

        old_shares = db.execute(
            "SELECT shares FROM portfolio WHERE symbol = ? AND user_id = ?", symbol, session["user_id"])

        if not old_shares:
            db.execute("INSERT INTO portfolio (user_id, symbol, shares, price, total) VALUES (?, ?, ?, ?, ?)",
                       session["user_id"], symbol, shares, price, round(price * shares, 2))

        else:
            db.execute("UPDATE portfolio SET shares = shares + ?, total = total + ? WHERE symbol = ? AND user_id = ?",
                       shares, (price * shares), symbol, session["user_id"])

        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
                   session["user_id"], symbol, shares, price)

        stocks, user_cash, total_account_value, _ = get_updated_stocks()

        flash("Bought!")

        return render_template("index.html", stocks=stocks, cash=user_cash, total=total_account_value)

    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    my_list = get_transaction_list()

    return render_template("history.html", transactions=my_list)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route('/quote', methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "POST":
        stock_info = lookup(request.form.get("symbol"))

        if stock_info:
            return render_template("quote.html", stock=stock_info)

        else:
            return apology("Stock not found", 400)

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        if not request.form.get("username"):
            return apology("Must enter username", 400)

        elif not request.form.get("password"):
            return apology("Must enter password", 400)

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords don't match", 400)

        rows = db.execute(
            "SELECT id FROM users WHERE username = ?", request.form.get("username")
        )

        if rows is not None and len(rows) > 0:
            return apology("Username already exists", 400)

        hashed_password = generate_password_hash(request.form.get("password"))

        db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get(
                "username"), hashed_password
        )

        updated_rows = db.execute(
            "SELECT id FROM users WHERE username = ?", request.form.get("username")
        )

        if updated_rows is not None:
            user_id = updated_rows[0]["id"]

            session["user_id"] = user_id

            flash("Registered!")

            return redirect("/")

        return apology("something went wrong", 200)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    if request.method == "POST":

        if not request.form.get("symbol"):
            return apology("Missing symbol", 403)

        if not request.form.get("shares"):
            return apology("Missing shares", 403)

        symbol = request.form.get("symbol").upper()
        shares = int(request.form.get("shares"))

        owned_symbol = db.execute(
            "SELECT symbol FROM portfolio WHERE user_id = ? AND UPPER(symbol) = ?", session["user_id"], symbol)
        owned_shares = db.execute(
            "SELECT shares FROM portfolio WHERE user_id = ? AND UPPER(symbol) = ?", session["user_id"], symbol)

        stock_info = lookup(symbol)
        price = stock_info["price"]

        if not owned_symbol:
            return apology("Symbol not owned", 400)

        try:
            if int(request.form.get("shares")) < 1:
                return apology("Shares must be positive", 400)
        except ValueError:
            return apology("Invalid shares", 400)

        if int(request.form.get("shares")) > owned_shares[0]['shares']:
            return apology("Too many shares", 400)

        db.execute("UPDATE portfolio SET shares = shares - ? WHERE UPPER(symbol) = ? AND user_id = ?",
                   shares, symbol, session["user_id"])
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?",
                   price * shares, session["user_id"])
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
                   session["user_id"], symbol, shares * -1, price)

        owned_shares = db.execute(
            "SELECT shares FROM portfolio WHERE user_id = ? AND UPPER(symbol) = ?", session["user_id"], symbol)

        owned_shares = int(owned_shares[0]['shares'])

        if owned_shares < 1:
            db.execute("DELETE FROM portfolio WHERE user_id = ? AND UPPER(symbol) = ?",
                       session["user_id"], symbol)

        flash("Sold!")

        return redirect("/")

    else:

        _, _, _, symbols = get_updated_stocks()

        symbols = [symbol.upper() for symbol in symbols]

        return render_template("sell.html", sellable_stocks=symbols)


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change the users password"""

    if request.method == "POST":

        if not request.form.get("old_password"):
            return apology("Must enter old password", 403)

        elif not request.form.get("new_password"):
            return apology("Must enter new password", 403)

        elif request.form.get("new_password") != request.form.get("new_password_conf"):
            return apology("Passwords don't match", 403)

        elif request.form.get("new_password") == request.form.get("old_password"):
            return apology("New password can't match old password", 403)

        current_user = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

        if not check_password_hash(current_user[0]["hash"], request.form.get("old_password")):
            return apology("Old password incorrect", 403)

        updated_hash_pw = generate_password_hash(request.form.get("new_password"))

        db.execute("UPDATE users SET hash = ? WHERE id = ?", updated_hash_pw, session["user_id"])

        flash("Password changed!")

        return redirect("/")

    else:

        return render_template("password.html")

from flask import Flask, render_template, request
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = int(os.getenv("DB_PORT", "3306"))


def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    name = request.form["name"]
    email = request.form["email"]
    message = request.form["message"]

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO users (name, email, message)
                VALUES (%s, %s, %s)
            """
            cursor.execute(sql, (name, email, message))

        connection.commit()

    finally:
        connection.close()

    return render_template("success.html", name=name)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
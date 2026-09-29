import os
import json
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
DATABASE = os.path.join(BASE_DIR, "students.db")
REGIONS_FILE = os.path.join(BASE_DIR, "data", "regions.json")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check that the uploaded file has an allowed image extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_db_connection():
    """Open a new database connection with rows returned as dict-like objects."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the students table if it does not already exist."""
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_filename TEXT,
            first_name TEXT NOT NULL,
            middle_name TEXT,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            gender TEXT NOT NULL,
            dob TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            state TEXT NOT NULL,
            lga TEXT NOT NULL,
            next_of_kin TEXT NOT NULL,
            wassce_aggregate INTEGER NOT NULL,
            admission_status TEXT DEFAULT 'Admitted'
        )
    """)
    conn.commit()
    conn.close()



@app.route("/")
def index():
    """Landing page: Navbar, Intro section, Footer."""
    return render_template("index.html")


@app.route("/form")
def form():
    """Portal form page where a new student registers."""
    return render_template("form.html")


@app.route("/submit", methods=["POST"])
def submit():
    """Validate the submitted form, save the image, and insert a new record."""
    required_fields = [
        "first_name", "last_name", "email", "gender", "dob",
        "phone", "address", "state", "lga", "next_of_kin", "wassce_aggregate"
    ]

    for field in required_fields:
        if not request.form.get(field):
            flash(f"Please fill in the '{field.replace('_', ' ')}' field.")
            return redirect(url_for("form"))

    image = request.files.get("image")
    image_filename = None

    if image and image.filename != "":
        if not allowed_file(image.filename):
            flash("Invalid image file type. Allowed types: png, jpg, jpeg, gif.")
            return redirect(url_for("form"))
        image_filename = secure_filename(image.filename)
        image.save(os.path.join(app.config["UPLOAD_FOLDER"], image_filename))
    else:
        flash("Please upload an image.")
        return redirect(url_for("form"))

    try:
        conn = get_db_connection()
        conn.execute("""
            INSERT INTO students
            (image_filename, first_name, middle_name, last_name, email, gender,
             dob, phone, address, state, lga, next_of_kin, wassce_aggregate, admission_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            image_filename,
            request.form.get("first_name"),
            request.form.get("middle_name"),
            request.form.get("last_name"),
            request.form.get("email"),
            request.form.get("gender"),
            request.form.get("dob"),
            request.form.get("phone"),
            request.form.get("address"),
            request.form.get("state"),
            request.form.get("lga"),
            request.form.get("next_of_kin"),
            request.form.get("wassce_aggregate"),
            "undecided"
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        flash(f"Something went wrong while saving your details: {e}")
        return redirect(url_for("form"))

    return redirect(url_for("students"))


@app.route("/students")
def students():
    """Index page: lists all students in a searchable / filterable table."""
    search_name = request.args.get("name", "")
    status = request.args.get("status", "")
    gender = request.args.get("gender", "")
    wassce_aggregate = request.args.get("wassce_aggregate", "")

    query = "SELECT * FROM students WHERE 1=1"
    params = []

    if search_name:
        query += " AND (first_name LIKE ? OR last_name LIKE ? OR middle_name LIKE ?)"
        like_term = f"%{search_name}%"
        params.extend([like_term, like_term, like_term])

    if status:
        query += " AND admission_status = ?"
        params.append(status)

    if gender:
        query += " AND gender = ?"
        params.append(gender)

    if wassce_aggregate:
        query += " AND wassce_aggregate = ?"
        params.append(wassce_aggregate)

    conn = get_db_connection()
    all_students = conn.execute(query, params).fetchall()
    conn.close()

    return render_template("students.html", students=all_students)


@app.route("/details/<int:student_id>")
def details(student_id):
    """Details page: shows the full record of one student."""
    conn = get_db_connection()
    student = conn.execute(
        "SELECT * FROM students WHERE id = ?", (student_id,)
    ).fetchone()
    conn.close()

    if student is None:
        flash("Student not found.")
        return redirect(url_for("students"))

    return render_template("details.html", student=student)


@app.route("/api/states")
def api_states():
    """Return the list of regions, used to dynamically populate the State select box."""
    with open(REGIONS_FILE) as f:
        data = json.load(f)
    return jsonify(list(data.keys()))


@app.route("/api/lgas/<state>")
def api_lgas(state):
    """Return districts for a given region -- powers the cascading select box."""
    with open(REGIONS_FILE) as f:
        data = json.load(f)
    return jsonify(data.get(state, []))


@app.route("/update_status/<int:student_id>", methods=["POST"])
def update_status(student_id):
    """AJAX endpoint: update a student's admission status without a page reload."""
    new_status = request.json.get("status") if request.is_json else request.form.get("status")

    if new_status not in ("admitted", "rejected", "undecided"):
        return jsonify({"success": False, "message": "Invalid status."}), 400

    conn = get_db_connection()
    conn.execute(
        "UPDATE students SET admission_status = ? WHERE id = ?",
        (new_status, student_id)
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True, "status": new_status})


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
from flask import Flask
from api.routes import api
from api.admin import setup_admin
from api.utils import APIException, generate_sitemap
from api.models import db, Teacher, Course, User
from api.routes import api
from api.admin import setup_admin
from api.commands import setup_commands
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
import os

ENV = "development" if os.getenv("FLASK_DEBUG") == "1" else "production"
static_file_dir = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), '../public/')
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "ultra-secret"  # Change this!
jwt = JWTManager(app)
app.url_map.strict_slashes = False

# database configuration
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"

# No need to create a new SQLAlchemy instance
# db = SQLAlchemy(app)

migrate = Migrate(app, db)

# add the admin
setup_admin(app)

# add the admin
setup_commands(app)

# Add all endpoints form the API with a "api" prefix
app.register_blueprint(api, url_prefix='/api')

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    if ENV == "development":
        return generate_sitemap(app)
    return send_from_directory(static_file_dir, 'index.html')

# any other endpoint will try to serve it like a static file


@app.route('/<path:path>', methods=['GET'])
def serve_any_other_file(path):
    if not os.path.isfile(os.path.join(static_file_dir, path)):
        path = 'index.html'
    response = send_from_directory(static_file_dir, path)
    response.cache_control.max_age = 0  # avoid cache memory
    return response

###############################################################

@app.route('/course', methods=['GET'])
def get_course():
    all_course = Course.query.all()
    results = list(map(lambda elemento: elemento.serialize(), all_course))
    return jsonify({"msg": "Hello course"}), 200

@app.route('/course/<int:class_id>', methods=['GET'])
def get_class_id(course_id):

    print(course_id)
    course = Course.query.filter_by(id=course_id).first()
    return jsonify(course.serialize())


###############################################################

@app.route('/teacher', methods=['GET'])
def get_teacher():
    all_teachers = Teacher.query.all()
    results = list(map(lambda elemento: elemento.serialize(), all_teachers))
    return jsonify({"msg": "Hello Teacher"}), 200

@app.route('/teacher/<int:teacher_id>', methods=['GET'])
def get_teacher_id(teacher_id):

    print(teacher_id)
    teacher = Teacher.query.filter_by(id=teacher_id).first()
    return jsonify(teacher.serialize())

###############################################################


@app.route("/login", methods=['POST'])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    user = User.query.filter_by(email=username).first()
    print(user)
    print(user.serialize())
    if username != "test" or password != "test":
        return jsonify({"msg": "Lo siento, tu password o username esta incorrecta"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=PORT, debug=True)
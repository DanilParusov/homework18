""" Импорт всех необходимых библиотек """
import json
from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from data import data

""" Подключение flask и sqlalchemy """
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

""" Создание модели с фильмами """


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Integer)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


""" Создание модели с режиссерами """


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


""" Создание модели с жанрами """


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


db.drop_all()
db.create_all()

""" Добавление данных в таблицу Movie """
for movie in data["movies"]:
    m = Movie(
        id=movie["pk"],
        title=movie["title"],
        description=movie["description"],
        trailer=movie["trailer"],
        year=movie["year"],
        rating=movie["rating"],
        genre_id=movie["genre_id"],
        director_id=movie["director_id"],
    )
    with db.session.begin():
        db.session.add(m)

""" Добавление данных в таблицу Director """
for director in data["directors"]:
    d = Director(
        id=director["pk"],
        name=director["name"],
    )
    with db.session.begin():
        db.session.add(d)

""" Добавление данных в таблицу Genre """
for genre in data["genres"]:
    g = Genre(
        id=genre["pk"],
        name=genre["name"],
    )
    with db.session.begin():
        db.session.add(g)

""" Создание схемы для Movie """


class SchemaMovie(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Int()
    genre_id = fields.Int()
    director_id = fields.Int()


""" Создание схемы для Director """


class SchemaDirector(Schema):
    id = fields.Int()
    name = fields.Str()


""" Создание схемы для Genre """


class SchemaGenre(Schema):
    id = fields.Int()
    name = fields.Str()


movie_schema = SchemaMovie()  # для одного фильма
movies_schema = SchemaMovie(many=True)  # для нескольких фильмов

director_schema = SchemaDirector()  # для одного режиссера
directors_schema = SchemaDirector(many=True)  # для нескольких режиссеров

genre_schema = SchemaGenre()  # для одного жанра
genres_schema = SchemaGenre(many=True)  # для нескольких жанров

api = Api(app)
""" Создание namespace для всех api """
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')

""" Эндпоинт для Movie /movie """


@movie_ns.route('/')
class MovieView(Resource):
    """ Получение всех фильмов """

    def get(self):
        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        if director_id:
            movies = db.session.query(Movie).filter(Movie.director_id == int(director_id)).all()
            return movies_schema.dump(movies), 200
        elif genre_id:
            movies = db.session.query(Movie).filter(Movie.genre_id == int(genre_id)).all()
            return movies_schema.dump(movies), 200

        """ Help """
        # elif director_id and genre_id:
        # movies = db.session.query(Movie).filter(Movie.director_id == int(
        # director_id)).filter(Movie.genre_id == int(genre_id)).one()
        # return movies_schema.dump(movies), 200

        return movies_schema.dump(Movie.query.all()), 200

    """ Добавление фильма """

    def post(self):
        data = json.loads(request.data)
        new_movie = Movie(**data)
        with db.session.begin():
            db.session.add(new_movie)
        return movie_schema.dump(movie), 201


""" Эндпоинт для Movie /movie/{id} """


@movie_ns.route('/<int:uid>')
class MovieView(Resource):
    """ Получение по id """

    def get(self, uid: int):
        movie = Movie.query.get(uid)
        if not movie:
            return "Фильм не найден", 404
        return movie_schema.dump(movie), 200

    """ Удаление по id """

    def delete(self, uid: int):
        movie = Movie.query.get(uid)
        if not movie:
            return "Фильм не найден", 404
        db.session.delete(movie)
        db.session.commit()
        return "Фильм удален", 204

    """ Частичное обновление по id """

    def put(self, uid: int):
        movie = Movie.query.get(uid)
        if not movie:
            return "Фильм не найден", 404
        data = json.loads(request.data)
        movie.title = data.get("title")
        movie.description = data.get("description")
        movie.trailer = data.get("trailer")
        movie.year = data.get("year")
        movie.rating = data.get("rating")
        movie.genre_id = data.get("genre_id")
        movie.director_id = data.get("director_id")
        db.session.add(movie)
        db.session.commit()
        return "Фильм обновлен", 204


""" Эндпоинт для Director /director """


@director_ns.route('/')
class DirectorView(Resource):
    """ Получение всех режиссеров """

    def get(self):
        return directors_schema.dump(Director.query.all()), 200

    """ Добавление режиссера """

    def post(self):
        data = json.loads(request.data)
        new_director = Director(**data)
        with db.session.begin():
            db.session.add(new_director)
        return director_schema.dump(new_director), 201


""" Эндпоинт для Director /director/{id} """


@director_ns.route('/<int:uid>')
class DirectorView(Resource):
    """ Получение по id """

    def get(self, uid: int):
        director = Director.query.get(uid)
        if not director:
            return "Режиссер не найден", 404
        return director_schema.dump(director), 200

    """ Удаление по id """

    def delete(self, uid: int):
        director = Director.query.get(uid)
        if not director:
            return "Режиссер не найден", 404
        db.session.delete(director)
        db.session.commit()
        return "", 204

    """ Частичное обновление по id """

    def put(self, uid: int):
        director = Director.query.get(uid)
        if not director:
            return "Режиссер не найден", 404
        data = json.loads(request.data)
        director.name = data.get("name")
        db.session.add(director)
        db.session.commit()
        return director_schema.dump(director), 204


""" Эндпоинт для Genre /genre """


@genre_ns.route('/')
class GenreView(Resource):
    """ Получение всех жанров """

    def get(self):
        return genres_schema.dump(Genre.query.all()), 200

    """ Добавление жанра """

    def post(self):
        data = json.loads(request.data)
        new_genre = Genre(**data)
        with db.session.begin():
            db.session.add(new_genre)
        return director_schema.dump(new_genre), 201


""" Эндпоинт для Genre /genre/{id} """


@genre_ns.route('/<int:uid>')
class GenreView(Resource):
    """ Получение по id """

    def get(self, uid: int):
        genre = Genre.query.get(uid)
        if not genre:
            return "Жанр не найден", 404
        return genre_schema.dump(genre), 200

    """ Удаление по id """

    def delete(self, uid: int):
        genre = Genre.query.get(uid)
        if not genre:
            return "Жанр не найден", 404
        db.session.delete(genre)
        db.session.commit()
        return "", 204

    """ Частичное обновление по id """

    def put(self, uid: int):
        genre = Genre.query.get(uid)
        if not genre:
            return "Жанр не найден", 404
        data = json.loads(request.data)
        genre.name = data.get("name")
        db.session.add(genre)
        db.session.commit()
        return genre_schema.dump(genre), 204


if __name__ == '__main__':
    app.run(debug=True)


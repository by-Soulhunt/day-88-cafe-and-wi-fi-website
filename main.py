from flask_bootstrap import Bootstrap5
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, ForeignKey, Boolean
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp, InputRequired
import datetime
import os



# Flask configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("FLASK_KEY")
Bootstrap5(app)


# Create DataBase
class Base(DeclarativeBase):
    """Declarative class"""
    pass

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cafes.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        """ Loop through each column in the data record
        Create a new dictionary entry where the key is the name of the column
        and the value is the value of the column"""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


def convert_data_nums_to_str(data:list):
    """
    Takes all data and convert values from 0 and 1 to "No" and "Yes"
    :param data: list of Cafe objects
    :return: list with converted attributes
    """
    columns = ["has_sockets", "has_toilet", "has_wifi", "can_take_calls"]
    for cafe in data:
        for column in columns:
            value = getattr(cafe, column)  # Take value of attribute
            if value:  # Checking if a value is 1
                setattr(cafe, column, "Yes")  # Set new value YES
            else:  # If the value is 0
                setattr(cafe, column, "No")  # Set new value NO

    return data

# Routs
@app.route("/")
def index():
    # Cafe data from DataBase
    cafe = db.session.execute(db.Select(Cafe))
    cafe = cafe.scalars().all()
    # Data with changed cafe options info
    all_cafe = convert_data_nums_to_str(cafe)

    return render_template("index.html", all_cafe=all_cafe)

if __name__ == "__main__":
    app.run(debug=True, port=5005)
from flask_bootstrap import Bootstrap5
from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import  DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, IntegerField, FloatField
from wtforms.validators import DataRequired,  Length, URL
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


class AddNewCafe(FlaskForm):
    """
    New Cafe Add Form
    """
    name = StringField("Cafe Name", validators=[DataRequired(), Length(min=2, max=100)])
    map_url = StringField("Map URL", validators=[DataRequired(), URL()])
    img_url = StringField("IMG URL", validators=[DataRequired(), URL()])
    location = StringField("Location", validators=[DataRequired(), Length(min=2, max=100)])
    has_sockets = SelectField("Has sockets?:", choices=[("False","No"), ("True","Yes")])
    has_toilet = SelectField("Has toilet?:", choices=[("False","No"), ("True","Yes")])
    has_wifi = SelectField("Has wifi?:", choices=[("False","No"), ("True","Yes")])
    can_take_calls = SelectField("Can take calls?:", choices=[("False","No"), ("True","Yes")])
    seats = IntegerField("Seats", validators=[DataRequired()])
    coffee_price = FloatField("Coffee Price", validators=[DataRequired()])
    submit = SubmitField("Add information")


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

@app.route("/add-new-cafe", methods=["GET", "POST"])
def add_new_cafe():
    """
    Takes data from form and
    :return: Add new data into database
    """
    form = AddNewCafe()
    if form.validate_on_submit():
        # Create new cafe object
        new_cafe = Cafe (
        name = request.form.get("name"),
        map_url = request.form.get("map_url"),
        img_url = request.form.get("img_url"),
        location = request.form.get("location"),

        # Check and convert str into bool
        has_sockets = request.form.get("has_sockets") == "True",
        has_toilet = request.form.get("has_toilet")  == "True",
        has_wifi = request.form.get("has_wifi")  == "True",
        can_take_calls = request.form.get("can_take_calls")  == "True",
        # Check and convert str into bool

        seats = request.form.get("seats"),
        coffee_price = request.form.get("coffee_price")
        )

        # Add new cafe into DataBase
        db.session.add(new_cafe)
        db.session.commit()

        return redirect(url_for("index"))

    return render_template("add_new_cafe.html", form=form)


@app.route("/edit/<int:cafe_id>", methods=["GET", "POST"])
def edit_cafe(cafe_id):
    current_cafe = db.session.get_one(Cafe, cafe_id)

    if not current_cafe:
        return redirect(url_for("index"))

    # Show current information from DataBase
    edit_form = AddNewCafe(
        obj=current_cafe
    )
    if edit_form.validate_on_submit():
        current_cafe.name = edit_form.name.data
        current_cafe.map_url = edit_form.map_url.data
        current_cafe.img_url = edit_form.img_url.data
        current_cafe.location = edit_form.location.data
        current_cafe.has_sockets = edit_form.has_sockets.data == "True"
        current_cafe.has_toilet = edit_form.has_toilet.data == "True"
        current_cafe.has_wifi = edit_form.has_wifi.data == "True"
        current_cafe.can_take_calls = edit_form.can_take_calls.data == "True"
        current_cafe.seats = edit_form.seats.data
        current_cafe.coffee_price = edit_form.coffee_price.data
        db.session.commit()

        return redirect(url_for("index"))

    return render_template("add_new_cafe.html", form=edit_form)


@app.route("/delete", methods=["POST"])
def delete_cafe():
    cafe_id = request.form.get('cafe_id')
    current_cafe = db.session.get_one(Cafe, cafe_id)
    db.session.delete(current_cafe)
    db.session.commit()

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, port=5005)
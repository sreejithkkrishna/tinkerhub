from flask_wtf import FlaskForm
from wtforms import StringField,TextAreaField,SubmitField,SelectField,IntegerField
from wtforms.validators import DataRequired,Length,ValidationError
from wtforms.fields.html5 import DateField
from datetime import date, timedelta

class EventForm(FlaskForm):
    title = StringField('Title',validators=[DataRequired(),Length(min=5)])
    description = TextAreaField('Description',validators=[DataRequired(),Length(min=30)])
    event_date = DateField('Event Date', validators=[DataRequired()])
    state = SelectField('State',validate_choice=False, validators=[DataRequired()])
    city = SelectField('city', validate_choice=False, validators=[DataRequired()])
    place = StringField('Place', validators=[DataRequired()])
    category = SelectField('Category', choices=['Seminar', 'Conference', 'Trade shows', 'Workshops','IT'])
    seat = IntegerField('Seat available', validators=[DataRequired()])

    submit = SubmitField('Post')

    def validate_event_date(self,field):
        check_date = date.today()+timedelta(days=2)
        if check_date > field.data:
            raise ValidationError('Please select a date atleast 2 days later')

    #check city name


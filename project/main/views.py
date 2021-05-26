
from flask import render_template, request, Blueprint
from project.models import Event

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def home():
    page = request.args.get('page',1,type=int)
    event = Event.query.order_by(Event.date_posted.desc()).paginate(per_page=5,page=page)
    return render_template('home.html',events=event)


@main.route('/about')
def about():
    return render_template('about.html')
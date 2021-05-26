from flask import (Blueprint,render_template,redirect,url_for,flash,
        request,current_app,jsonify,session,abort)
from flask_login import current_user,login_required
from project.events.forms import EventForm
from project.models import Event,User
from project import db
import os, json
from flask_weasyprint import HTML, render_pdf

def pprint(message):
    print(f'\n#################\n{message}\n')


events = Blueprint('events',__name__)

@events.route('/event/new',methods=['POST','GET'])
@login_required
def new_event():
    form = EventForm()
    with open(os.path.join(current_app.root_path,'states-and-districts.json')) as f:
        data = json.load(f)
        states = [ data['states'][i]['state'] for i in range(len(data['states']))]
        city = data['states'][0]['districts']
        pprint(states)
    form.state.choices = states
    form.city.choices = city
    
    if form.validate_on_submit():
        event = Event(
                author = current_user,
                title = form.title.data,
                description = form.description.data,
                event_date = form.event_date.data,
                state = form.state.data,
                city = form.city.data,
                category = form.category.data,
                seat = form.seat.data,
                place = form.place.data,
                )
        db.session.add(event)
        db.session.commit()
        flash('Your Event has been created','success')
        return redirect(url_for('main.home'))
    return render_template('create_event.html', title='New Event', form=form, legend='Create Event')

@events.route('/city/<state>')
def city(state):
    pprint('called')
    with open(os.path.join(current_app.root_path,'states-and-districts.json')) as f:
        data = json.load(f)
        for data in data['states']:
            if data['state'] == state:
                districts = data['districts']
                break

    cityArray = []

    for city in districts:
        cityObj = {}
        cityObj['name'] = city
        cityArray.append(cityObj)

    return jsonify({'cities' : cityArray})

@events.route('/event/<int:event_id>')
def event(event_id):
    event = Event.query.get_or_404(event_id)
    if current_user in event.participents:
        pprint('found')

    return render_template('event.html',title=event.title,event=event)

@events.route('/event/<int:event_id>/update',methods=['POST','GET'])
@login_required
def update_event(event_id):
    form = EventForm()
    event = Event.query.get(event_id)
    if event.author != current_user:
        abort(403)
    if form.validate_on_submit():
        event.title = form.title.data
        event.description = form.description.data
        event.event_date = form.event_date.data
        event.category = form.category.data
        event.seat = form.seat.data
        event.place = form.place.data

        db.session.commit()
        flash('Event Successfully Updated','success')
        return redirect(url_for('events.event',event_id=event_id))
    elif request.method == 'GET':
        form.title.data = event.title
        form.description.data = event.description
        form.event_date.data = event.event_date
        form.state.choices = [event.state,]
        form.city.choices = [event.city,]
        form.category.data = event.category
        form.seat.data = event.seat
        form.place.data = event.place

    return render_template('create_event.html',legend='Update Event',form=form)

#only need event,becuz we only going to accept request if it submitted through the form 
@events.route('/event/<int:event_id>/delete',methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get(event_id)
    if event.author != current_user:
        abort(403)
    db.session.delete(event)
    db.session.commit()
    flash('Event Delete successfully','success')
    return redirect(url_for('main.home'))


@events.route('/event/<string:username>')
def user_events(username):
    page = request.args.get('page',1,type=int)
    user = User.query.filter_by(username=username).first_or_404()
    event = Event.query.filter_by(author=user)\
            .order_by(Event.date_posted.desc()).paginate(per_page=5,page=page)
    return render_template('user_events.html',user=user,events=event)

@events.route('/participate_event/<int:event_id>', methods=['POST','GET'])
@login_required
def participate_in_event(event_id):
    event = Event.query.get(event_id)
    event.participents.append(current_user)
    event.seat = event.seat-1
    db.session.commit()
    return redirect(url_for('events.event', event_id=event_id))

@events.route('/cancel_participate/<int:event_id>', methods=['POST','GET'])
def cancel_participate(event_id):
    event = Event.query.get(event_id)
    event.participents.remove(current_user)
    event.seat = event.seat+1
    db.session.commit()
    return redirect(url_for('events.event', event_id=event_id))


@events.route('/participent_pdf/<event_id>', methods=['GET'])
def participent_pdf(event_id):
    event = Event.query.get(event_id)
    if current_user != event.author:
        abort(403)
    all_participent=[
            [user.username,user.email]
            for user in event.participents]
    html = render_template('view_participent.html', participent=all_participent)
    return render_pdf(HTML(string=html), download_filename= f'{event.title}.pdf')


@events.route('/events')
@login_required
def participated_event():
    return render_template('par.html')


    

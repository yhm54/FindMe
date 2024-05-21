from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import LargeBinary
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import io
from main import scan

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///final_events.db"
# app.config['SQLALCHEMY_DATABASE_URI_URI'] = "sqlite:///credentials.db"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///findme_final_final_final_final.db"

db = SQLAlchemy(app)


# username = "yhm54"


class Credentials(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200), nullable=True)
    event_name = db.Column(db.String(200), nullable=False)
    files = db.relationship('ImageFile', backref='event', lazy=True)

    def __repr__(self):
        return '<User %r>' % self.username


class ImageFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(300), nullable=False)
    filedata = db.Column(LargeBinary, nullable=False)
    eventid = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)

    def __repr__(self):
        return '<File %r>' % self.filename


xyz = "HI"


@app.route('/user_events')
def user_events():
    print("user_events")
    print(str(request.args))
    username = request.args.get('username')
    print(username)

    events = Event.query.filter_by(username=username).all()
    print(events)
    event_data = []

    for eventl in events:
        event_data.append({'event': eventl.id, 'event_name': eventl.event_name, 'location': eventl.location,
                           'files': len(ImageFile.query.filter_by(eventid=eventl.id).all())})
    # Retrieve the user and print the list of files

    # print(len(all_photos_ever))
    # user = Event.query.first()
    # # for file in request.files:
    # #     file1 = File(filename=file[''], event=event)
    #
    # db.session.commit()

    # Retrieve the user and print the list of files
    # user = Event.query.first()
    return render_template("user_events.html", username=username, event_data=event_data)


@app.route('/')
def login():
    return render_template("login.html", str=xyz)


errmsg = ""


@app.route('/login', methods=['POST', 'GET'])
def req_login():
    print(request.method)
    if request.method == 'POST':
        return render_template('sign_up.html')
    else:
        username = request.args.get('username')
        print(username)

        password = request.args.get('password')
        print(password)
        if len(Credentials.query.filter_by(username=username).all()) == 0:
            print("no user")
            return render_template("login.html", error_message="Username doesn't exist")
        else:
            if Credentials.query.filter_by(username=username).first().password == password:
                print("pass")
                return redirect(url_for('user_events', username=username))
            else:
                print("err pass")
                return render_template("login.html", error_message="Wrong password")


@app.route('/sign_up', methods=['POST'])
def sign_up():
    print("sign_up")
    print(request.form)

    space_there = False

    if request.form['p1'] == "" or request.form['un'] == "":
        return render_template("sign_up.html", error_message="Enter something G")

    try:
        if request.form['p1'].index(" ") or request.form['un'].index(" "):
            space_there = True
    except ValueError:
        space_there = False

    if request.form['p1'] != request.form['p2']:
        errmsg = "Passwords don't match"
        return render_template("sign_up.html", error_message=errmsg)
    elif space_there:
        return render_template("sign_up.html", error_message="Password or Username contains one or more spaces")

    if len(Credentials.query.filter_by(username=request.form['un']).all()) > 0:
        return render_template("sign_up.html", error_message="Username already exists")

    cred = Credentials(username=request.form['un'], password=request.form['p1'])
    print(cred)
    username = request.form['un']
    db.session.add(cred)
    db.session.commit()
    return redirect(url_for('user_events', username=username))


@app.route('/create_event')
def create_event():
    print("create_event")

    username = request.args.get('username')

    print(username)
    return render_template("create_event.html", username=username)


@app.route('/upload_dir', methods=['post'])
def upload_dir():
    print("upload_dir")
    # print(str(request.form))
    username = request.form['username']
    location = request.form['location']
    event_name = request.form['event_name']

    e = Event(username=username, location=location, event_name=event_name)
    db.session.add(e)
    db.session.commit()
    e_id = e.id

    for binary_data in request.files.getlist('file'):
        # Convert binary data to image
        image_stream = io.BytesIO(binary_data.read())
        image = Image.open(image_stream)

        if image.mode == 'RGBA':
            image = image.convert('RGB')

        with io.BytesIO() as output:
            image.save(output, format='JPEG')
            image_bytes = output.getvalue()

        # print(image_bytes)
        f = ImageFile(filename=binary_data.filename, filedata=image_bytes, eventid=e_id)
        db.session.add(f)
        db.session.commit()
        # Convert PIL image to NumPy array
    return redirect(url_for('user_events', username=username))


import base64


@app.route('/join_event')
def join_event():
    print("join_event")
    username = request.args.get('username')
    return render_template("join_event.html", username=username)


send_these_images = []


@app.route('/event', methods=['get'])
def event():
    print("fetching")
    send_these_images.clear()
    pc = request.args.get('passcode')
    event_data = Event.query.filter_by(id=pc).first()
    images = ImageFile.query.filter_by(eventid=pc).all()
    # print(images)
    for image in images:
        # print(image.filedata)
        send_these_images.append(base64.b64encode(image.filedata).decode('utf-8'))
    print(event_data)
    # print(len(images))
    return render_template("event.html", event_data=event_data, passcode=pc, search_result=False, images=send_these_images)


@app.route('/search', methods=['post'])
def search():

    # print(request.files)
    img = request.files.get('faceImg')
    passcode = request.form['passcode']
    print(passcode)
    event_data = Event.query.filter_by(id=passcode)
    print(event_data)
    # imgs = request.files.getlist('allImages')
    image_stream = io.BytesIO(img.read())
    image = Image.open(image_stream)

    if image.mode == 'RGBA':
        image = image.convert('RGB')

    with io.BytesIO() as output:
        image.save(output, format='JPEG')
        image_bytes = output.getvalue()

    print("fetching matches")

    images = scan(image_bytes, send_these_images)

    # send_these_images.clear()
    # pc = request.args.get('passcode')
    # images = ImageFile.query.filter_by(eventid=pc).all()
    # print(images)
    # send_these_images.clear()

    search_images = []

    for image in images:
        # print(image.filedata)
        image = Image.fromarray(image)

        # Create a BytesIO object to hold the image data
        with io.BytesIO() as output:
            image.save(output, format='JPEG')
            image_bytes = output.getvalue()

        # Encode the byte data as a base64 string
        base64_encoded = base64.b64encode(image_bytes).decode("utf-8")
        search_images.append(base64_encoded)

    # print(images)
    print(len(send_these_images))
    return render_template('event.html', event_data=event_data, passcode=passcode, search_result=True, images=search_images)



with app.app_context():
    db.create_all()

    # Create a user with a list of files
    # event = Event(username='example')
    # file1 = File(filename='file1.txt', event=event)
    # file2 = File(filename='file2.txt', event=event)
    # db.session.add(event)
    # db.session.add(file1)
    # db.session.add(file2)
    # db.session.commit()
    #
    # # Retrieve the user and print the list of files
    # user = Event.query.first()
    # print([file.filename for file in event.files])

if __name__ == "__main__":
    app.run(debug=True)

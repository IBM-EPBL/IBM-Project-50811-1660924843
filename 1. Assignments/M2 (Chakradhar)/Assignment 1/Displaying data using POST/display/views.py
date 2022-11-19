from flask import Blueprint, request 
from flask import render_template # for rendering the html templates

blue = Blueprint("print", "__name__")

@blue.route('/', methods=('GET', 'POST'))
def home():
    if request.method == 'POST':
        # getting the data entered by the user from the request
        name = request.form.get('name')
        Qualification = request.form.get('Qualification')
        Age = request.form.get('Age')
        email = request.form.get('email')

        return render_template('display.html',
            name = name, Qualification = Qualification, Age = Age,email=email
        )
        
    return render_template('index.html')

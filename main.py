"""Personal Blog (Capstone Part 3)

This 'Flask' app website is the third part of a 'Blog Capstone' project.
In part 3, the ability obtain, create, edit and delete blog posts from an SQLite database were implemented.
It has 5 pages: The index, about, contact, make-post and an individual blog post page.
There are 2 HTML templates used in inheritance to keep specific elements on each page.
The blog posts data are obtained from an SQLite database. 'Jinja' templating is used
to render 'Python' code inside the HTML templates. The static files (CSS, img, JS) were provided
by the instructor.

This script requires that 'Flask', 'requests', 'smtplib',
and 'python_dotenv', 'Flask-Bootstrap', 'Flask-SQLAlchemy', 'Flask-WTF',
and 'flask-ckeditor' be installed within the Python
environment you are running this script in.
"""

from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
import datetime as dt

## Delete this code:
# import requests
# posts = requests.get("https://api.npoint.io/43644ec4f0013682fc0d").json()

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##CONFIGURE TABLE
class BlogPost(db.Model):
    """
    A class used to represent a blog post record in a database.
    ...
    Attributes
    ----------
    id: db.Column
        an integer column representing the primary key
    title: db.Column
        a string column representing the title of the blog post
    subtitle: db.Column
        a string column representing the subtitle of the blog post
    date: db.Column
        a date column representing when the blog post was created
    author: db.Column
        a string column representing the writer of the blog post
    img_url: db.Column
        a string column representing a URL to an image relevant to the blog post
    """

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


##WTForm
class CreatePostForm(FlaskForm):
    """
    A class used to represent create a Flask-WTForm to create new blog posts
    ...
    Attributes
    ----------
    title: StringField
        a string field to enter the title of the blog post
    subtitle: StringField
        a string field to enter the subtitle of the blog post
    author: StringField
        a string field to enter the author of the blog post
    img_url: StringField
        a string field to enter the URL to the image relevant to the blog post
    body: CKEditorField
        a string field to enter the main content of the blog post
    submit: SubmitField
        a submit field to submit the form data
    """

    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


@app.route('/')
def get_all_posts():
    """the landing page, displays all blog posts

    GET: Landing page
    """

    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:index>")
def show_post(index):
    """the individual blog post page, displays one blog post

    GET: Individual blog post page
    """

    requested_post = None
    posts = BlogPost.query.all()
    for blog_post in posts:
        if blog_post.id == index:
            requested_post = blog_post
    return render_template("post.html", post=requested_post)


@app.route("/about")
def about():
    """the about page, displays information about the blog

    GET: About page
    """

    return render_template("about.html")


@app.route("/contact")
def contact():
    """the contact page, displays a form

    GET: Contact page
    """

    return render_template("contact.html")


@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    """the page to edit individual blog posts, displays a form to edit the post data

    Parameters
    ----------
    post_id: int
        the id of the blog post the user wishes to edit

    GET: displays the form to edit the post data
    POST: makes a request to edit the post data, redirects to the individual post page for the edited blog post
    """

    post_id = post_id
    blog_post = BlogPost.query.get(post_id)
    #Create a WTF quick form and pass in default values into the fields
    form = CreatePostForm(
        title=blog_post.title,
        subtitle=blog_post.subtitle,
        author=blog_post.author,
        img_url=blog_post.img_url,
        body=blog_post.body,
    )
    #update all of the data for the blog_post if POST request, then redirect to the page for that post
    if form.validate_on_submit():
        blog_post.title = form.title.data
        blog_post.subtitle = form.subtitle.data
        blog_post.author = form.author.data
        blog_post.img_url = form.img_url.data
        blog_post.body = form.body.data
        db.session.commit()
        return redirect(url_for('show_post', index=post_id))
    return render_template('make-post.html', form=form, new_post=False)


# HTTP POST ROUTE
@app.route('/new-post', methods=['POST', 'GET'])
def new_post():
    """the page to create a new individual blog post, displays a form to create the blog post

    GET: displays the form to create a new blog post
    POST: makes a request to create a new blog post in the database, redirects to the landing page
    """

    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            date=dt.datetime.now().strftime('%m %d, %Y'),
            body=form.body.data,
            author=form.author.data,
            img_url=form.img_url.data
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    return render_template('make-post.html', form=form, new_post=True)


@app.route('/delete/<int:post_id>')
def delete(post_id):
    """deletes a specific blog post from the database

    Parameters
    ----------
    post_id: int
        the id in the database for the blog post the user wishes to delete

    GET: deletes a specific blog post from the database, redirects to the landing page
    """

    blog_post = BlogPost.query.get(post_id)
    db.session.delete(blog_post)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run(debug=True)
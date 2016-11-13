import os
import re
import random
import hashlib
import hmac
from string import letters

import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

secret = 'ashokm'

# Features:
#   Register new user
#   Login user
#   Logout user
#   View all blogs
#   Add a new blog
#   Edit a blog
#   Comment on a blog
#   Like/Unlike a blog
#   Delete a blog

############## functions
def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())


def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

def render_post(response, post):
    response.out.write('<b>' + post.subject + '</b><br>')
    response.out.write(post.content)


class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))


############# Main Page
class MainPage(BlogHandler):
    def get(self):
        self.write('Hello, Welcome to Blog Posts!')


##### user logic
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")


def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")


def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')


def valid_email(email):
    return not email or EMAIL_RE.match(email)


def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))


def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)


def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)


def users_key(group = 'default'):
    return db.Key.from_path('users', group)


class Signup(BlogHandler):
    def get(self):
        self.render("signup-form.html")

    def post(self):
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username = self.username,
                      email = self.email)

        if not valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup-form.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError


class Register(Signup):
    def done(self):
        #make sure the user doesn't already exist
        u = User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('signup-form.html', error_username = msg)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('/blog')


class Login(BlogHandler):
    def get(self):
        self.render('login-form.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/blog')
        else:
            msg = 'Invalid login'
            self.render('login-form.html', error = msg)


class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.redirect('/blog')


class User(db.Model):
    name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent = users_key())

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent = users_key(),
                    name = name,
                    pw_hash = pw_hash,
                    email = email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u


################### Post related logic
def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)


@db.transactional
def insert_new_post(p_subject, p_content, p_owner, p_rowid):
    np_p = Post(parent=blog_key(), subject=p_subject, content=p_content, owner=p_owner, rowid=p_rowid, likes=0, unlikes=0)
    np_p.put()


@db.transactional
def insert_new_comment(p_rowid, p_comment):
    nc_p = Comment(parent=blog_key(), rowid=p_rowid, comment=p_comment)
    nc_p.put()


class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    rowid = db.IntegerProperty(required = True)
    owner = db.StringProperty(required = True)
    likes = db.IntegerProperty(required = True)
    unlikes = db.IntegerProperty(required = True)

    @classmethod
    def by_rowid(cls, rowid):
        p = Post.all().filter('rowid =', rowid).get()
        return p

    @classmethod
    def all_order_by_rowid(cls):
        p = Post.all().order('-rowid').get()
        return p

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p = self)


class Comment(db.Model):
    rowid = db.IntegerProperty(required = True)
    comment = db.StringProperty(required = True)

    @classmethod
    def all_by_rowid_order_by_rowid(cls, rowid):
        c = Comment.all().filter('rowid =', rowid).order('-rowid').get()
        return c


class BlogFront(BlogHandler):
    def get(self):
        posts = greetings = Post.all().order('-created')
        self.render('front.html', posts = posts)


class PostPage(BlogHandler):
    def get(self, post_id):
        # dummy call to force insert commit
        p2 = Post.all_order_by_rowid()

        #get all rows for a post
        pp = Post.by_rowid(int(post_id))
        if pp:
            pp_post = Post(parent=blog_key(), subject=pp.subject, content=pp.content,
                           owner=pp.owner, rowid=int(post_id), likes=pp.likes, unlikes=pp.unlikes)
            comment_list = []

            # get all comments
            comment_cur = Comment.all()
            result=''
            for i in comment_cur.run():
                # create list of comments for a post
                if i.rowid == int(post_id):
                    comment_list.append(i.comment)
            # iterate thru list to create html code
            for i, val in enumerate(comment_list):
                    result += val + '<br>'
            self.render("permalink.html", post = pp_post, comment=result)
        else:
            msg = 'Post id %s not found' % post_id
            self.render('errorpost.html', error = msg)


class EditPage(BlogHandler):
    def get(self, post_id):
        if self.user is None:
            self.redirect("/login")
            return

        #get data for the post id
        ep_get = Post.by_rowid(int(post_id))
        if ep_get:
            if ep_get.owner != self.user.name:
                msg = 'Post id %s: You are not the owner of the post so cannot edit' % post_id
                self.render('errorpost.html', error=msg)
                return
            self.render("editpost.html", subject=ep_get.subject, content=ep_get.content)
        else:
            msg = 'Post id %s not found' % post_id
            self.render('errorpost.html', error=msg)

    def post(self, post_id):
        # get edited data
        ep_subject = self.request.get('subject')
        ep_content = self.request.get('content')
        ep_post = Post.by_rowid(int(post_id))
        if ep_post:
            # save record to database
            ep_post.subject = ep_subject
            ep_post.content = ep_content
            ep_post.put()
            posts = greetings = Post.all().order('-created')
            self.render('front.html', posts = posts)


class CommentPage(BlogHandler):
    def get(self, post_id):
        if self.user is None:
            self.redirect("/login")
            return

        #get data for the post id
        cp_get = Post.by_rowid(int(post_id))
        if cp_get:
            if cp_get.owner == self.user.name:
                msg = 'Post id %s: You are the owner of the post so cannot comment on it' % post_id
                self.render('errorpost.html', error=msg)
                return
            self.render("commentpost.html", rowid=cp_get.rowid, owner=cp_get.owner, subject=cp_get.subject,
                        content=cp_get.content, likes=cp_get.likes, unlikes=cp_get.unlikes)
        else:
            msg = 'Post id %s not found' % post_id
            self.render('errorpost.html', error=msg)

    def post(self, post_id):
        comment = self.request.get('comment')
        cp_post = Post.by_rowid(int(post_id))
        if cp_post:
            # save comment to database
            insert_new_comment(int(post_id), comment)
            self.redirect('/blog/%s' % post_id)
        else:
            msg = 'Post id %s not found' % post_id
            self.render('errorpost.html', error=msg)


class DeletePage(BlogHandler):
    def get(self, post_id):
        if self.user is None:
            self.redirect("/login")
            return

        #get data for the post id
        dp_get = Post.by_rowid(int(post_id))
        if dp_get:
            if dp_get.owner != self.user.name:
                msg = 'Post id %s: You are not the owner of the post so cannot delete' % post_id
                self.render('errorpost.html', error=msg)
                return
            self.render("deletepost.html", rowid=dp_get.rowid, owner=dp_get.owner, subject=dp_get.subject,
                        content=dp_get.content, likes=dp_get.likes, unlikes=dp_get.unlikes)
        else:
            msg = 'Post id %s not found' % post_id
            self.render('errorpost.html', error=msg)

    def post(self, post_id):
        dp_post = Post.by_rowid(int(post_id))
        if dp_post:
            dp_post.delete()
            msg = 'Post successfully deleted'
            self.render('messagepost.html', message=msg)
        else:
            msg = 'Post id %s not found' % post_id
            self.render('errorpost.html', error=msg)


class LikeUnlikePage(BlogHandler):
    def get(self, post_id):
        if self.user is None:
            self.redirect("/login")
            return

        #get data for the post id
        lu_get = Post.by_rowid(int(post_id))
        if lu_get:
            if lu_get.owner == self.user.name:
                msg = 'Post id %s: You are the owner of the post so cannot like/unlike' % post_id
                self.render('errorpost.html', error=msg)
                return
            self.render("likeunlikepost.html", rowid=lu_get.rowid, owner=lu_get.owner, subject=lu_get.subject,
                        content=lu_get.content, likes=lu_get.likes, unlikes=lu_get.unlikes)
        else:
            msg = 'Post id %s not found' % post_id
            self.render('errorpost.html', error=msg)

    def post(self, post_id):
        #get current value of like and unlike and increment based on response
        p_like = 0;
        p_unlike = 0;
        lu_likeunlike = self.request.get('likeunlike')
        lu_post = Post.by_rowid(int(post_id))
        if lu_post:
            if lu_likeunlike == 'like':
                lu_post.likes += 1
            else:
                lu_post.unlikes += 1
            lu_post.put()
            posts = greetings = Post.all().order('-created')
            self.render('front.html', posts = posts)


class NewPost(BlogHandler):
    def get(self):
        if self.user:
            self.render("newpost.html")
        else:
            self.redirect("/login")

    def post(self):
        if not self.user:
            self.redirect('/blog')

        # get input data
        np_subject = self.request.get('subject')
        np_content = self.request.get('content')
        np_owner = self.user.name
        np_rowid = 0

        # get last rowid value
        p = Post.all_order_by_rowid()
        if p:
            np_rowid = p.rowid

        #increment rowid and save record
        if np_subject and np_content:
            # save new blog to database
            insert_new_post(np_subject, np_content, np_owner, np_rowid+1)
            self.redirect('/blog/%s' % str(np_rowid+1))
        else:
            error = "subject and content, please!"
            self.render("newpost.html", subject=np_subject, content=np_content, error=error)


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/blog/?', BlogFront),
                               ('/blog/([0-9]+)', PostPage),
                               ('/blog/newpost', NewPost),
                               ('/blog/editpost/([0-9]+)', EditPage),
                               ('/blog/commentpost/([0-9]+)', CommentPage),
                               ('/blog/deletepost/([0-9]+)', DeletePage),
                               ('/blog/likeunlikepost/([0-9]+)', LikeUnlikePage),
                               ('/signup', Register),
                               ('/login', Login),
                               ('/logout', Logout),
                               ],
                              debug=True)
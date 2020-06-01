from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.main.forms import EditProfileForm, EmptyForm, PostForm, CloseAccountForm
from app.models import User, Post
from app.main import bp

@bp.before_app_request #decorator 
def before_request(): #before the user accesses any page in our server we implicitly log the time in which they accessed it
    if current_user.is_authenticated: #checks if user is logged in (must be a registered user) if so...
        current_user.last_seen = datetime.utcnow() #we set the current time data we have for the user, to the updated time
        db.session.commit() #save the data in our database
    g.locale = str(get_locale())

@bp.route("/", methods=['GET', 'POST'])  # decorator
@bp.route("/index", methods=['GET', 'POST'])  # decorator
@login_required
def index():  # view function
    form = PostForm()
    if form.validate_on_submit(): #if submission passes validation...
        post = Post(body=form.post.data, author=current_user) #posts instance variable is set to the user's post data
        db.session.add(post) #adds post data to the db
        db.session.commit() #saves the db
        flash(_('Your post has been published!')) #comfirmation message
        return redirect(url_for('main.index')) #redirect to home page
    page = request.args.get("page", 1, type=int) #'page' is set to the first page of posts using the request.args.get method. "page" is an identifier used in the link, "1" is the page number, and we know 1 is an int but we declare in with type=int 
    posts = current_user.followed_posts().paginate(page, current_app.config['POSTS_PER_PAGE'], False) #gets the posts from users followed pages, .paginate is used to retrieve only the disired page of post results
    next_url = url_for('main.index', page = posts.next_num) \
        if posts.has_next else None  #next_url is assigned the link to the next page, if no next page available, link is not shown
    prev_url = url_for("main.index", page = posts.prev_num) \
        if posts.has_prev else None  #prev_url is assigned the link to the prev page, if no previous page available, link is not shown
    return render_template("index.html", title=_("Home Page"), form=form, posts=posts.items, next_url=next_url, prev_url=prev_url) #render_template renders code in html. #colored 'posts' contains all the user's posts, 'posts' can be accessed by 'index.html' to print data to the page usually using the "." operator

#'GET' request = no page input from user allowed, (page can only output to the user). 'POST' request = a user can submit data from a form to the page.
@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int) #determines page number 1 will be shown
    posts= Post.query.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False) #gets the posts from users followed pages, .paginate is used to retrieve only the disired page of post results
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None #next_url is assigned the link to the next page, if no next page available, link is not shown
    prev_url= url_for('main.explore', page = posts.prev_num) \
        if posts.has_prev else None #prev_url is assigned the link to the prev page, if no previous page available, link is not shown
    return render_template('index.html', title=_('Explore'), posts=posts.items, next_url=next_url, prev_url=prev_url)

@bp.route('/user/<username>') #route to a user profile
@login_required #must be logged in to see a user profile
def user(username):
    user = User.query.filter_by(username=username).first_or_404() # either finds the user's profile or returns a 404 error
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username, page=posts.next_num) \
        if posts.has_next else None #next_url is assigned the link to the next page, if no next page available, link is not shown   
    prev_url = url_for('main.user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None #prev_url is assigned the link to the prev page, if no previous page available, link is not shown
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url, form=form) #colored 'user' contains all the user's data and colored 'posts' contains all the user's posts. Both 'user' and 'posts' can be accessed by 'user.html' to print data to the page usually using the "." operator

@bp.route('/edit_profile', methods=['GET','POST'])
@login_required
def edit_profile(): #data pre-checks are done in forms.py, so the form can check the inputs for invalidity and inform the user of the invalidity before the page can be submitted
    form = EditProfileForm(current_user.username) #invokes the editprofile form
    if form.validate_on_submit(): #if the user submits...
        current_user.username=form.username.data #reassign the current username data to the newly submitted username data 
        current_user.about_me=form.about_me.data #reassign the current about me data to the newly submitted about_me data 
        db.session.commit() #save the changes in the data base
        flash(_('Your changes have been saved')) #let the user know their changes have been saved
        return redirect(url_for('main.edit_profile')) #redirects user to edit profile page
    elif request.method == 'GET': #else if, if the user has just been directed to the edit profile page for an initial time('GET'TING INFO)...
        form.username.data = current_user.username # pre-populate the username and about_me 
        form.about_me.data = current_user.about_me # forms with the data we have in our database
    CAform = CloseAccountForm()    
    return render_template('edit_profile.html', title=_('Edit Profile'), form=form, CAform=CAform) #colored 'form' contains all the user's form data, 'form' can be accessed by 'edit_profile.html' to print data to the page usually using the "." operator

@bp.route('/follow/<username>', methods = ['POST'])
@login_required
def follow(username):
    form = EmptyForm()        
    if form.validate_on_submit(): #if follow is clicked...
        user = User.query.filter_by(username=username).first() #check for a matching username in User db
        if user is None: #if no matching username found in User db...
            flash(_('User %(username)s not found', username=username)) #flash message
            return redirect(url_for('main.index'))#and redirect user to home page
        if user == current_user: #if user attempts to follow themself...
            flash(_('Nice try, you cannot follow yourself.')) #flash message
            return redirect(url_for('main.user', username=username)) #and send them back to their profile
        current_user.follow(user) #if user is NOT == None and NOT == current_user, follow the user that current_user wishes to follow
        db.session.commit() #update the data in the database
        flash(_('You are now following %(username)s!', username=username)) #flash confirmation message
        return redirect(url_for('main.user', username=username)) #finally send them back to their profile page
    else:
        return redirect(url_for('main.index')) #if form is not validated, redirect user to home page  

@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first() #sets user to the first match found or None if no match found
        if user is None: #if no username match found...
            flash(_('User %(username)s not found', username = username)) #flash message
            return redirect(url_for('main.index')) #and then send user to home
        if user == current_user: #if user tries to unfollow themselves...
            flash(_('Nice try %(username)s, you cannot unfollow yourself.', username=username)) #print flash message
            return redirect(url_for('main.user', username=username)) #and then takes the user their page
        current_user.unfollow(user) #if username is found and it is not the current_user's, process the unfollow
        db.session.commit() #save changes in database
        flash(_('You no longer follow %(username)s', username=username)) #flash message
        return redirect(url_for('main.user', username=username)) #redirect user to their profile
    else:
        return redirect(url_for('main.index')) #if submission cant be validated redirect user to home page

@bp.route("/about")
def about():
    return render_template('about.html')

@bp.route("/close_account/<username>", methods=['POST'])    
@login_required
def close_account(username):
    form = CloseAccountForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user == current_user:
            db.session.delete(current_user) 
            posts = Post.query.filter_by(user_id=None).all() #gets all posts by users who closed their accounts
            for p in posts:
                db.session.delete(p) #deletes posts by users who closed their accounts
            db.session.commit()
            flash(_('Your account has been permanently closed.'))
            return redirect(url_for('auth.login'))
        else:
            flash(_('You can only close your own account.'))
            return redirect(url_for('main.index'))
    else:
        flash(_('An error occured in your attempt to close your account.'))
        return redirect(url_for('main.index'))

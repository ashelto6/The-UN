from flask import render_template
from app import db
from app.errors import bp

@bp.app_errorhandler(404) #declares a custom error handler
def not_found_error(error): 
 return render_template('errors/404.html'), 404

@bp.app_errorhandler(500) #could be invoked after a database error
def internal_error(error):
 db.session.rollback() #resets the session to a clean slate to ensure everything continues to work properly in the db
 return render_template('errors/500.html'), 500


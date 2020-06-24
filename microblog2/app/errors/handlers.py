from flask import render_template, request
from app import db
from app.errors import bp
from app.api.errors import error_response as api_error_response

def wants_json_response():
 return request.accept_mimetypes['application/json'] >= \
  request.accept_mimetypes['text/html']


@bp.app_errorhandler(404) #declares a custom error handler
def not_found_error(error): 
 if wants_json_response():
  return api_error_response(404)
 return render_template('errors/404.html'), 404

@bp.app_errorhandler(500) #could be invoked after a database error
def internal_error(error):
 db.session.rollback() #resets the session to a clean slate to ensure everything continues to work properly in the db
 if wants_json_response():
  return api_error_response(500)
 return render_template('errors/500.html'), 500


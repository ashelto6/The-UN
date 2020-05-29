
import click
import os

def register(app):
  @app.cli.group()
  def translate():
    """Translation and localization commands."""
    pass

  @translate.command() 
  def update(): #defines a custom translate command to take place of the long command used to update translation files used in the cmd
    """Update all languages."""
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
      raise RuntimeError('extract command failed')
    if os.system('pybabel update -i messages.pot -d app/translations'):
      raise RuntimeError('update command failed')
    os.remove('messages.pot')

  @translate.command()
  def compile(): #defines a custom compile command to be used in the cmd
    """Compile all languages."""
    if os.system('pybabel compile -d app/translations'):
      raise RuntimeError('compile command failed')

  @translate.command()
  @click.argument('lang')
  def init(lang): #defines a custom language initialization command that takes the language to be added as an argument and uses it in the command
    """Initialize a new language."""
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
      raise RuntimeError('extract command failed')
    if os.system('pybabel init -i messages.pot -d app/translations -l ' + lang):
      raise RuntimeError('init command failed')
    os.remove('messages.pot')
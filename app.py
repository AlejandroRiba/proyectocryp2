from flask import redirect, render_template, request, session
from models.Database import getDatabase
from init import getApp
import os


from routes.login import login_blueprint
from routes.users import users_blueprint
from routes.reports import reports_blueprint
from routes.products import products_blueprint
from routes.clients_transactions import clients_transactions_blueprint

app = getApp()
 
app.register_blueprint(login_blueprint)
app.register_blueprint(users_blueprint)
app.register_blueprint(reports_blueprint)
app.register_blueprint(products_blueprint)
app.register_blueprint(clients_transactions_blueprint)


EXCLUDE_ROUTES = []
with app.test_request_context():
    EXCLUDE_ROUTES = [
        rule.rule
        for rule in app.url_map.iter_rules()
        if rule.endpoint.startswith('login')
    ]

EXCLUDE_ROUTES.append('/')

# Filtro para verificar que hay una sesión activa antes de resolver una petición
@app.before_request
def before_request():
    # Servir correctamente los archivos estaticos
    if request.path.startswith('/static'):
        return
    
    # Verificar si el usuario está logueado
    if (request.path not in EXCLUDE_ROUTES) and (not 'username' in session):
        return redirect('/login_route')

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.route("/")
def home():
    # Verificar si el usuario está logueado
    if 'username' in session:
        username = session['username']
    else:
        username = None
    return render_template("index.html", status=username)

if __name__ == "__main__":
    app.run(debug=False)
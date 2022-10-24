import os
from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from supabase import create_client as sb_create_client, Client as sb_client
from config import Config as Credentials

# Get credentials from config
credentials = Credentials()
public = credentials.get ("supabase_public")
secret = credentials.get ("supabase_secret")
project_url = credentials.get ("supabase_project_url")

# Conncect to Supabase
supabase: sb_client = sb_create_client(project_url, secret)

def home(request):
    context = {"current_page": "home"}
    return context

def signup(request):
    context = {"current_page": "signup"}
    return context

def login(request):
    context = {"current_page": "login"}
    return context

# Setup and start app
if __name__ == '__main__':
    with Configurator() as config:
        
        config.include("pyramid_jinja2")
        config.add_jinja2_renderer(".html")
        config.add_jinja2_search_path("./templates", name=".html")
        
        # routes
        config.add_route('home', '/')
        config.add_route('signup', '/signup')
        config.add_route('login', '/login')
        
        # views
        config.add_view(home, route_name='home', renderer="home.html")
        config.add_view(signup, route_name='signup', renderer="signup.html")
        config.add_view(login, route_name='login', renderer="login.html")
        
        # Setup wsgi
        app = config.make_wsgi_app()
        
    # Run
    host = "0.0.0.0"
    port = 6543
    print (f"Running app, open at: http://localhost:{port}/")
    make_server(host=host, port=port, app=app).serve_forever()

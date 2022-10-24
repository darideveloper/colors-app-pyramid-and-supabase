import os
import mimetypes
from unicodedata import name
from wsgiref.simple_server import make_server
from psutil import users
from pyramid.config import Configurator
from pyramid.response import Response
from supabase import create_client as sb_create_client, Client as sb_client
from config import Config as Credentials
from pyramid.httpexceptions import HTTPFound

# Get credentials from config
credentials = Credentials()
public = credentials.get ("supabase_public")
secret = credentials.get ("supabase_secret")
project_url = credentials.get ("supabase_project_url")

# Conncect to Supabase
supabase: sb_client = sb_create_client(project_url, secret)

def home(request):
    # Home page with users data
    context = {
        "current_page": "Home",
        "error": "",
        "message": "",
    }
    return context

def signup(request):
    # Sign up page with email, google and discord
    
    # Get ikmages path
    context = {
        "current_page": "Signup",
        "error": "",
        "message": "",
    }
    
    # Get form data in post
    if request.method == 'POST':
        email = request.params["email"]
        password = request.params["password"]
        
        # Validateif the user email already exist
        users = supabase.auth.api.list_users ()
        users_found = list(filter (lambda user: user.email == email, list(users)))
        users_found_num = len(users_found)
        
        # Show error if user exist
        if users_found_num == 1:
            context["error"] = f"The user '{email}' already exist"
        
        # Register new user with email
        elif users_found_num == 0:
            user = supabase.auth.sign_up (email=email, password=password)
            context["message"] = f"Done. Check your inbox to verity your email"
            
            
        
    
    return context

def login(request):
    # Login page with email, google and discord
    
    context = {
        "current_page": "Login",
        "error": "",
        "message": "",
    }
    return context

def successful(request):
    # Confiroation page after signups
    
    context = {
        "current_page": "email-done",
        "error": "",
        "message": "",
    }
    return context

def signup_google(request):
    # Redirect to page to wign up with google
    
    # Generate sign up page
    signin_link = supabase.auth.sign_in (provider="google")
    
    # Redirect
    return HTTPFound(location=signin_link)

def signup_github(request):
    # Redirect to page to wign up with google
    
    # Generate sign up page
    signin_link = supabase.auth.sign_in (provider="github")
    
    # Redirect
    return HTTPFound(location=signin_link)

# Setup and start app
if __name__ == '__main__':
    with Configurator() as config:
        
        # Templates and static seetings
        config.include("pyramid_jinja2")
        config.add_jinja2_renderer(".html")
        config.add_jinja2_search_path("./templates", name=".html")
        
        # routes
        config.add_route('home', '/')
        config.add_route('signup', '/signup')
        config.add_route('login', '/login')
        config.add_route('successful', '/successful')
        config.add_route('signup_google', '/signup/google')
        config.add_route('signup_github', '/signup/github')
        
        # views
        config.add_view(home, route_name='home', renderer="home.html")
        config.add_view(signup, route_name='signup', renderer="signup.html")
        config.add_view(login, route_name='login', renderer="login.html")
        config.add_view(successful, route_name='successful', renderer="successful.html")
        config.add_view(signup_google, route_name='signup_google')
        config.add_view(signup_github, route_name='signup_github')
        
        # Setup wsgi
        app = config.make_wsgi_app()
        
    # Run
    host = "0.0.0.0"
    port = 3000
    print (f"Running app, open at: http://localhost:{port}/")
    make_server(host=host, port=port, app=app).serve_forever()

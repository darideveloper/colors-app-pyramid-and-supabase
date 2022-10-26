from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from supabase import create_client as sb_create_client, Client as sb_client
from config import Config as Credentials
from pyramid.httpexceptions import HTTPFound
from pyramid.session import SignedCookieSessionFactory
from tools import get_session_user, set_session_user

# Get credentials from config
credentials = Credentials()
public = credentials.get ("supabase_public")
secret = credentials.get ("supabase_secret")
project_url = credentials.get ("supabase_project_url")

# Conncect to Supabase
supabase: sb_client = sb_create_client(project_url, secret)

# Setup pyramit sessions
session_factory = SignedCookieSessionFactory('my secret key 123')


def home(request):      
    # Home page with users data
    
    user = get_session_user(request)
    
    context = {
        "current_page": "Home",
        "error": "",
        "message": "",
        "user": user,
    }
    return context

def signup(request):
    # Sign up page with email, google and discord
    
    user = get_session_user(request)
    
    # Get ikmages path
    context = {
        "current_page": "Signup",
        "error": "",
        "message": "",
        "user": user,
    }
    
    if request.method == 'POST':
        # Get form data in post
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
    
    user = get_session_user(request)
     
    context = {
        "current_page": "Login",
        "error": "",
        "message": "",
        "user": user,
    }
    
    if request.method == 'POST':
        
        # Check for email token
        valid_login = False
        if "token_email" in request.params:
            # Save user in session
            set_session_user (request, request.params["token_email"])
            
            valid_login = True
        else:
                    
            # Get form data in post
            email = request.params["email"]
            password = request.params["password"]
            
            # Try to login with credentials
            user = None
            try:
                response = supabase.auth.sign_in (email=email, password=password)
            except:
                pass
            else:
                # Save user in session
                user = response.user.email
                set_session_user (request, user)
                
            if user:
                valid_login = True
            else: 
                # Show login error
                context["error"] = "Invalid user or password"
                
        # Redirect to home if login is valid
        if valid_login:
            return HTTPFound(location="/")
    
    return context

def successful(request):
    # Confiroation page after signups
    
    user = get_session_user(request)
    
    context = {
        "current_page": "email-done",
        "error": "",
        "message": "",
        "user": user,
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
        
        # App settings
        config.include("pyramid_jinja2")
        config.add_jinja2_renderer(".html")
        config.add_jinja2_search_path("./templates", name=".html")        
        config.set_session_factory(session_factory)
        
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

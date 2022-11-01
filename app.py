from webbrowser import get
import requests
from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from supabase import create_client as sb_create_client, Client as sb_client
from config import Config as Credentials
from pyramid.httpexceptions import HTTPFound
from pyramid.session import SignedCookieSessionFactory
from tools import get_session_user, set_session_user, delete_session, get_session_token, set_session_token, get_email_token

# Get credentials from config
credentials = Credentials()
public = credentials.get ("supabase_public")
secret = credentials.get ("supabase_secret")
project_url = credentials.get ("supabase_project_url")

# Conncect to Supabase
supabase: sb_client = sb_create_client(project_url, secret)

# Setup pyramit sessions
session_factory = SignedCookieSessionFactory('my secret key 123')

# Run server and port
host = "localhost"
port = 3000


def home(request):      
    # Home page with users data
        
    user = get_session_user(request)
    
    context = {
        "current_page": "Home",
        "error": "",
        "message": "",
        "user": user,
    }
    
    data_user = supabase.from_("colors").select("*").eq("email", user).execute().data
    if data_user:
        context["user_found"] = data_user[0]["email"]
    else:
        context["user_found"] = ""
    
    # Request colors from supabase
    colors = supabase.from_("colors").select("*").execute()
    context["colors"] = colors.data
        
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
    
    # Redirect to home if user is logged
    if request.method == 'GET':
        if user:
            return HTTPFound(location="/")
    
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
    
    # Redirect to home if user is logged
    if request.method == 'GET':
        if user:
            return HTTPFound(location="/")
    
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

def logout(request):
    # Rewrite cookie
    delete_session (request)
    
    # Go to login page
    return HTTPFound(location="/login")

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

def successful_token (request):
    
    # Get token after user login with google ot github
    token = request.matchdict.get ("token")
    
    # Get email token and save as a cookie
    email_token = get_email_token (token)
    set_session_user (request, email_token)
    
    return HTTPFound(location="/")


def reset_password(request):
    
    user = get_session_user(request)
    
    context = {
        "current_page": "email-done",
        "error": "",
        "message": "",
        "user": user,
    }
    
    # Redirect to home if user is logged
    if request.method == 'GET':
        if user:
            return HTTPFound(location="/")
    
    if request.method == 'POST':
        # Submit recovery email
        email = request.params["email"]
        supabase.auth.api.reset_password_for_email (email=email, redirect_to=f"http://{host}:{port}/new-password")
        
        # Show confirmation message
        context["message"] = "Email send. Check your inbox to reset your password"
        
    
    return context

def new_password(request):
    
    user = get_session_user(request)
    token = get_session_token(request)
    
    context = {
        "current_page": "email-done",
        "error": "",
        "message": "",
        "user": user,
    }
    
    if request.method == 'POST':
        
        # Get token from session
        token = get_session_token(request)
                    
        if "password" in request.params and token:
            
            # Update password with supabase api
            headers = {
                "apikey": secret,
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            data = {
                "password": request.params["password"],
            }
            res = requests.put (f'{project_url}/auth/v1/user', headers=headers, json=data)
    
            # Confirmation or error message
            if res.status_code == 200:
                context["message"] = "Password updated."
            else: 
                context["error"] = "Something was wrong, try again later"
                
            
            # Delete user reset
            delete_session(request)
    
    return context

def new_password_token (request):
    
    # Get token for password recovery
    token = request.matchdict.get ("token")
    
    # Save token in session
    set_session_token (request, f"token={token}")
    
    return HTTPFound(location="/new-password")


def signup_google(request):
    # Redirect to page to wign up with google
    
    # Redirect to home if user is logged
    user = get_session_user(request)
    if request.method == 'GET':
        if user:
            return HTTPFound(location="/")
    
    # Generate sign up page
    signin_link = supabase.auth.sign_in (provider="google")
    
    # Redirect
    return HTTPFound(location=signin_link)

def signup_github(request):
    # Redirect to page to wign up with github
    
    # Redirect to home if user is logged
    user = get_session_user(request)
    if request.method == 'GET':
        if user:
            return HTTPFound(location="/")
    
    # Generate sign up page
    signin_link = supabase.auth.sign_in (provider="github")
    
    # Redirect
    return HTTPFound(location=signin_link)

def profile(request):      
    # Home page with users data
    
    user = get_session_user(request)
    
    context = {
        "current_page": "Profile",
        "error": "",
        "message": "",
        "user": user,
        "colors": ['black', 'white', 'yellow', 'orange', 'red', 'purple', 'magenta', 'green', 'teal', 'blue']
    }
    
    if request.method == 'GET':
        if not user:
            return HTTPFound(location="/login")
    
    # Get color of the current user
    if user:
        data_user = supabase.from_("colors").select("*").eq("email", user).execute().data
        if data_user:
            color_user = data_user[0]["color"]
            context["color_user"] = color_user
        else:
            context["color_user"] = "black"
    
    if request.method == 'POST':
        # Get new color and update or insert in supabase
        color = request.params["color"]
        user_updated = supabase.from_("colors").update({"color": color}).eq("email", user).execute().data
        if not user_updated:
            supabase.from_("colors").insert ({"email": user, "color": color}).execute()
        
        # Redirect to home
        return HTTPFound(location="/")
        
    
    return context

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
        config.add_route('successful_token', '/successful/{token}')
        config.add_route('signup_google', '/signup/google')
        config.add_route('signup_github', '/signup/github')
        config.add_route('logout', '/logout')
        config.add_route('reset_password', '/reset-password')
        config.add_route('new_password', '/new-password')
        config.add_route('new_password_token', '/new-password/{token}')
        config.add_route('profile', '/profile')
        
        # views
        config.add_view(home, route_name='home', renderer="home.html")
        config.add_view(signup, route_name='signup', renderer="signup.html")
        config.add_view(login, route_name='login', renderer="login.html")
        config.add_view(successful, route_name='successful', renderer="successful.html")
        config.add_view(successful_token, route_name='successful_token', renderer="successful.html")
        config.add_view(signup_google, route_name='signup_google')
        config.add_view(signup_github, route_name='signup_github')
        config.add_view(logout, route_name='logout')
        config.add_view(reset_password, route_name='reset_password', renderer="reset_password.html")
        config.add_view(new_password, route_name='new_password', renderer="new_password.html")
        config.add_view(new_password_token, route_name='new_password_token', renderer="new_password.html")
        config.add_view(profile, route_name='profile', renderer="profile.html")
        
        # Setup wsgi
        app = config.make_wsgi_app()
        
    # Run
    print (f"Running app, open at: http://{host}:{port}/")
    make_server(host=host, port=port, app=app).serve_forever()

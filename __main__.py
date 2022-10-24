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

def hello_world(request):
    print('Incoming request')
    return Response('<body><h1>Hello World!</h1></body>')


# Setup and start app
if __name__ == '__main__':
    with Configurator() as config:
        
        # app includes
        config.include("pyramid_jinja2")
        
        # add rtoutes
        config.add_route('hello', '/')
        config.add_view(hello_world, route_name='hello')
        
        # Setup wsgi
        app = config.make_wsgi_app()
        
    # Run
    make_server(host='0.0.0.0', port=6543, app=app).serve_forever()
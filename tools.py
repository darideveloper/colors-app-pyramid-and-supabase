def get_session_user (request):
    
    # read cookies for check if user is logged
    user = ""
    session = request.session
    if "email" in session:
        user = session["email"] 
        
    return user

def set_session_user (request, email:str):
    
    # set cookies for user logged
    session = request.session
    session["email"] = email
    
def delete_session (request): 
    
    # delete cookies for user logged
    session = request.session
    session.invalidate()
    
def get_session_token (request):
    
    # read cookies for check if user is logged
    user = ""
    session = request.session
    if "token" in session:
        user = session["token"] 
        
    return user

def set_session_token (request, token:str):
    
    # Clen token    
    token_start = token.find ("=") +1
    token_end = token.find ("&")
    token = token[token_start:token_end]
    
    # set cookies for user logged
    session = request.session
    session["token"] = token
    
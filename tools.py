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
    
def delete_session_user (request): 
    
    # delete cookies for user logged
    session = request.session
    session.invalidate()
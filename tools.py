def get_session_user (request):
    
    # read cookies for check if user is logged
    user = ""
    session = request.session
    if "email" in session:
        user = session["email"] 
        
    return user  
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from auth import handle_login, handle_logout, handle_registration, get_authenticated_user


templates = Jinja2Templates(directory="templates")
app = FastAPI()


# Login page
@app.get("/login", response_class=HTMLResponse)
async def show_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# Login
@app.post("/login")
async def login(email: str = Form(...), password: str = Form(...)):
    session_id = handle_login(email, password)
    response = RedirectResponse(url="/secure", status_code=302)
    response.set_cookie(key="session_id", value=session_id, httponly=True, secure=False)
    return response


# Regist page
@app.get("/register", response_class=HTMLResponse)
async def show_registration_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Registration 
@app.post("/register")
async def register(name: str = Form(...), email: str = Form(...), password: str = Form(...)):
    handle_registration(name, email, password)  # Handle registration
    return RedirectResponse(url="/login", status_code=302)


# Secure page
@app.get("/secure", response_class=HTMLResponse)
async def show_secure_page(request: Request, user=Depends(get_authenticated_user)):
    return templates.TemplateResponse("secure.html", {"request": request, "user": user})


# Logout
@app.get("/logout")
async def logout(request: Request):
    return handle_logout(request)

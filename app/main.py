import uuid

from fastapi import Cookie, FastAPI, Form, Request, Response, templating, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from jose import jwt

from .flowers_repository import Flower, FlowersRepository
from .purchases_repository import Purchase, PurchasesRepository
from .users_repository import User, UsersRepository

IMAGEDIR = 'static'

app = FastAPI()
templates = templating.Jinja2Templates("templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

flowers_repository = FlowersRepository()
purchases_repository = PurchasesRepository()
users_repository = UsersRepository()


def encode_jwt(user_id: int):
    body = {"user_id": user_id}
    token = jwt.encode(body, "flower", algorithm='HS256')
    return token


def decode_jwt(token: str):
    data = jwt.decode(token, "flower", 'HS256')
    return data["user_id"]


@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/base")
def base(request: Request, token: str = Cookie()):
    user = users_repository.is_authenticated(decode_jwt(token))
    return templates.TemplateResponse("base.html", {"request": request, "user": user})


@app.get("/signup")
def get_signup(request: Request):
    return templates.TemplateResponse("authorization/signup.html", {"request": request})


@app.post("/signup")
def post_signup(request: Request,
                email: str = Form(...),
                name: str = Form(...),
                lastname: str = Form(...),
                password: str = Form(...)):
    user = User(email=email, name=name, lastname=lastname, password=password, profile_photo="")
    if users_repository.email_exists(user.email):
        error_message = "Email already exists."
        return templates.TemplateResponse("authorization/signup.html",
                                          {"request": request, "error_message": error_message})
    if len(password) < 8:
        error_message = "len(password)>=8"
        return templates.TemplateResponse("authorization/signup.html",
                                          {"request": request, "error_message": error_message})
    users_repository.save_user(user)
    return RedirectResponse("/login", status_code=303)


@app.get("/login")
def get_login(request: Request):
    return templates.TemplateResponse("authorization/login.html", {"request": request})


@app.post("/login")
def post_login(request: Request,
               email: str = Form(...),
               password: str = Form(...)):
    user = users_repository.get_user_by_email(email)
    if user is None or user.password != password:
        error_message = "No user with such email or incorrect password"
        return templates.TemplateResponse("authorization/login.html",
                                          {"request": request, "error_message": error_message})
    response = RedirectResponse("/profile", status_code=303)
    token = encode_jwt(user.id)
    response.set_cookie("token", token)
    return response


@app.get("/profile")
def get_profile(request: Request, token: str = Cookie()):
    user_id = decode_jwt(token)
    user = users_repository.get_user_by_id(int(user_id))
    return templates.TemplateResponse("authorization/profile.html", {"request": request, "user": user})


@app.get("/profile/edit")
def get_edit(request: Request, token=Cookie()):
    user = users_repository.get_user_by_id(decode_jwt(token))
    return templates.TemplateResponse("authorization/edit.html", {"request": request, "user": user})


@app.post("/profile/edit")
async def update_profile(request: Request,
                         profile_photo: UploadFile = File(...),
                         name: str = Form(...),
                         lastname: str = Form(...),
                         password: str = Form(...),
                         token: str = Cookie()) -> Response:
    user_id = decode_jwt(token)
    user = User(email='', name=name, lastname=lastname, password=password, profile_photo='')
    if profile_photo is not None:
        profile_photo.filename = f"{uuid.uuid4()}.jpg"
        contents = await profile_photo.read()
        with open(f"{IMAGEDIR}/{profile_photo.filename}", "wb") as f:
            f.write(contents)
        user.profile_photo = f"{profile_photo.filename}"
        print(f"{profile_photo.filename}")
    if len(password) < 8:
        error_message = "Password must be at least 8 characters long."
        return templates.TemplateResponse("authorization/edit.html",
                                          {"request": request, "error_message": error_message})

    users_repository.update_profile(user_id, user)
    return RedirectResponse("/profile", status_code=303)

@app.get("/flowers")
def get_flowers(request:Request):
    return templates.TemplateResponse("flowers/flowers.html",{"request":request})

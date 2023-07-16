import json
import uuid

from fastapi import Cookie, FastAPI, Form, Request, Response, templating, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from jose import jwt

from .flowers_repository import Flower, FlowersRepository
from .purchases_repository import Purchase, PurchasesRepository
from .users_repository import User, UsersRepository

IMAGEDIR = 'static'
current_user_id = None

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
    print(303)
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
    global current_user_id
    current_user_id = user.id
    print(current_user_id)
    response = RedirectResponse("/profile", status_code=303)
    token = encode_jwt(user.id)
    response.set_cookie("token", token)
    return response


@app.get("/profile")
def get_profile(request: Request, token: str = Cookie()):
    user_id = decode_jwt(token)
    if current_user_id:
        user = users_repository.get_user_by_id(int(user_id))
        return templates.TemplateResponse("authorization/profile.html", {"request": request, "user": user})
    else:
        return RedirectResponse("/login", status_code=303)


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
                         token: str = Cookie()):
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
def get_flowers(request: Request, page: int = 1):
    flowers = flowers_repository.get_all_flowers()
    return templates.TemplateResponse("flowers/flowers.html",
                                      {"request": request, "flowers": flowers})


@app.get('/flowers/new')
def add_flower(request: Request):
    return templates.TemplateResponse("flowers/new.html", {"request": request})


@app.post('/flowers')
def add_flower(request: Request, name: str = Form(...), count: int = Form(...), cost: int = Form(...)):
    flowers_repository.save(Flower(name=name, count=count, cost=cost))
    return RedirectResponse("/flowers", status_code=303)


@app.post('/{flower_id}/delete')
def delete_flower(request: Request, flower_id: int):
    flowers_repository.delete_flower(flower_id)
    return RedirectResponse("/flowers", status_code=303)


@app.post('/{flower_id}/delete')
def delete_flower(request: Request, flower_id: int):
    flowers_repository.delete_flower(flower_id)
    return RedirectResponse("/flowers", status_code=303)


@app.post('/add/{flower_id}/to/cart')
def add_to_cart(flower_id: int, token: str = Cookie(default=encode_jwt(current_user_id)),
                cart: str = Cookie(default="[]")):
    flower = flowers_repository.get_one(flower_id)

    if not flower:
        error_message = "Not flower with such name"
        return templates.TemplateResponse("flowers/flowers.html", {"error_message": error_message})
    if current_user_id:

        cart_json = json.loads(cart)
        cart_json.append(flower.id)
        new_cart = json.dumps(cart_json)

        response = RedirectResponse("/cart/items")
        response.set_cookie(token, new_cart)
        users_repository.save_cart(user_id=current_user_id, cart=new_cart)
        return response

    else:
        return RedirectResponse("/login", status_code=303)


@app.post('/cart/items')
def add_to_cart(flower_id: int = Form(), token: str = Cookie(default=encode_jwt(current_user_id)),
                cart: str = Cookie(default="[]")):
    flower = flowers_repository.get_one(flower_id)
    cart_json = json.loads(cart)
    cart_json.append(flower.id)
    new_cart = json.dumps(cart_json)

    response = RedirectResponse("/cart/items",status_code=303)
    response.set_cookie(token, new_cart)
    return response


@app.get('/cart/items')
def get_cart_items(request: Request, token: str = Cookie(default=encode_jwt(current_user_id))):
    if users_repository.get_user_by_id(decode_jwt(token)):
        flowers_id = request.cookies.get(token)
        total_cost = 0
        flowers = flowers_repository.get_many(flowers_id)
        if flowers:
            for i in flowers:
                total_cost += i.cost
            return templates.TemplateResponse("flowers/cart.html",
                                              {"request": request, "flowers": flowers, "total_cost": total_cost})
        else:
            return templates.TemplateResponse("flowers/cart.html",
                                              {"request": request})

    else:
        return RedirectResponse("/login", status_code=303)



import requests


def test_cart():
    session = requests.session()

    data = {"flower_id": 1}
    response = session.post("http://localhost:8000/cart/items", data=data)
    print(response.text)
    response = session.get("http://localhost:8000/cart/items", data=data)
    print(response.text)

    assert "1" in response.text

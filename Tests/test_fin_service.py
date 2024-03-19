import pytest
from fin_service import app, calculate_next_month, InputData
from fastapi.testclient import TestClient
from pydantic import ValidationError


client = TestClient(app)

def test_calculate_success():
    # Дополнительные проверки на содержимое ответа
    response = client.post("/calculate/", json={
        "date": "01.01.2024",
        "periods": 12,
        "amount": 10000,
        "rate": 5.0
    })
    assert response.status_code == 200


def test_calculate_invalid_data():
    # Проверка на содержимое ответа с ошибкой
    response = client.post("/calculate/", json={
        "date": "invalid_date",
        "periods": 12,
        "amount": 10000,
        "rate": 5.0
    })
    assert response.status_code == 400
    

def test_input_data_model():
    try:
        InputData(date="01.01.2024", periods=12, amount=10000, rate=5.0)
    except ValidationError:
        pytest.fail("Model validation failed unexpectedly")


def test_calculate_next_month():
    current_date = "01.01.2024"
    next_date = calculate_next_month(current_date)
    assert next_date == "01.02.2024"


def test_calculate_with_invalid_date():
    # проверка на вхожждение исходной даты в диапозон
    response = client.post("/calculate/", json={
        "date": "invalid_date",
        "periods": 12,
        "amount": 10000,
        "rate": 5.0
    })
    assert response.status_code == 400
    assert any("date" in error["error"] for error in response.json())


def test_calculate_with_invalid_periods():
    # проверка на вхожждение количества периодов в диапозон
    response = client.post("/calculate/", json={
        "date": "01.01.2024",
        "periods": 61,
        "amount": 10000,
        "rate": 5.0
    })
    assert response.status_code == 400
    assert any("periods" in error["error"] for error in response.json())

def test_calculate_with_invalid_amount():
    # проверка на диапозон суммы
    response = client.post("/calculate/", json={
        "date": "01.01.2024",
        "periods": 12,
        "amount": 2999,
        "rate": 5.0
    })
    assert response.status_code == 400
    assert any("amount" in error["error"] for error in response.json())


def test_calculate_with_invalid_rate():
    # проверка на диапозон ставки
    response = client.post("/calculate/", json={
        "date": "01.01.2024",
        "periods": 12,
        "amount": 10000,
        "rate": 9.0
    })
    assert response.status_code == 400
    assert any("rate" in error["error"] for error in response.json())

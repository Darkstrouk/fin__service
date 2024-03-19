from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pydantic import BaseModel, Field

app = FastAPI()

class InputData(BaseModel):
    date: str = Field(..., pattern=r'\d{2}\.\d{2}\.\d{4}', description="Дата заявки в формате dd.mm.YYYY")
    periods: int = Field(..., ge=1, le=60, description="Количество месяцев по вкладу (от 1 до 60)")
    amount: int = Field(..., ge=10000, le=3000000, description="Сумма вклада (от 10000 до 3000000)")
    rate: float = Field(..., ge=1, le=8, description="Процент по вкладу (от 1 до 8)")

class OutputData(BaseModel):
    date: str
    amount: float

def calculate_next_month(current_date):
    current_date = datetime.strptime(current_date, '%d.%m.%Y')
    next_date = current_date + relativedelta(months=1)
    return next_date.strftime('%d.%m.%Y')

@app.post("/calculate/")
async def calculate(data: InputData):
    result = {}
    current_date = data.date
    amount = data.amount
    rate = data.rate

    for i in range(data.periods):
        result[current_date] = round(amount, 2)
        amount += amount * rate / 12 / 100
        current_date = calculate_next_month(current_date)

    return result

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    response = []
    for error in errors:
        # Создаем человекочитаемое описание ошибки
        error_message = f"{error['loc'][1]} {error['msg']}"
        response.append({"error": error_message})
    return JSONResponse(content=response, status_code=400)

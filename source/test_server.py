import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route
import httpx
import json


async def init(req: Request) -> Response:
    print(dict(await req.json()))
    data: json = json.dumps(
        {
            "Success": "true",
            "ErrorCode": "0",
            "TerminalKey": "TinkoffBankTest",
            "Status": "NEW",
            "PaymentId": "13660",
            "OrderId": "21050",
            "Amount": 100000,
            "PaymentURL": "http://localhost:8000/to_pay"
        }
    )
    return Response(data, status_code=httpx.codes.OK)


async def state(req: Request) -> Response:
    data: json = json.dumps(
        {
            "Success": "true",
            "ErrorCode": "0",
            "Message": "OK",
            "TerminalKey": "TinkoffBankTest",
            "Status": "CONFIRMED",
            "PaymentId": "2304882",
            "OrderId": "#419",
            "Amount": "1000"
        }
    )
    return Response(data, status_code=httpx.codes.OK)


async def to_pay(req: Request) -> Response:
    print("Оплачено")
    data: dict = {"Status": "CONFIRMED"}
    return Response(data, status_code=httpx.codes.OK)


routes = [
    Route("/init", init, methods=["POST", "HEAD"]),
    Route("/state", state, methods=["POST", "HEAD"]),
    Route("/to_pay", to_pay, methods=["GET"]),
]

api = Starlette(routes=routes)

if __name__ == '__main__':
    uvicorn.run(app=api, debug=True, host="localhost", port=8000)
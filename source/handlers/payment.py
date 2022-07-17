import httpx
import logging

from asyncio import sleep, run
from hashlib import sha256
from requests import post, Response, get
from typing import Union

from core import config as cfg
from core.create import bot
from database import sql_db
from localization import ru


async def create_payment_url(price: float, payment_id: int) -> str:
    payment_data: dict = {"TerminalKey": cfg.TERMINAL_KEY, "Amount": price * 100, "OrderId": payment_id}
    payment_response: Response = await get_response("post", cfg.INIT_PAYMENT_API, json_data=payment_data)
    if payment_response:
        payment_response: dict = payment_response.json()
        url: Response = await get_response("get", "https://clck.ru/--?url=" + payment_response["PaymentURL"])
        if url:
            url: str = url.text
            sql_db.update_payment_id(payment_response["PaymentId"], payment_id)
            return url
    return ""


async def check_payment_status():
    """
    Check payment status and updates it in database
    :return: Updated statuses of payments
    """
    while True:
        not_paid: list = sql_db.expire_old_payments()
        payments: list = sql_db.get_new_payments()
        for payment in payments:
            data: dict = {"PaymentId": payment[1], "TerminalKey": cfg.TERMINAL_KEY}
            # https://www.tinkoff.ru/kassa/develop/api/request-sign/
            token = sha256(f"{cfg.TERMINAL_PASSWORD}{payment[1]}{cfg.TERMINAL_PASSWORD}".encode("utf-8")).hexdigest()
            data["Token"] = token
            response: Response = await get_response("post", cfg.STATE_PAYMENT_API, json_data=data)
            status: str = response.json().get("Status", "")
            if status and status != "NEW":
                sql_db.change_payment_status(status, payment[0])
                if status == "CONFIRMED":
                    await bot.send_message(payment[2], ru.MSG_PAYMENT_CONFIRMED.format(payment[0]))
                elif status == "REJECTED":
                    await bot.send_message(payment[2], ru.ERR_NOT_PAID.format(payment[0]))
                    not_paid.append(payment[0])
        for payment in not_paid:
            adds: list = sql_db.get_paid_products(payment)
            for add in adds:
                sql_db.sum_product_count(add[1], add[0])
        await sleep(cfg.STATE_PAYMENT_RETRIES)


async def get_response(method: str, url: str, json_data: dict = None, params: dict = None) -> Union[Response, None]:
    """
    Tries to connect to any server or return empty string
    :param method: Method for connection
    :param url: Any url to connect
    :param json_data: Any additional post-request data
    :param params: Any additional get-request params
    :return: Response
    """
    for _ in range(cfg.INIT_PAYMENT_RETRIES[0]):
        try:
            if method.lower() == "post":
                response: Response = post(url, json=json_data)
            else:
                response: Response = get(url, params=params)
        except Exception as exc:
            logging.error(exc)
        else:
            if response.status_code is httpx.codes.OK.value:
                return response
            logging.warning(f"{url} ({json_data or params or '-'}): {response.status_code}")
        await sleep(cfg.INIT_PAYMENT_RETRIES[1])

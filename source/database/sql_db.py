import sqlite3 as sql

from datetime import datetime as dt, timedelta as td
from typing import List, Tuple, Union

from core.config import logging, BASE_DIR, START_SHIFT
from localization import ru

base = sql.connect(BASE_DIR / "CafeBar.db")
cur = base.cursor()


def sql_start() -> None:
    """
    Creates CafeBar database if not exists
    :return: created CafeBar database
    """
    if base:
        logging.info(ru.INF_DB_CONNECTED)
    else:
        logging.info(ru.ERR_FAILED_BD)
        raise sql.DatabaseError
    base.execute(
        "CREATE TABLE if NOT EXISTS client("
        "   user_id     INTEGER NOT NULL    UNIQUE      CHECK ( user_id BETWEEN 100000000 AND 999999999 )             ,"
        "   name        TEXT                            CHECK ( length(name) >= 1 )                                   ,"
        "   phone       INTEGER                         CHECK ( phone BETWEEN 10000000000 AND 99999999999 )           ,"
        "   email       TEXT                            CHECK ( email LIKE '%_@%_.__%' )                               "
        ")"
    )
    base.execute(
        "CREATE TABLE if NOT EXISTS product("
        "   category    TEXT    NOT NULL                CHECK ( length(category) >= 1 )                               ,"
        "   image       TEXT    NOT NULL                                                                              ,"
        "   name        TEXT    NOT NULL    UNIQUE      CHECK ( length(name) >= 1 AND length(name) <= 25)             ,"
        "   description TEXT    NOT NULL                CHECK ( length(description) BETWEEN 50 AND 500)               ,"
        "   price       REAL    NOT NULL                CHECK ( price > 0 )                                           ,"
        "   count       INTEGER NOT NULL                CHECK ( count >= 0 )                                           "
        ")"
    )
    base.execute(
        "CREATE TABLE if NOT EXISTS pre_order("
        "   product     TEXT    NOT NULL                CHECK ( length(product) >= 1 )                                ,"
        "   user_id     INTEGER NOT NULL                CHECK ( user_id BETWEEN 100000000 AND 1000000000 )            ,"
        "   count       INTEGER NOT NULL    DEFAULT 1   CHECK ( count >= 0 )                                          ,"
        "   UNIQUE(product, user_id) ON CONFLICT REPLACE                                                       "
        ")"
    )
    base.execute(
        "CREATE TABLE if NOT EXISTS payment("
        "   id          INTEGER PRIMARY KEY                                                                           ,"
        "   date_time   REAL    NOT NULL                                                                              ,"
        "   user_id     INTEGER NOT NULL                CHECK ( user_id BETWEEN 100000000 AND 1000000000 )            ,"
        "   payment_id  INTEGER             UNIQUE                                                                    ,"
        "   amount      REAL    NOT NULL                                                                              ,"
        "   status      TEXT    NOT NULL    DEFAULT 'NEW'                                                              "
        ")"
    )
    base.execute(
        "CREATE TABLE if NOT EXISTS paid_product("
        "   payment_id  INTEGER NOT NULL                CHECK ( payment_id > 0 )                                      ,"
        "   product     TEXT    NOT NULL                CHECK ( length(product) >= 1 )                                ,"
        "   price       REAL    NOT NULL                CHECK ( price > 0 )                                           ,"
        "   count       INTEGER NOT NULL    DEFAULT 1   CHECK ( count > 0 )                                            "
        ")"
    )
    base.commit()


# -------------------------------------------------------------------------------------------------------------------- #
# Get requests to client database                                                                                      #
# -------------------------------------------------------------------------------------------------------------------- #
def check_user(user_id: str) -> int:
    """
    Checks user's id in client
    :param user_id: User's id
    :return: 1 if user's id exists or 0 if not
    """
    return cur.execute("SELECT count(*) FROM client WHERE user_id == ?", (user_id,)).fetchone()[0]


def add_user(user_id) -> None:
    """
    Adds new user
    :param user_id: User telegram id
    :return: Added user
    """
    cur.execute("INSERT INTO client(user_id) VALUES (?)", (user_id,))
    base.commit()


# -------------------------------------------------------------------------------------------------------------------- #


# -------------------------------------------------------------------------------------------------------------------- #
# Get requests to preorder database                                                                               #
# -------------------------------------------------------------------------------------------------------------------- #
def get_pre_order(user_id: Union[str, int]) -> List:
    """
    Requests preorder cart objects filtered by user_id
    :param user_id: User's telegram id
    :return: User's preorder cart data with matching telegram id
    """
    return cur.execute("SELECT product, count FROM pre_order WHERE user_id == ?", (user_id,)).fetchall() or []


def check_in_pre_order(product: str, user_id: Union[str, int]) -> int:
    """
    Checks product in user's preorder cart
    :param product: Product's name
    :param user_id: User's telegram id
    :return: 1 if product is in preorder cart or 0 if not
    """
    result: Tuple = cur.execute(
        "SELECT count FROM pre_order WHERE product == ? AND user_id == ? LIMIT 1", (product, user_id)
    ).fetchone()
    return (result or (-1,))[0]


def get_ordered(product: str, user_id: Union[int, str]) -> int:
    """
    Checks dishes in preorder carts of other users
    :param product: Product's name
    :param user_id: User's telegram id
    :return: Ordered dish's count
    """
    result: int = cur.execute(
        "SELECT sum(count) FROM pre_order WHERE product == ? AND user_id != ? ORDER BY product",
        (product, user_id),
    ).fetchone()[0]
    return result or 0


def get_orders(user_id: Union[int, str]) -> List:
    """
    Collects user's orders
    :param user_id: User's telegram id
    :return: User's orders
    """
    result: List = cur.execute(
        "SELECT p.image, p.name, p.description, p.price, po.count "
        "FROM product as p INNER JOIN pre_order as po ON p.name = po.product "
        "WHERE po.count > 0 AND po.user_id == ?",
        (user_id,),
    ).fetchall()
    return result or []


def get_orders_to_pay(user_id: Union[int, str]) -> List:
    """
    Collects user's orders
    :param user_id: User's telegram id
    :return: User's orders
    """
    result: List = cur.execute(
        "SELECT p.name, p.price, po.count "
        "FROM product as p INNER JOIN pre_order as po ON p.name = po.product "
        "WHERE po.count > 0 AND po.user_id == ?",
        (user_id,),
    ).fetchall()
    return result or []
# -------------------------------------------------------------------------------------------------------------------- #


# -------------------------------------------------------------------------------------------------------------------- #
# Change requests to preorder database                                                                                #
# -------------------------------------------------------------------------------------------------------------------- #
def add_product_into_cart(product: str, user_id: Union[int, str], count: int) -> None:
    """
    Add product into the user's preorder cart
    :param product: Name of product
    :param user_id: User's telegram ID
    :param count: Product's count
    :return: Added product into the user's cart
    """
    if check_in_pre_order(product, user_id) == -1:
        cur.execute("INSERT INTO pre_order(product, user_id, count) VALUES (?,?,?)", (product, user_id, count))
        base.commit()
    else:
        update_in_cart_product_count(count, product, user_id)


def update_in_cart_product_count(count: int, product: str, user_id: Union[int, str]) -> None:
    """
    Updates product's count in the user's preorder cart
    :param count: Product's count
    :param product: Name of product
    :param user_id: User's telegram ID
    :return: Updated count of the product in the user's cart
    """
    cur.execute("UPDATE pre_order SET count = ? WHERE product == ? AND user_id == ?", (count, product, user_id))
    base.commit()


def cancel_user_orders(user_id: Union[int, str]) -> None:
    """
    Cancels all user's orders
    :param user_id: User's telegram ID
    :return: Canceled user's orders
    """
    cur.execute("UPDATE pre_order SET count = 0 WHERE user_id == ?", (user_id,))
    base.commit()


def close_orders() -> None:
    """
    Cancels all orders when shift is closing
    :return: Canceled orders
    """
    cur.execute("UPDATE pre_order SET count = 0")
    base.commit()


def change_payment_status(status: str, payment_id: int) -> None:
    """
    Changes the status to the one from the bank's response
    :param payment_id: In database payment id
    :param status: New status from bank
    :return: Updated payment status
    """
    cur.execute("UPDATE payment SET status = ? WHERE id == ?", (status, payment_id))
    base.commit()
# -------------------------------------------------------------------------------------------------------------------- #


# -------------------------------------------------------------------------------------------------------------------- #
# Get requests to product database                                                                                     #
# -------------------------------------------------------------------------------------------------------------------- #
def get_menu(category: str, count: int = 0) -> List:
    """
    Requests product objects filtered by category
    :return: Filtered menu
    """
    result: List = cur.execute(
        "SELECT image, name, description, price, count FROM product WHERE category==? AND count>?",
        (category, count),
    ).fetchall()
    return result or []


def get_product_fields() -> List:
    """
    Requests product fields
    :return: Product fields
    """
    return [name[0] for name in cur.execute("select * from product limit 1").description]


def check_product_name(name: str) -> int:
    """
    Checks product's name in product
    :param name: Product's name
    :return: 1 if product's name exists or 0 if not
    """
    return cur.execute("SELECT count(*) FROM product WHERE name == ?", (name,)).fetchone()[0]


def get_product(name: str) -> List:
    """
    Requests product object
    :param name: Object's name
    :return: Product data
    """
    return cur.execute("SELECT * FROM product WHERE name == ?", (name,)).fetchone()


def get_product_count(name: str) -> int:
    """
    Requests product object
    :param name: Object's name
    :return: Product data
    """
    return (cur.execute("SELECT count FROM product WHERE name == ?", (name,)).fetchone() or (0,))[0]


# -------------------------------------------------------------------------------------------------------------------- #


# -------------------------------------------------------------------------------------------------------------------- #
# Change requests to product database                                                                                  #
# -------------------------------------------------------------------------------------------------------------------- #
def add_product(data: dict) -> int:
    """
    Adds menu's position
    :param data: Product's data
    :return: Added new position in menu
    """
    if not check_product_name(data["name"]):
        cur.execute("INSERT INTO product VALUES (?,?,?,?,?,?)", tuple(data.values()))
        base.commit()
        return 0
    else:
        return update_product(data)


def update_product(data: dict) -> int:
    """
    Updates menu's position
    :param data: Product's data
    :return: Updated a position in menu
    """
    cur.execute(
        "UPDATE product SET category = ?, image = ?, description = ?, price = ?, count = ? WHERE name == ?",
        (data["category"], data["image"], data["description"], data["price"], data["count"], data["name"]),
    )
    base.commit()
    return 1


def update_product_count(count: int, name: str) -> None:
    """
    Updates product's count
    :param count: Product's count
    :param name: Name of product
    :return: Updated count of the position
    """
    cur.execute("UPDATE product SET count = ? WHERE name == ?", (count, name))
    base.commit()


def sum_product_count(count: int, name: str) -> None:
    """
    Sum product's count
    :param count: Product's count
    :param name: Name of product
    :return: Updated count of the position
    """
    cur.execute("UPDATE product SET count = count + ? WHERE name == ?", (count, name))
    base.commit()


def del_product(name: str) -> None:
    """
    Deletes position from menu database
    :return: Deleted position
    """
    cur.execute("DELETE FROM product WHERE name == ?", (name,))
    base.commit()


# -------------------------------------------------------------------------------------------------------------------- #

# -------------------------------------------------------------------------------------------------------------------- #
# Get requests to payment database                                                                                     #
# -------------------------------------------------------------------------------------------------------------------- #
def get_user_payments(user_id: int) -> List:
    """
    Requests payments filtered by user's tg id
    :param user_id: User tg id
    :return: Filtered payments
    """
    result: List = cur.execute(
        "SELECT id, amount, date_time, status FROM payment WHERE user_id == ?", (user_id,)
    ).fetchall()
    return result or []


def get_in_time_payments(time_start: dt = None, time_finish: dt = dt.now()) -> List:
    """
    Requests payments filtered by time
    :param time_start: Start time for searching
    :param time_finish: Finish time for searching
    :return: Filtered payments
    """
    if not time_start:
        time_start: dt = dt.now().replace(hour=START_SHIFT[0], minute=START_SHIFT[1], second=0, microsecond=0)
        time_start: dt = time_start - td(days=1) if time_start > time_finish else time_start
    result: List = cur.execute(
        "SELECT id FROM payment WHERE status == 'CONFIRMED' AND date_time BETWEEN ? AND ?",
        (time_start.timestamp(), time_finish.timestamp()),
    ).fetchall()
    return result or []


def get_payment_status(payment_id: Union[str, int]) -> str:
    """
    Requests payment status
    :param payment_id: Payment's id in database
    :return: Payment's status saved in database
    """
    return cur.execute("SELECT status FROM payment WHERE id = ?", (payment_id,)).fetchone() or ""


def get_paid_products(payment_id: Union[int, str]) -> List:
    """
    Requests paid products filtered by id
    :param payment_id: Payment's id
    :return: Filtered orders
    """
    result: List = cur.execute(
        "SELECT product, count FROM paid_product WHERE payment_id == ?", (payment_id,)
    ).fetchall()
    return result or []


def get_report(payment_ids: Tuple, in_order: bool = True) -> List:
    """
    Request report data by payment's ids
    :param payment_ids: List of payment's ids
    :param in_order: Adds in order products for a report
    :return: List of paid and pre-ordered (optional) products
    """
    if payment_ids:
        payment_filter: str = f"IN {payment_ids}" if len(payment_ids) > 1 else f"== {payment_ids[0]}"
        paid: str = f"SELECT product, count, price, 0 FROM paid_product WHERE payment_id {payment_filter}              "
        ordered: str = (
            "UNION                                                                                                     "
            "SELECT product, 0, 0, count FROM pre_order WHERE count > 0                                                "
        )
        return cur.execute(paid + ordered if in_order else paid).fetchall() or []
    else:
        return []

# -------------------------------------------------------------------------------------------------------------------- #


# -------------------------------------------------------------------------------------------------------------------- #
# Change requests to paid_product database                                                                          #
# -------------------------------------------------------------------------------------------------------------------- #
def create_payment(user_id: Union[str, int], amount: float) -> int:
    """
    Create payment object in database if not exists
    :param user_id: Payer tg id
    :param amount: Total price
    :return: ID of created or existed payment
    """
    now: dt = dt.now()
    day_start: dt = now.replace(hour=START_SHIFT[0], minute=START_SHIFT[1], second=0, microsecond=0)
    day_start: float = (day_start - td(days=1) if day_start > now else day_start).timestamp()
    exist: int = cur.execute(
        "SELECT COUNT(*) FROM payment WHERE status == 'NEW' AND user_id == ? AND date_time >= ?", (user_id, day_start)
    ).fetchone()[0]
    if not exist:
        cur.execute("INSERT INTO payment(date_time, user_id, amount) VALUES(?,?,?)", (now.timestamp(), user_id, amount))
        base.commit()
    return cur.execute(
        "SELECT id FROM payment WHERE status == 'NEW' AND user_id == ? AND date_time >= ?", (user_id, day_start)
    ).fetchone()[0]


def update_payment_id(payment_id: Union[int, str], self_id: Union[int, str]) -> None:
    """
    Update payment id in payment database
    :param self_id: Payment id in database
    :param payment_id: Payment id in bank
    :return: Updated payment id
    """
    cur.execute("UPDATE payment SET payment_id = ? WHERE id == ?", (payment_id, self_id))
    base.commit()


def make_payment_list(payment_id: int, product: str, price: float, count: int) -> None:
    """
    Makes product's list of payment
    :param payment_id: In database payment's id
    :param product: Product's name
    :param price: Product's price
    :param count: Product's order count
    :return: Added products to payment's list
    """
    cur.execute(
        "INSERT INTO paid_product(payment_id, product, price, count) VALUES(?,?,?,?)",
        (payment_id, product, price, count),
    )
    base.commit()


def get_new_payments() -> List:
    """
    Finds ids of payments with status "New"
    :return: New payment's ids
    """
    return cur.execute("SELECT id, payment_id, user_id FROM payment WHERE status == 'NEW'").fetchall() or []


def expire_old_payments() -> List:
    """
    Finds and expires old orders
    :return: Expired orders
    """
    old: float = (dt.now() - td(days=1)).timestamp()
    result: List = cur.execute("SELECT id FROM payment WHERE status == 'NEW' AND date_time < ?", (old,)).fetchall()
    cur.execute("UPDATE payment SET status='EXPIRED' WHERE status == 'NEW' AND date_time < ?", (old,))
    base.commit()
    return [payment[0] for payment in result]

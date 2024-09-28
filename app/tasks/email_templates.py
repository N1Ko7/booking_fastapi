from email.message import EmailMessage

from pydantic import EmailStr

from app.bookings.dao import BookingsDAO
from app.config import settings


def create_booking_confirmation_template(booking: dict, email_to: EmailStr):
    email = EmailMessage()
    email["Subject"] = "Подтверждение бронирования"
    email["From"] = settings.SMTP_USER
    email["To"] = email_to

    email.set_content(
        f"""
            <h1> Подтвердите бронирование </h1>
            Вы забронировали отель c {booking["date_from"]} по {booking["date_to"]}

            Цена за {booking["total_days"]} дней прибывания = {booking["total_cost"]} руб.
            """,
        subtype="html",
    )

    return email

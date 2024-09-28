from pathlib import Path

from PIL import Image

from app.tasks.celery_root import celery


@celery.task
def proces_picture(
        path: str,
):
    im_path = Path(path)
    im = Image.open(im_path)
    im_resized_1000_500 = im.resize((1000, 500))
    im_resized_200_100 = im.resize((200, 100))
    im_resized_1000_500.save(f"app/static/images/resized_1000_500_{im_path.name}")
    image_resized_200_100.save(f"app/static/images/resized_200_100_{image_path.name}")


@celery.task
def send_booking_confirmation_email(booking: dict, email_to: EmailStr):
    email_to_mock = settings.SMTP_USER
    message_content = create_booking_confirmation_template(
        booking=booking, email_to=email_to_mock
    )

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(message_content)

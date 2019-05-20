import re
from django.conf import settings
from postmarker.core import PostmarkClient

postmark = PostmarkClient(server_token=settings.POSTMARK_TOKEN)


def get_booking_successful_template(booking):
    template = (
        '<html>'
        '<body>'
        f'<strong>Hello {booking.booked_by.first_name.title()}, </strong>'
        '<p>You have successfully booked a flight with Airtech. Find below your ticket details.</p>'
        '<p>  </p>'
        '<p>  </p>'
        f'<p> <b style="font-size:15px;">Ticket Number: </b> {booking.id}</p>'
        f'<p> <b style="font-size:15px;">From: </b> {booking.origin.airport}, {booking.origin.city}, {booking.origin.country}</p>'
        f'<p> <b style="font-size:15px;">To: </b> {booking.destination.airport}, {booking.destination.city}, {booking.destination.country}</p>'
        f'<p> <b style="font-size:15px;">Travel Date: </b> {booking.travel_date}</p>'
        f'<p> <b style="font-size:15px;">Flight Name: </b> {booking.flight.name if booking.flight else ""}</p>'
        f'<p> <b style="font-size:15px;">Seat: </b> {booking.seat.seat if booking.seat else ""}, {booking.seat.class_group if booking.seat else ""}</p>'
        '</body>'
        '</html>'
    )
    return template


def get_booking_reminder_template(booking):
    template = (
        '<html>'
        '<body>'
        f'<strong>Hello {booking.booked_by.first_name.title()}, </strong>'
        f'<p>You booked a flight with us from {booking.origin.city}, {booking.origin.country} to {booking.destination.city}, {booking.destination.country}.</p>'
        f'<p>Kindly login into the platform to confirm your flight details and make sure everything is in order for your departure tomorrow, {booking.flight.departure_time if booking.flight and booking.flight.departure_time else booking.travel_date}  </p>'
        '<p>Thank you for choosing to travel with us.</p>'
        '<p>Flight Airtech </p>'
        '</body>'
        '</html>'
    )
    return template


def send_booking_successful_email(booking):
    """Sends an email with ticket information to users upon successfully booking."""
    # confirm if email belongs to andela domain before trying to send an email
    if re.search(r'@andela.com$', booking.booked_by.email) is not None:
        # email if user has an andela email
        template = str(get_booking_successful_template(booking))
        # import pdb; pdb.set_trace()
        postmark.emails.send(
            From=settings.POSTMARK_SENDER_EMAIL,
            To=str(booking.booked_by.email),
            Subject='Flight Airtech Booking successful',
            HtmlBody=template
        )


def send_booking_reminder_email(booking):
    """Sends an email to user reminding them of their flight."""
    # confirm if email belongs to andela domain before trying to send an email
    if re.search(r'@andela.com$', booking.booked_by.email) is not None:
        # email if user has an andela email
        template = str(get_booking_reminder_template(booking))
        # import pdb; pdb.set_trace()
        postmark.emails.send(
            From=settings.POSTMARK_SENDER_EMAIL,
            To=str(booking.booked_by.email),
            Subject='Flight Airtech Travel Date Reminder',
            HtmlBody=template
        )

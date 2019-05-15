import re
from django.conf import settings
from postmarker.core import PostmarkClient


def send_booking_email(booking):
    """Sends an email with ticket information to users"""
    postmark = PostmarkClient(server_token=settings.POSTMARK_TOKEN)
    # confirm if email belongs to andela domain before trying to send an email
    if re.search(r'@andela.com$', booking.booked_by.email) is not None:
        # email if user has an andela email
        postmark.emails.send(
            From=settings.POSTMARK_SENDER_EMAIL,
            To=str(booking.booked_by.email),
            Subject='Flight Ticket Notification',
            HtmlBody='<html>'
                    '<body>'
                        f'<strong>Hello {booking.booked_by.first_name}, </strong>'
                        '<p>You have successfully booked a flight with Airtech. Find below your ticket details.</p>'
                        '<p>  </p>'
                        '<p>  </p>'
                        f'<p> <b style="font-size:15px;">Ticket Number: </b> {booking.id}</p>'
                        f'<p> <b style="font-size:15px;">From: </b> {booking.origin.airport}, {booking.origin.city}, {booking.origin.country}</p>'
                        f'<p> <b style="font-size:15px;">To: </b> {booking.destination.airport}, {booking.destination.city}, {booking.destination.country}</p>'
                        f'<p> <b style="font-size:15px;">Travel Date: </b> {booking.travel_date}</p>'
                        f'<p> <b style="font-size:15px;">Flight Name: </b> {booking.flight.name}</p>'
                        f'<p> <b style="font-size:15px;">Seat: </b> {booking.seat.seat}, {booking.seat.class_group}</p>'
                    '</body>'
                    '</html>'
        )

import os
from twilio.rest import Client
from dotenv import load_dotenv

# Using a .env file to retrieve the phone numbers and tokens.
load_dotenv()

class NotificationManager:

    def __init__(self):
        self.client = Client(os.environ['TWILIO_SID'], os.environ["TWILIO_AUTH_TOKEN"])

    def send_sms(self, message_body):
        """
        Sends an SMS message through the Twilio API.
        This function takes a message body as input and uses the Twilio API to send an SMS from
        a predefined virtual number (provided by Twilio) to your own "verified" number.
        It logs the unique SID (Session ID) of the message, which can be used to
        verify that the message was sent successfully.
        Parameters:
        message_body (str): The text content of the SMS message to be sent.
        Returns:
        None
        Notes:
        - Ensure that `TWILIO_VIRTUAL_NUMBER` and `TWILIO_VERIFIED_NUMBER` are correctly set up in
        your environment (.env file) and correspond with numbers registered and verified in your
        Twilio account.
        - The Twilio client (`self.client`) should be initialized and authenticated with your
        Twilio account credentials prior to using this function when the Notification Manager gets
        initialized.
        - The Twilio virtual number is verified by sending Twilio a request within your Twilio account
         which can take several days
        """
        message = self.client.messages.create(
            from_=os.environ["TWILIO_VIRTUAL_NUMBER"],
            body=message_body,
            to=os.environ["TWILIO_SENDTO_PHONE"]
        )

    #Use the Whatsapp functionality if the SMS isn't working.
    def send_whatsapp(self, message_body):
        message = self.client.messages.create(
            from_=f'whatsapp:{os.environ["TWILIO_VIRTUAL_NUMBER"]}',
            body=message_body,
            to=f'whatsapp:{os.environ["TWILIO_SENDTO_PHONE"]}'
        )



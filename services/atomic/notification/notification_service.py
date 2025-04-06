from twilio.rest import Client
from dotenv import load_dotenv
import os


#Twilio Credentials
load_dotenv()
account_sid = os.getenv("TWILIO_ACCOUNT_ID")
auth_token = os.getenv("TWILIO_ACCOUNT_TOKEN")
twilio_number = os.getenv("TWILIO_NUMBER")  

client = Client(account_sid, auth_token)

# Receive from confirmDelivery
# Send message to volunteer informing successful dropoff.
def gen_message(userObject):
    user_name = userObject.get("volunteerName")
    phone_number = userObject.get("volunteerMobile")
    # temp_format_phone_number = unformatted_phone_number.replace(" ", "")
    # Currently hardcoded, will get Ferrell's inputs on mobile formatting.
    # phone_number = "+6590603108"

    # Send SMS via Twilio
    message = client.messages.create(
        body=f"Hello {user_name}! Dropoff successful! Thank you for delivering.",
        from_=twilio_number,
        to=phone_number
    )

# Receive from notifyVolunteers
# May be able to reuse chunk from above.
def send_volunteer_notification(message):
    try:
        volunteer_name = message.get("volunteerName")
        volunteer_mobile = message.get("volunteerMobile")

        # Placeholder for the application link
        # 6 Apr call 
        app_link = "https://www.youtube.com/c/ISHOWSPEED"
        
        # Send SMS via Twilio
        sms = client.messages.create(
            body=f"Hello {volunteer_name}! There is a new pickup available, check FoodBridge for more details.\nAccess the link here: {app_link}",
            from_=twilio_number,
            to=volunteer_mobile
        )
        print(f"SMS sent to {volunteer_name} at {volunteer_mobile}, SID: {sms.sid}")
    except Exception as e:
        print(f"Error sending volunteer notification: {e}")
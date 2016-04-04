from twilio.rest import TwilioRestClient

class Twilio(object):

    def __init__(self, account_sid, auth_token, from_phone):
        self.client = TwilioRestClient(account_sid, auth_token)
        self.from_phone = from_phone

    def send_sms(self, to_phone, message):
        sms = self.client.messages.create(to=to_phone, from_=self.from_phone,
            body=message)
        return sms

import six
from django.contrib.auth.tokens import PasswordResetTokenGenerator

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):                                   #added
        return (
            six.text_type(user.date_joined) + six.text_type(user.email) + six.text_type(user.username) +
            six.text_type(timestamp) +
            six.text_type(user.profile.verified)
        )

account_activation_token = TokenGenerator()
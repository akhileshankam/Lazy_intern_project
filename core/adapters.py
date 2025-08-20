from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import login, get_backends
from django.contrib.auth.models import User

class MySocialAccountAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
        """
        Eğer sosyal hesap ile sistemde kayıtlı bir kullanıcı varsa,
        signup formunu atlayıp direkt login yap.
        """
        if sociallogin.is_existing:
            return  # Zaten bağlı bir sosyal hesap var

        email_address = sociallogin.account.extra_data.get('email')
        if email_address:
            try:
                user = User.objects.get(email__iexact=email_address)
                # Sosyal hesabı mevcut kullanıcıya bağla
                sociallogin.connect(request, user)

                # Hangi backend ile login yapılacağını belirt
                backend = get_backends()[0].__class__.__module__ + '.' + get_backends()[0].__class__.__name__
                login(request, user, backend=backend)

            except User.DoesNotExist:
                pass  # Kullanıcı yoksa normal signup devam eder

    def is_open_for_signup(self, request, sociallogin):
        # Yeni kullanıcılar için signup formunu göster
        return True

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        if not user.username:
            user.username = data.get("email", "").split("@")[0]
        return user

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailBackend(ModelBackend):
    def authenticate(self, request, email = None, password = None, **kwargs):
        CustomUser = get_user_model()
        try:
            user = CustomUser.objects.get(email = email)
            if user.check_password(password):
                return user
        except CustomUser.DoesNotExist as e:
            print("no user")
            return None
        

# from django.contrib.auth.backends import ModelBackend

# from .models import CustomUser


# class EmailBackend(ModelBackend):
#     def authenticate(self, request, email=None, password=None, **kwargs):
#         try:
#             user = CustomUser.objects.get(email=email)
#             if user.check_password(password):
#                 return user
#         except CustomUser.DoesNotExist:
#             return
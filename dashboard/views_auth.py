from django.http import JsonResponse
from pandas import json_normalize
from .models import StartApp, UserProfile
from django.contrib.auth.models import User
from django.views import View
from django.db.models import Q
import logging
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import redirect , render , HttpResponse
from django.contrib.auth.hashers import make_password, check_password

# db_logger = logging.getLogger('db')
try:
    db_logger = logging.getLogger('django')
except Exception as err:
    print(str(err))

# @login_required(redirect_field_name=None)
class TempUsers(View):
    def get(self, request):
        username = request.GET.get("username",None)
        password = request.GET.get("password",None)
        mail = request.GET.get("email",None)
        product = request.GET.get("product",None)
        if username == None or password == None or mail == None or product == None:
            # return JsonResponse({'error':True, 'msg': "No Information Given"})
            return render(request, "dashboard/demouser.html",{"msg":"No Information Given"})
        if product == "bluetail":
            return render(request, "dashboard/demouser.html",{"msg":"Bluetail Coming soon.."})
        else:
            if User.objects.filter(Q(email=mail)).count():
                # return JsonResponse({'error':True, "msg":"Email Already Registered with us"})
                return render(request, "dashboard/demouser.html",{"msg":"Email Already Registered with us"})
            elif User.objects.filter(Q(username=username)).count():
                # return JsonResponse({'error':True, "msg":"Username Already Registered with us"})
                return render(request, "dashboard/demouser.html",{"msg":"Username Already Registered with us"})
            else:
                user = User()
                user.username = username
                user.email = mail
                # user.password = data['password']
                user.set_password(password)
                user.is_active = True          
                user.save()
                profile = UserProfile()
                profile.user = user
                profile.master_password = password
                profile.save()
                login(request, user)
                return redirect('/')
                
            # return JsonResponse({'error':True, "msg":"You have successfully registered with us, You can control all the pages for 7 days"})

class ProfileUpdate(View):
    def get(self, request):
        return render(request, 'dashboard/profile-update.html')

    def post(self, request):
        try:
            
            data = {key:value.strip() for key, value in request.POST.items()}
            img = request.FILES.get('input-img')
            User.objects.filter(username=request.user.username).update(first_name = data["input-f_name"], last_name = data["input-l_name"])
            user_info = UserProfile.objects.get(user=request.user)
            user_info.bio = data["input-bio"]
            if img:
                user_info.pic = img
            user_info.save()

            path = request.path
            return render(request, "dashboard/profile-update.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Profile Updated Successfully",'errOutput':'Profile Updated!!!'})

            
        except Exception as err:
            db_logger.exception(err)
            path = request.path
            return render(request, "dashboard/profile-update.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(err)})


class Registration(View):
    def get(self, request):
        return render(request, 'dashboard/registration.html')
    
    def post(self, request):
        try:
            data = {key:value.strip() for key, value in request.POST.items() if key != "csrfmiddlewaretoken" }
        
            if data["username"] == "" and data["yourEmail"] == "" and "@" not in data["yourEmail"] and "." not in data["yourEmail"] and data["password"] == "":
                path = request.path
                return render(request, "dashboard/registration.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"User Registration Failure",'errOutput':'Please provide all the details asked in the registrations form!!'})

            
            if User.objects.filter(Q(email=data["yourEmail"]) | Q(username=data["username"])).count():
                path = request.path
                return render(request, "dashboard/registration.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"User Registration Failure",'errOutput':'Email Id and Username provided are already registered with us!! If you can not t login then please contact the admin(Your account may have not been activated yet)'})
            
            else:
            
                user = User()
                user.username = data['username']
                user.email = data['yourEmail']
                # user.password = data['password']
                user.set_password(data['password'])
                user.first_name = data['first_name']
                user.last_name = data['last_name']
                user.is_active = False
                
                if data['role'] == 'staff':
                    user.is_staff = True
                    user.is_superuser = False
                else:
                    user.is_staff = False
                    user.is_superuser = True
                    

                user.save()

                profile = UserProfile()
                profile.user = user
                profile.master_password = data['master_password']
                profile.staff_type = "STAFF"
                profile.save()
                messages.success(request, "Thank You for registering with us. Now, wait untill your account is approved and activated by the Admin!!")
                return redirect("login_page")
                
        except Exception as err:
            db_logger.exception(err)
            path = request.path
            return render(request, "dashboard/registration.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"User Registration Failure",'errOutput':str(err)})



class ResetPassword(View):
    def get(self, request):
        return render(request, 'dashboard/reset_password.html')

    def post(self, request):
        try:
            data = {key:value.strip() for key, value in request.POST.items() if key != "csrfmiddlewaretoken" }
        
            if data["yourEmail"] == "" and "@" not in data["yourEmail"] and "." not in data["yourEmail"] and data["password"] == "" and data["masterpassword"] == "":
                path = request.path
                return render(request, "dashboard/reset_password.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"User Password Reset Failure",'errOutput':'Please provide all the details asked in the Password Reset form!!'})

            
            if User.objects.filter(email=data["yourEmail"]).count():
                user = User.objects.get(email=data["yourEmail"])
                if UserProfile.objects.filter(user=user).count():
                    curr_mp = UserProfile.objects.get(user=user).master_password
                    if (check_password(data["masterpassword"], curr_mp)):
                        user.password = data['password']
                        user.save()               
                        path = request.path
                        return render(request, "dashboard/reset_password.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Password Changed",'errOutput':'Thank You for registering with us. Now, wait untill your account is approved and activated by the Admin!!'})
                    
                    else:
                        path = request.path
                        return render(request, "dashboard/reset_password.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Password Reset Failure",'errOutput':'Master password does not match'})

                else:
                    path = request.path
                    return render(request, "dashboard/reset_password.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Password Reset Failure",'errOutput':'User Exists but I cannot find your profile!!'})
            else:
                path = request.path
                return render(request, "dashboard/reset_password.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Password Reset Failure",'errOutput':'Email Id does not exist'})
                
        except Exception as err:
            db_logger.exception(err)
            path = request.path
            return render(request, "dashboard/reset_password.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Password Reset Failure",'errOutput':str(err)})



    
class Login(View):
    def get(self, request):
        obj, created = StartApp.objects.update_or_create(id=1)
        if obj.is_start:
            return render(request, "dashboard/login.html")
        else:
            return redirect("/start")

    def post(self, request):
        try:
            
            data = {key:value.strip() for key, value in request.POST.items() if (key != "csrfmiddlewaretoken")}
            user_fields = User.objects.filter(email=data['yourEmail'])
            # print(data['yourEmail'], data['password'])
            if len(user_fields) == 1:
                user = authenticate(request, username=User.objects.get(email=data['yourEmail']).username, password=data['password'])
                # print(user)
        
                if user is not None:
                    login(request, user)
                    # request.session['uid'] = email=data['yourEmail']
                    return redirect('/')
                else:
                    path = request.path
                    return render(request, "dashboard/login.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Login Error",'errOutput':'Please check your information and try again'})
                
            else:
                path = request.path
                return render(request, "dashboard/login.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Login Error",'errOutput':'No such user found'})
        except Exception as e:
            db_logger.exception(e)
            path = request.path
            return render(request, "dashboard/login.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Login Error",'errOutput':str(e)})
    
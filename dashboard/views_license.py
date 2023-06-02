import random
from django.http import JsonResponse , HttpResponse
from django.shortcuts import render
import string
from datetime import date, datetime
from .models import License




def ActivationPage(request):
    try:
        obj = License.objects.get(status=True)
        endDate = obj.end_date
        today = datetime.now().date()
        
        delta = endDate - today
        days = delta.days
    except Exception as err:
        print(err)
        days = -1

    data = {
        "data" : days
    }
    
    return render(request, 'license/license.html' , data)



def encrypt(text):
    if not str(text).isdigit():
        return "Enter an integer"
    else:
        text = int(text)

    num1 = str(random.randrange(100 , 999))
    num2 = str(random.randrange(55555 , 99999))
    letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    str1 = ''.join(random.choices(letters, k=10))
    str2 = ''.join(random.choices(letters, k=5))

    str1 = "akus" + str1
    str2 =  str2 + "suka"

    text = str(str1 + "-" + num1 + str(text)  + num2 + "-" + str2)
    result = ""
    s = 5
   # transverse the plain text
    for i in range(len(text)):
        char = text[i]
        # Encrypt uppercase characters in plain text
        if char.isdigit():
            result += char
        elif (char == "-") :
            result += "-"
        elif (char.isupper()):
            result += chr((ord(char) + s-65) % 26 + 65)
        # Encrypt lowercase characters in plain text
        else:
            result += chr((ord(char) + s - 97) % 26 + 97)
    
    return result


def DecryptKey(request):
    text = request.GET["key"]
    #text = request
    print(text)
    result = ""
    s = -5
   # transverse the plain text
    try:
        for i in range(len(text)):
            char = text[i]

            if char.isdigit():
                result += char
            elif(char == "-"):
                result += "-"
            elif (char.isupper()):
                result += chr((ord(char) + s-65) % 26 + 65)
            # Encrypt lowercase characters in plain text
            else:
                result += chr((ord(char) + s - 97) % 26 + 97)

        print(result)
        if result[:4] != "akus" or result[-4:] != "suka":
            print("not matched")
            return JsonResponse({"error" : True, "message" : "Invalid Key" })    

        obj = License.objects.filter(status=True).update(status=False)
        duration = text.split("-")[1]
        l = len(duration) - 3 - 5
        duration = int(duration[3:3 + l])
    

        d = add_years(datetime.now() , duration)
        obj = License.objects.create(key=text , duration=duration  , status=True , end_date=d)
        obj.save() 
        return JsonResponse({"error" : False, "message" : "Successful" })

    except Exception as err:
        return JsonResponse({"error" : True, "message" : "Something went wrong: "+str(err) })

def compareDate(request):
    try:
        obj = License.objects.get(status=True)
        endDate = obj.end_date
        today = datetime.now().date()
        
        delta = endDate - today
        days = delta.days

        # 0 = visible , 1 = invisible 
        FADEOUT_VALUE = 0

        if days <= 0:
            obj.status = False
            obj.save()
            return JsonResponse({"error" : False , "expired" : True , "message" : "Expired" , "redirect" : "/license/" , "data" : FADEOUT_VALUE})

        elif days < 5:
            FADEOUT_VALUE = 0.8

        elif days < 10:
            FADEOUT_VALUE = 0.5

        elif days < 20:
            FADEOUT_VALUE = 0.2

        return JsonResponse({"error" : False , "expired" : False , "message" : str(days) + " days left" , "redirect" : "/license/" , "data" : FADEOUT_VALUE})
    except License.DoesNotExist as err:
        return JsonResponse({"error" : False , "expired" : True , "message" : "Expired" , "redirect" : "/license/"  , "data" : 1 , "messageError" : str(err)})
    except Exception as err:
        print(str(err))
        return JsonResponse({"error" : False , "expired" : False , "message" : "Seomthing went wrong, you have more than 1 active license" , "redirect" : "/license/"  , "data" : 1 , "messageError" : str(err)})
   

def add_years(d, years):
    """Return a date that's `years` years after the date (or datetime)
    object `d`. Return the same calendar date (month and day) in the
    destination year, if it exists, otherwise use the following day
    (thus changing February 29 to March 1).

    """
    try:
        return d.replace(year = d.year + years)
    except ValueError:
        return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))
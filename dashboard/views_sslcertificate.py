from OpenSSL import crypto, SSL
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator    
from django.contrib.auth.decorators import permission_required
from django.views.decorators.csrf import csrf_exempt
def cert_gen(
    emailAddress="emailAddress",
    commonName="commonName",
    countryName="NT",
    localityName="localityName",
    stateOrProvinceName="stateOrProvinceName",
    organizationName="organizationName",
    organizationUnitName="organizationUnitName",
    serialNumber=0,
    validityStartInSeconds=0,
    validityEndInSeconds=10*365*24*60*60,
    KEY_FILE = "/etc/ssl/private/nginx-selfsigned.key",
    CERT_FILE="/etc/ssl/certs/nginx-selfsigned.crt"):
    #can look at generated file using openssl:
    #openssl x509 -inform pem -in selfsigned.crt -noout -text
    # create a key pair
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 4096)
    # create a self-signed cert
    cert = crypto.X509()
    cert.get_subject().C = countryName
    cert.get_subject().ST = stateOrProvinceName
    cert.get_subject().L = localityName
    cert.get_subject().O = organizationName
    cert.get_subject().OU = organizationUnitName
    cert.get_subject().CN = commonName
    cert.get_subject().emailAddress = emailAddress
    cert.set_serial_number(serialNumber)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(validityEndInSeconds)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha512')
    with open(CERT_FILE, "wt") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode("utf-8"))
    with open(KEY_FILE, "wt") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k).decode("utf-8"))
@csrf_exempt
def generate_ssl_certificate(request):
    if not request.is_ajax():
        if not request.user.has_perm("dashbaord.view_settings"):
            return redirect("/noperm/")
        return render(request, 'dashboard/ssl_certificate.html')
    try:
        if not request.user.has_perm("dashbaord.add_settings"):
            return JsonResponse({"error" : True , "redirectError" : "noperm"})

        btnType = request.GET.get("type")
        if (btnType == "generator"):
            emailAddress = request.GET.get("email","")
            commonName = request.GET.get("commonName","")
            countryName = request.GET.get("countryName","")
            localityName = request.GET.get("localityName","")
            stateOrProvinceName = request.GET.get("stateOrProvinceName","")
            organizationName = request.GET.get("organizationName","")
            organizationUnitName = request.GET.get("organizationUnitName","")
            # print(emailAddress,commonName,countryName,localityName,stateOrProvinceName,organizationName,organizationUnitName)
            cert_gen(emailAddress, commonName, countryName, localityName, stateOrProvinceName, organizationName, organizationUnitName)
        else:
            KEY_FILE = "/etc/ssl/private/nginx-selfsigned.key"
            CERT_FILE="/etc/ssl/certs/nginx-selfsigned.crt"
            certificate = request.POST.get("certificate","")
            key = request.POST.get("key","")
            with open(CERT_FILE, "wt") as f:
                f.write(certificate)
            with open(KEY_FILE, "wt") as f:
                f.write(key)
        return JsonResponse({
            'error':False,
            'data': 'Success'
        })
    except Exception as err:
        return JsonResponse({
            'error':True,
            'data': str(err)
        })

from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib import auth
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import connections
from collections import namedtuple
from django.template import RequestContext
from django.shortcuts import render
import json
import requests
import random


def namedtuplefetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

# def my_custom_sql():
#     cursor = connections['nfv'].cursor()
#    # cursor = connection.cursor()
#
#     cursor.execute("SELECT User_Id, User_Type,First_Name FROM VNF_User")
#     results = namedtuplefetchall(cursor)
#
#     for row in results :
#         print "User Id " +str(row.User_Id)
#         print "User Type " +str(row.User_Type)
#         row = cursor.fetchone()
#     #print results[0][0]
#     #print results[0].User_Id
#
#     # data = cursor.fetchall()
#     # for row in data :
#     #     print row[0].User_Id
#     #     row = cursor.fetchone()
#
#     cursor.close()
#
#     return results


# Create your views here.

 
def login(request):
    c = {}
    c.update(csrf(request))
    
    return render_to_response('login.html', c)

def login_auth(request):

    username = request.POST.get('username','')
    password = request.POST.get('password','')

    url='http://192.168.1.18:8001/login/loginHandler/'+username+'/'+password

    # if resp.status_code!=200:
    #     raise ApiError(resp.status_code)

    resp=requests.get(url)
    item = resp.json()

    print(item['UserRole'])

    if item['UserRole']=="Developer":
        #username = {'Ram'}
        return HttpResponseRedirect('/nfv/developer')
        #return HttpResponseRedirect('/nfv/developer',{"username":username})
        #return render(request, '/nfv/developer', {"username": username},content_type="application/xhtml+xml" )
    elif item['UserRole']=="admin":
        #username = 'Ben'
        #return HttpResponseRedirect('/nfv/admin' + '?username')
        return HttpResponseRedirect('/nfv/admin')
      #  return render(request, '/nfv/admin', {"username": username},content_type="application/xhtml+xml" )
    elif item['UserRole']=="Enterprise":
        return HttpResponseRedirect('/nfv/enterprise')
    else:
        return HttpResponseRedirect('/nfv/invalid')


def CreateVNF(request):
    ip = 'http://192.168.1.18:8001'
    print("Create VNF")

    vnfName= request.POST.get('txtvnfName','')
    vnfDesc = request.POST.get('txtDescription','')
    imgLoc = request.POST.get('txtImageLocation','')
    vnfDef = request.POST.get('vnfDefinition','')
    vnfConfig = request.POST.get('Config','')
    vnfParam = request.POST.get('ParameterValuePoint','')
    if imgLoc == '':
        imgLoc = 'NA'
    # upload_api='http://192.168.1.6:8081/admin/uploadVNF/'
    #
    # imgLoc='/Users/cccuser/sample.txt'
    #
    # finalurl=upload_api+imgLoc
    #
    # print(finalurl)
    #
    # resp1= requests.get(finalurl)
    # item1=resp1.json()
    #
    # print(item1)

    path = handle_uploaded_file(request.FILES['vnfDefinition'])
    r = requests.post(ip + '/admin/toscaValidate', files={'path': open(path, 'rb')})
    obj = r.json()
    if obj['status'] != 'success':
        messages.error(request, 'Invalid (' + request.FILES['vnfDefinition'].name + ') file - Not Compliant to TOSCA Standards')
    else:
        vnfDefinitionPath = obj['path']
        vnfDefinitionName = request.FILES['vnfDefinition'].name
        path = handle_uploaded_file(request.FILES['Config'])
        r = requests.post(ip + '/admin/toscaValidate', files={'path': open(path, 'rb')})
        obj = r.json()
        if obj['status'] != 'success':
            messages.error(request, 'Invalid (' + request.FILES['Config'].name + ') file - Not Compliant to TOSCA Standards.')
        else:
            configPath = obj['path']
            configName = request.FILES['Config'].name
            path = handle_uploaded_file(request.FILES['ParameterValuePoint'])
            r = requests.post(ip + '/admin/toscaValidate', files={'path': open(path, 'rb')})
            obj = r.json()
            if obj['status'] != 'success':
                messages.error(request, 'Invalid (' + request.FILES['ParameterValuePoint'].name + ') file - Not Compliant to TOSCA Standards.')
            else:
                parameterValuePointPath = obj['path']
                parameterValuePointName = request.FILES['ParameterValuePoint'].name
                path = handle_uploaded_file(request.FILES['ImageFile'])
                r = requests.post(ip + '/admin/uploadImage', files={'path': open(path, 'rb')})
                imagePath = obj['path']
                imageName = request.FILES['ImageFile'].name
                dev_api= ip + '/developer/create/'

                url=dev_api+vnfName+'/'+vnfDesc+'/'+imgLoc+'/'+vnfDefinitionName+'/'+configName+'/'+parameterValuePointName+ '/' + vnfDefinitionPath.replace('\\', '\\\\')+'/'+configPath.replace('\\', '\\\\')+'/'+parameterValuePointPath.replace('\\', '\\\\')+'/'+imagePath

                print(url)

                resp=requests.get(url)
                item = resp.json()
                if item['CatalogId']!=None:
                    print "Success"
                    messages.error(request, 'Files Compliant with TOSCA Standards and catalog added successfully with ID:' + item['CatalogId'])
                    return HttpResponseRedirect('/nfv/developer')


    return HttpResponseRedirect('/nfv/developer')



def handle_uploaded_file(f):
    print f.name
    extension = f.name.split('.')[-1]
    filename = f.name +`random.random()` + '.' + extension
    path = 'C:\\'+ filename
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return path








# def auth_view(request):
#     username = request.POST.get('username','')
#     password = request.POST.get('password','')
#
#     cursor = connections['nfv'].cursor()
#
#     sql = "SELECT User_Id, User_Type,First_Name FROM VNF_User where User_Id ="+username+" AND Password='"+password+"'"
#     print 'sql:'+sql
#     cursor.execute(sql)
#     results = namedtuplefetchall(cursor)
#
#     for row in results :
#         if row.User_Type=="Developer":
#             role= "Developer"
#             #return HttpResponseRedirect('/nfv/developer')
#         elif row.User_Type=="admin":
#             role="admin"
#             #return HttpResponseRedirect('/nfv/admin')
#         elif row.User_Type=="Enterprise":
#             role="Enterprise"
#             #return HttpResponseRedirect('/nfv/enterprise')
#         else:
#             role="Invalid"
#             #return HttpResponseRedirect('/nfv/invalid')
#         row = cursor.fetchone()
#         cursor.close()
#         return HttpResponse(role)
#

def invalid_login(request):
    return render_to_response('Invalid.html')

def logout(request):
    auth.logout(request)
    return render_to_response('logout.html')

def developer(request):
    #return render_to_response('Developer.html', {'full_name': request.user.first_name})
    return render_to_response('Developer.html',context_instance=RequestContext(request))

def admin(request):
    #return render_to_response('Admin.html', {'full_name': request.user.first_name})
    return render_to_response('Admin.html', context_instance=RequestContext(request))

def enterprise(request):
    #return render_to_response('Enterprise.html', {'full_name': request.user.first_name})
    return render_to_response('Enterprise.html', context_instance=RequestContext(request))





        


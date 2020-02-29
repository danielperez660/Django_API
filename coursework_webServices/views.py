from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from flask_restful.representations import json
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
import json

from django.core.exceptions import *
from django.db.utils import *

from coursework_webServices.models import *


@csrf_exempt
def HandleRegisterRequest(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    username = body['Username']
    email = body['Email']
    password = body['Password']

    response = HttpResponse()
    response['Content-Type'] = 'application/text'

    try:
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        response.status_code = 200
        response.reason_phrase = 'User Created Successfully'
    except IntegrityError:
        response.status_code = 409
        response.reason_phrase = 'User Creation Failed'

    return response


@csrf_exempt
def HandleLoginRequest(request):
    is_post, bad_response = POST_req_checker(request)

    if not is_post:
        return bad_response

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    username = body['Username']
    password = body['Password']

    account_object = authenticate(username=username, password=password)
    response = HttpResponse()

    if account_object is not None:
        token = Token.objects.create(user=account_object)

        response['Content-Type'] = 'application/text'
        response.status_code = 200
        response.reason_phrase = 'Login Successful'
        response.content = token.key
    else:
        response['Content-Type'] = 'application/text'
        response.status_code = 401
        response.reason_phrase = 'Login Failed'

    return response


@csrf_exempt
def HandleLogoutRequest(request):
    is_post, bad_response = POST_req_checker(request)

    if not is_post:
        return bad_response

    response = HttpResponse()
    if not Token.objects.get(key=request.headers['Authorization']):
        response = HttpResponse()
        response['Content-Type'] = 'application/text'
        response.status_code = 401
        response.reason_phrase = 'Not Logged in'

    Token.objects.get(key=request.headers['Authorization']).delete()
    response['Content-Type'] = 'application/text'
    response.status_code = 200
    response.reason_phrase = 'Logout Successful'

    return response


# list command
def HandleListRequest(request):
    is_get, bad_response = GET_req_checker(request)

    if not is_get:
        return bad_response

    if not Token.objects.get(key=request.headers['Authorization']):
        response = HttpResponse()
        response['Content-Type'] = 'application/text'
        response.status_code = 401
        response.reason_phrase = 'Not Logged in'
        return HttpResponse(response)

    return_list = []

    for i in ModuleInstance.objects.all():
        prof_list = []

        for prof in i.professor_names.all():
            prof_list.append({"name": prof.name, "professor_code": prof.professor_code})

        item = {"module_code": i.module.module_code,
                "module_name": i.module.module_name,
                "module_semester": i.module_semester,
                "professors": prof_list,
                "academic_year": i.academic_year}

        return_list.append(item)

    payload = {"modules": return_list}

    response = HttpResponse(json.dumps(payload))
    response['Content-Type'] = 'application/json'
    response.status_code = 200
    response.reason_phrase = 'OK'

    return response


#  view command
def HandleViewRequest(request):
    is_get, bad_response = GET_req_checker(request)

    if not is_get:
        return bad_response

    if not Token.objects.get(key=request.headers['Authorization']):
        response = HttpResponse()
        response['Content-Type'] = 'application/text'
        response.status_code = 401
        response.reason_phrase = 'Not Logged in'
        return response

    return_list = []

    for i in Professor.objects.all():

        total = 0
        counter_final = 0

        try:
            for j in Rating.objects.filter(professor_code=i):
                total += j.rating
                counter_final += 1
        except ObjectDoesNotExist:
            continue

        if counter_final == 0:
            continue

        item = {"name": i.name,
                "code": i.professor_code,
                "rating": total / counter_final
                }

        return_list.append(item)

    payload = {"professors": return_list}

    response = HttpResponse(json.dumps(payload))
    response['Content-Type'] = 'application/json'
    response.status_code = 200
    response.reason_phrase = 'OK'

    return response


# average command
def HandleAverageRequest(request, code):
    is_get, bad_response = GET_req_checker(request)

    if not is_get:
        return bad_response

    if not Token.objects.get(key=request.headers['Authorization']):
        response = HttpResponse()
        response['Content-Type'] = 'application/text'
        response.status_code = 401
        response.reason_phrase = 'Not Logged in'
        return response

    response = HttpResponse()

    try:
        prof_code = code[0:3]
        mode_code = code[3:6]

        professor = Professor.objects.get(professor_code=prof_code)
        professor_rating = Rating.objects.filter(professor_code=professor)

        average = 0
        total = 0

        for i in professor_rating:
            if i.module.module.module_code == mode_code:
                average += i.rating
                total += 1

        payload = {"name": professor.name, "code": professor.professor_code, "rating": average / total}
        response = HttpResponse(json.dumps(payload))
        response['Content-Type'] = 'application/json'
        response.status_code = 200
        response.reason_phrase = 'OK'
    except ObjectDoesNotExist:
        response['Content-Type'] = 'application/text'
        response.status_code = 404
        response.reason_phrase = 'Professor not found'

    return response


@csrf_exempt
def HandleRateRequest(request):
    # TODO make sure the prof is in the module instance
    is_post, bad_response = POST_req_checker(request)

    if not is_post:
        return bad_response

    response = HttpResponse()
    response['Content-Type'] = 'application/text'
    if not Token.objects.get(key=request.headers['Authorization']):
        response.status_code = 401
        response.reason_phrase = 'Not Logged in'
        return response

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    rating = body["rating"]
    professor = body["professor"]
    module = body["module"]
    year = body["year"]
    semester = body["semester"]

    try:
        prof_object = Professor.objects.get(professor_code=professor)
        module_object = Module.objects.get(module_code=module)

        module_instance_object = ModuleInstance.objects.get(module=module_object, academic_year=year,
                                                            module_semester=semester)
        rat = Rating.objects.create(rating=rating, module=module_instance_object)
        rat.professor_code.add(prof_object)
        rat.save()

        response.status_code = 200
        response.reason_phrase = 'OK'
    except ObjectDoesNotExist:
        response.status_code = 404
        response.reason_phrase = 'Not Found'
    return response


def GET_req_checker(request):
    bad_response = HttpResponseBadRequest()
    bad_response['Content-Type'] = 'text/plain'

    if request.method != "GET":
        bad_response.content = "Only GET requests are allowed for this resource\n"
        return False, bad_response

    return True, None


def POST_req_checker(request):
    bad_response = HttpResponseBadRequest()
    bad_response['Content-Type'] = 'text/plain'

    if request.method != "POST":
        bad_response.content = "Only POST requests are allowed for this resource\n"
        return False, bad_response

    return True, None

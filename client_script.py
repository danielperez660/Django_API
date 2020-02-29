import requests
from flask_restful.representations import json
import atexit

url = "http://127.0.0.1:8000/"

list_url = "api/list/"
view_url = "api/view/"
average_url = "api/average/"
register_url = "api/register/"
login_url = "api/login/"
logout_url = "api/logout/"
rate_url = "api/rate/"

# payload = {"Username": "Test", "Password": "TEST12312!", "Email": "abc@abc.com"}

print("Professor Rating System Started")

global def_prompt
def_prompt = "Anon: "

global headers
headers = None


def login():
    username = input("Username: ")
    password = input("Password: ")

    payload = {"Username": username, "Password": password}
    response = requests.post(url + login_url, json.dumps(payload))
    content = response.content.decode("utf-8")

    if response.status_code == 401:
        print("Login Failed")
        return

    global def_prompt
    def_prompt = username + ": "

    global headers
    headers = {'Authorization': content}


def register():
    username = input("Username: ")
    password = input("Password: ")
    email = input("Email: ")

    payload = {"Username": username, "Password": password, "Email": email}

    res = requests.post(url + register_url, json.dumps(payload))

    if res.status_code is not 200:
        print("Error on registering, try again")
        return
    else:
        print("Registration successful")


def logout():
    global headers

    requests.post(url + logout_url, headers=headers)

    global def_prompt
    def_prompt = "Anon: "


def list():
    global headers

    if headers is not None:
        res = requests.get(url + list_url, headers=headers).json()["modules"]
    else:
        print("Error, you are not logged in")
        return

    header_string = "Code                                Name                                " \
                    "Year                                Semester                                Taught By\n"

    print(header_string, end="")
    print("-" * (len(header_string) + 10))

    for i in res:
        tab = "                                "
        profs = ""

        for counter, j in enumerate(i["professors"]):

            if counter != len(i["professors"]) - 1:
                profs += (j["name"] + ", " + j["professor_code"] + " AND ")
            else:
                profs += (j["name"] + ", " + j["professor_code"])

                print(
                    i["module_code"], tab[1:], i["module_name"],
                    tab[len(i["module_name"]) + 3:] + "    ", i["academic_year"],
                    tab, i["module_semester"], tab + "     ", profs)

    print("-" * (len(header_string) + 10))


def view():
    global headers

    try:
        if headers is not None:
            res = requests.get(url + view_url, headers=headers).json()["professors"]
        else:
            print("Error, you are not logged in")
            return
    except:
        print("There are no ratings yet")
        return

    for i in res:
        num = str(i["rating"]).split(".")

        if int(num[1]) > 4:
            i["rating"] = (i["rating"] - int(num[1]) / 10) + 1
        else:
            i["rating"] = (i["rating"] - int(num[1]) / 10)

        print("Rating for " + i["name"] + " (" + i["code"] + ") is", (i["rating"]))


def average(input):
    global headers

    inputs = input.split(" ")[1:]

    if headers is not None and len(inputs) == 2:
        res = requests.get(url + average_url + inputs[0] + inputs[1], headers=headers)
    else:
        print("Error, you are not logged in")
        return

    if res.status_code is not 200:
        print("Error in average request")
        return

    num = str(res.json()["rating"]).split(".")

    if int(num[1]) > 4:
        num = (res.json()["rating"] - int(num[1]) / 10) + 1
    else:
        num = (res.json()["rating"] - int(num[1]) / 10)

    print("Rating of ", res.json()["name"], "(" + res.json()["code"] + ") is ", num)


def rate(input):
    global headers

    inputs = input.split(" ")[1:]

    payload = {"rating": inputs[4], "professor": inputs[0], "module": inputs[1], "year": inputs[2],
               "semester": inputs[3]}

    if headers is not None:
        res = requests.post(url + rate_url, json.dumps(payload), headers=headers)
    else:
        print("Error, you are not logged in")
        return

    if res.status_code is not 200:
        print("Error during rating submission")
        return
    else:
        print("Rating Submitted Correctly")


atexit.register(logout)

while True:
    inp = input(def_prompt)

    if "login" in inp:
        login()
    elif "logout" in inp:
        logout()
    elif "register" in inp:
        register()
    elif "list" in inp:
        list()
    elif "view" in inp:
        view()
    elif "average" in inp:
        average(inp)
    elif "rate" in inp:
        rate(inp)
    else:
        print("Command not recognised")

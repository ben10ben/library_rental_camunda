import json


json_path = r"C:\Users\Benedikt\Documents\UiPath\Presentation\download_project\lib_db.json"

def overdue_customer_check(booklist):
    for i in booklist:
        tmp = i.split(";")
        if tmp[1] == "1":
            return (True)

def overdue_checker():
    with open(json_path) as json_file:
            db = json.load(json_file)

    output_string = ""
    
    for i in db:
        if overdue_customer_check(db[i]["booklist"]):
            output_string += db[i]["c_data"]["email"]
            output_string += ";"
   
    return output_string[:-1]
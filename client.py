import requests
import json
from urllib.parse import quote
from typing import Any
import os

try:
    import nahcrofDB_client_config
    nahcrofDB_client_config.databases
except Exception as e:
    print(f"Failure setting up enterprise usage: {e}")

DB_folder = [0]
DB_pass = [0]
URL = [0]
DB_enterprise = [False]
DB_log = [False]

# for "current" value, appropriate values are "primary" and "backup". spot is only used if using backup databases,
# the reason for "spot" is in the event of multiple database failures, the client will switch which database is in use in the backup list.
# The client will only use this client from that point forward to avoid further de-syncing the databases.
database_in_use = {"current": "primary", "spot": 0}

def init(folder: str="", url: str="", password: str="", enterprise: bool=False, console_log: bool=False) -> None:
    # store important data in globally defined lists.
    DB_enterprise[0] = enterprise
    DB_folder[0] = folder
    URL[0] = url
    DB_pass[0] = password
    DB_log[0] = console_log

def is_alive():
    url = URL[0]
    try:
        status_url = f"{url.rstrip('/')}/status"
        response = requests.get(status_url, timeout=10)
        return response.status_code == 200
    except requests.RequestException:
        return False

def getKey(key: str) -> Any:
    if not DB_enterprise[0]:
        headers = {'X-API-Key': DB_pass[0]}
        r = requests.get(url=f"{URL[0]}/v2/key/{quote(key)}/{quote(DB_folder[0])}", headers=headers).json()
        try:
            return r["value"]
        except KeyError:
            return r
    elif DB_enterprise[0]:
        if database_in_use["current"] == "primary":
            try:
                headers = {'X-API-Key': DB_pass[0]}
                r = requests.get(url=f"{URL[0]}/v2/key/{quote(key)}/{quote(DB_folder[0])}", headers=headers).json()
                try:
                    return r["value"]
                except KeyError:
                    return r
            except Exception as e:
                if not is_alive():
                    database_in_use["current"] = "backup"

        if database_in_use["current"] == "backup":
            databases = nahcrofDB_client_config.databases
            headers = {'X-API-Key': databases[database_in_use['spot']]['password']}
            r = requests.get(url=f"{databases[database_in_use['spot']]['url']}/v2/key/{quote(key)}/{quote(DB_folder[0])}", headers=headers).json()
            try:
                return r["value"]
            except KeyError:
                return r

def search(data: str) -> list[str]: # this function is trash and will likely be deprecated soon
    # search database for keys containing specified data.
    r = requests.get(url=f"{URL[0]}/search/{DB_pass[0]}/?location={quote(DB_folder[0])}&parameter={quote(data)}")
    response = r.json()
    return response["data"]

def searchNames(data: str, where=None) -> list[str]:
    # search database for keys containing specified data.
    if not DB_enterprise[0]:
        headers = {'X-API-Key': DB_pass[0]}
        if where == None:
            # not sure why I decided to use a string with the value "null" but oh well.
            where = "null"
        r = requests.get(url=f"{URL[0]}/v2/searchnames/{quote(DB_folder[0])}/?query={quote(data)}&where={quote(where)}", headers=headers)
        response = r.json()
        return response
    elif DB_enterprise[0]:
        if database_in_use["current"] == "primary":
            try:
                headers = {'X-API-Key': DB_pass[0]}
                if where == None:
                    where = "null"
                r = requests.get(url=f"{URL[0]}/v2/searchnames/{quote(DB_folder[0])}/?query={quote(data)}&where={quote(where)}", headers=headers)
                response = r.json()
                return response
            except Exception as e:
                if not is_alive():
                    database_in_use["current"] = "backup"
        if database_in_use["current"] == "backup":
            databases = nahcrofDB_client_config.databases
            database = databases[database_in_use["spot"]]
            headers = {'X-API-Key': database['password']}
            if where == None:
                where = "null"
            r = requests.get(url=f"{database['url']}/v2/searchnames/{quote(DB_folder[0])}/?query={quote(data)}&where={quote(where)}", headers=headers)
            response = r.json()
            return response

def getKeys(*keys) -> dict:
    if not DB_enterprise[0]:
        templist = []
        headers = {'X-API-Key': DB_pass[0]}
        templist.append(f"?key[]={quote(str(keys[0]))}")
        if len(keys) > 1:
            for key in keys:
                if f"?key[]={key}" in templist:
                    pass
                else:
                    templist.append(f"&key[]={quote(str(key))}")
        result = "".join(templist)
        return requests.get(url=f"{URL[0]}/v2/keys/{quote(DB_folder[0])}/{result}", headers=headers).json()
    elif DB_enterprise[0]:
        if database_in_use["current"] == "primary":
            try:
                templist = []
                headers = {'X-API-Key': DB_pass[0]}
                templist.append(f"?key[]={quote(str(keys[0]))}")
                if len(keys) > 1:
                    for key in keys:
                        if f"?key[]={key}" in templist:
                            pass
                        else:
                            templist.append(f"&key[]={quote(str(key))}")
                result = "".join(templist)
                return requests.get(url=f"{URL[0]}/v2/keys/{quote(DB_folder[0])}/{result}", headers=headers).json()
            except Exception as e:
                if not is_alive():
                    database_in_use["current"] = "backup"
        if database_in_use["current"] == "backup":
            databases = nahcrofDB_client_config.databases
            templist = []
            headers = {'X-API-Key': databases[database_in_use["spot"]]["password"]}
            templist.append(f"?key[]={quote(str(keys[0]))}")
            if len(keys) > 1:
                for key in keys:
                    if f"?key[]={key}" in templist:
                        pass
                    else:
                        templist.append(f"&key[]={quote(str(key))}")
            result = "".join(templist)
            return requests.get(url=f"{databases[database_in_use['spot']]['url']}/v2/keys/{quote(DB_folder[0])}/{result}", headers=headers).json()

def postGetKeys(keys: list) -> dict: # gets keys using post request
    if not DB_enterprise[0]:
        headers = {'X-API-Key': DB_pass[0]}
        return requests.post(url=f"{URL[0]}/v2/postgetkeys/{quote(DB_folder[0])}", headers=headers, json=keys).json()
    elif DB_enterprise[0]:
        if database_in_use["current"] == "primary":
            try:
                headers = {'X-API-Key': DB_pass[0]}
                return requests.post(url=f"{URL[0]}/v2/postgetkeys/{quote(DB_folder[0])}", headers=headers, json=keys).json()
            except Exception as e:
                if not is_alive():
                    database_in_use["current"] = "backup"
        if database_in_use["current"] == "backup":
            databases = nahcrofDB_client_config.databases
            headers = {'X-API-Key': databases[database_in_use["spot"]]["password"]}
            return requests.post(url=f"{databases[database_in_use['spot']]['url']}/v2/postgetkeys/{quote(DB_folder[0])}", headers=headers, json=keys).json()

def getKeysList(keys: list) -> dict:
    if not DB_enterprise[0]:
        templist = []
        headers = {'X-API-Key': DB_pass[0]}
        templist.append(f"?key[]={quote(str(keys[0]))}")
        if len(keys) > 1:
            for key in keys:
                if f"?key[]={key}" in templist:
                    pass
                else:
                    templist.append(f"&key[]={quote(str(key))}")
        result = "".join(templist)
        return requests.get(url=f"{URL[0]}/v2/keys/{quote(DB_folder[0])}/{result}", headers=headers).json()
    elif DB_enterprise[0]:
        if database_in_use["current"] == "primary":
            try:
                templist = []
                headers = {'X-API-Key': DB_pass[0]}
                templist.append(f"?key[]={quote(str(keys[0]))}")
                if len(keys) > 1:
                    for key in keys:
                        if f"?key[]={key}" in templist:
                            pass
                        else:
                            templist.append(f"&key[]={quote(str(key))}")
                result = "".join(templist)
                return requests.get(url=f"{URL[0]}/v2/keys/{quote(DB_folder[0])}/{result}", headers=headers).json()
            except Exception as e:
                if not is_alive():
                    database_in_use["current"] = "backup"
        if database_in_use["current"] == "backup":
            databases = nahcrofDB_client_config.databases
            templist = []
            headers = {'X-API-Key': databases[database_in_use["spot"]]["password"]}
            templist.append(f"?key[]={quote(str(keys[0]))}")
            if len(keys) > 1:
                for key in keys:
                    if f"?key[]={key}" in templist:
                        pass
                    else:
                        templist.append(f"&key[]={quote(str(key))}")
            result = "".join(templist)
            return requests.get(url=f"{databases[database_in_use['spot']]['url']}/v2/keys/{quote(DB_folder[0])}/{result}", headers=headers).json()

def getKeysIncrements(keys: list, log: bool=False, increment: int=100):
    total_keys = len(keys)
    index = [0]
    current_request = []
    final_request = {}
    actual_index = -1

    for key in keys:
        index[0] += 1
        actual_index += 1
        current_request.append(keys[actual_index])
        if log:
            print(f"found values for {actual_index}/{total_keys} keys!")
        if index[0] > 100:
            data = getKeysList(current_request)
            current_request = []
            index[0] = 0
            for key in data:
                final_request[key] = data[key]

    return final_request

def makeKey(key: str, value: Any): # returns a response, unless in enterprise mode, where it returns a list of all responses
    payload = {key: value}
    headers = {'X-API-Key': DB_pass[0]}
    if not DB_enterprise[0]:
        return requests.post(url=f"{URL[0]}/v2/keys/{quote(DB_folder[0])}/", headers=headers, json=payload)

    requests_made = []
    try:
        requests_made.append(requests.post(url=f"{URL[0]}/v2/keys/{quote(DB_folder[0])}/", headers=headers, json=payload))
    except Exception as e:
        requests_made.append(f"[ERROR MAIN] {e}")
        if DB_log[0]:
            print(f"PRIMARY DB UPDATE ERROR: {e}")
    for database in nahcrofDB_client_config.databases:
        headers = {'X-API-Key': database['password']}
        try:
            requests_made.append(requests.post(url=f"{database['url']}/v2/keys/{quote(DB_folder[0])}/", headers=headers, json=payload))
        except Exception:
            requests_made.append("[ERROR]")
    return requests_made

def makeKeys(data: dict):
    headers = {'X-API-Key': DB_pass[0]}
    if not DB_enterprise[0]:
        return requests.post(url=f"{URL[0]}/v2/keys/{quote(DB_folder[0])}/", headers=headers, json=data)

    requests_made = []
    try:
        requests_made.append(requests.post(url=f"{URL[0]}/v2/keys/{quote(DB_folder[0])}/", headers=headers, json=data))
    except Exception as e:
        requests_made.append(f"[ERROR MAIN] {e}")
        if DB_log[0]:
            print(f"PRIMARY DB UPDATE ERROR: {e}")
    for database in nahcrofDB_client_config.databases:
        headers = {'X-API-Key': database['password']}
        try:
            requests_made.append(requests.post(url=f"{database['url']}/v2/keys/{quote(DB_folder[0])}/", headers=headers, json=data))
        except Exception as e:
            requests_made.append("[ERROR]")
    return requests_made



def makekeys_test(amount: int) -> dict:
    return requests.get(url=f"{URL[0]}/test/makekeys/{quote(DB_folder[0])}/{DB_pass[0]}/{amount}").json()

def kill_db() -> None:
    try:
        requests.get(url=f"{URL[0]}/kill_db/{DB_pass[0]}/")
    except Exception as e:
        print("successfully stopped database program.")
        print(f"response (Connection Error is success): {e}")

def delKey(key: str):
    payload = [key]
    headers = {'X-API-Key': DB_pass[0]}
    if not DB_enterprise[0]:
        return requests.delete(url=f"{URL[0]}/v2/keys/{quote(DB_folder[0])}/", headers=headers, json=payload)
    requests_made = []
    try:
        requests_made.append(requests.delete(url=f"{URL[0]}/v2/keys/{quote(DB_folder[0])}/", headers=headers, json=payload))
    except Exception as e:
        requests_made.append(f"[ERROR MAIN] {e}")
        if DB_log[0]:
            print(f"PRIMARY DB UPDATE ERROR: {e}")
    for database in nahcrofDB_client_config.databases:
        headers = {'X-API-Key': database['password']}
        try:
            requests_made.append(requests.delete(url=f"{database['url']}/v2/keys/{quote(DB_folder[0])}/", headers=headers, json=payload))
        except Exception:
            requests_made.append("[ERROR]")
    return requests_made

def incrementKey(amount, *pathtokey): # does not currently support enterprise mode
    payload = {"amount": amount}
    headers = {'X-API-Key': DB_pass[0]}
    templist = []
    for value in pathtokey:
        templist.append(f"{value}/")
    finalpath = "".join(templist)
    return requests.post(url=f"{URL[0]}/v2/increment/{quote(DB_folder[0])}/{finalpath}", headers=headers, json=payload)

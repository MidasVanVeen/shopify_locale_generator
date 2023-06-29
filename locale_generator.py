import requests
import json
import os
import sys
from datetime import datetime

DEFAULT_LOCALE = None
locales = {}
MODE = "auto"

# @param path: The path to the directory containing the locale files
# @return: A list of all the json filenames in the directory
def gather_files(path) -> list:
    files = []
    for _filename in os.listdir(path):
        if _filename.endswith(".json"):
            files.append(_filename)
    return files


def read_locales(files):
    for filename in files:
        with open("locales/" + filename, "r") as _file:
            locales[filename] = json.load(_file)


def write_locales():
    for locale in locales:
        directory = f"out_{datetime.today().strftime('%d-%m-%Y_%H:%M:%S')}"
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(f"{directory}/{locale}", "w") as _file:
            json.dump(locales[locale], _file, indent=4)


def translate(value, locale) -> str:
    print(".", end="", flush=True)
    if locale == DEFAULT_LOCALE:
        return value
    if MODE == "manual":
        return input("Enter the translation for " + value + " in " + locale + ": ")
    if MODE == "auto":
        # use google translate api
        stripped_locale = locale.split(".")[0]
        request = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=" + DEFAULT_LOCALE + "&tl=" + stripped_locale + "&dt=t&q=" + value
        response = requests.get(request)
        if response.status_code == 200:
            return response.json()[0][0][0]
        print("Error: " + response.status_code)
        return ""


def loop():
    namespace = input("Enter a namespace: ")
    for locale in locales:
        if namespace not in locales[locale]:
            locales[locale][namespace] = {}
    while True:
        i = input("\npress 'a' to add a new entry, 'q' to quit: ")
        if i == "a":
            key = input("Enter a key: ")
            value = input("Enter a value: ")
            for locale in locales:
                locales[locale][namespace][key] = translate(value, locale)
        elif i == "q":
            break
        else:
            print("Invalid input! trying again.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if "--manual" in sys.argv:
            MODE = "manual"
    json_files = gather_files("locales")
    for f in json_files:
        if 'default' in f:
            DEFAULT_LOCALE = f
            break
    if DEFAULT_LOCALE is None:
        print("No default locale found. Please create a file called 'XX.default.json' in the locales directory.")
        sys.exit(1)
    print("Using default locale: " + DEFAULT_LOCALE)
    read_locales(json_files)
    try:
        loop()
    finally:
        write_locales()

from flask import Flask
import flask

app = Flask(__name__)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import re
from bs4 import BeautifulSoup
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier

df = pd.read_csv("./gifthub_train_revised_num.csv")
df.head()
X = df.drop("gift", axis=1)
y = df["gift"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
dtree = DecisionTreeClassifier()
dtree.fit(X_train, y_train)
predictions = dtree.predict(X_test)
svc = SVC()
svc.fit(X_train, y_train)
svcpredictions = svc.predict(X_test)
rtree = RandomForestClassifier()
rtree.fit(X_train, y_train)
rpredictions = rtree.predict(X_test)


def prepdata(data):
    term = data.strip().replace(" ", "+")
    return term


def scraper(site):
    # getting requests from url
    r = requests.get(site)
    dct = {}
    dct_lst = []

    soup = BeautifulSoup(r.text, "html.parser")
    lst = soup.findAll("div", {"class": "KZmu8e"})
    for div in lst:
        anchor = re.findall("(<a[^>]*>)", str(div.a))
        dct["link"] = anchor[0]
        dct["img"] = div.find("img")["src"]
        dct["title"] = div.find("div", {"class": "sh-np__product-title translate-content"}).text.strip()
        dct["price"] = div.find("span", {"class": "T14wmb"}).text.strip()
        anchor = dct["price"][1:].split()
        # print(anchor[0])
        dct["price_num"] = float(anchor[0].replace(",", "").split("₹")[0])
        dct["seller"] = div.find("span", {"class": "E5ocAb"}).text.strip()
        dct_lst.append(dct.copy())

    lst = soup.findAll("div", {"class": ("u30d4")})
    lst = lst[:-1]
    for div in lst:
        anchor = re.findall("(<a[^>]*>)", str(div.a))
        dct["link"] = anchor[0]
        dct["img"] = div.find("img")["src"]
        anchor = div.div.next_sibling.div.a
        dct["title"] = anchor.text.strip()
        dct["price"] = div.find("span", {"class": "HRLxBb"}).text.strip()
        anchor = dct["price"][1:].split()
        # print(anchor[0])
        dct["price_num"] = float(anchor[0].replace(",", ""))
        anchor = div.find("div", {"class": "dD8iuc"}).text.strip()
        elem = re.findall("(from.*)", anchor)
        if elem:
            dct["seller"] = elem[0]
        else:
            dct["seller"] = " "
        dct_lst.append(dct.copy())
    res_lst = [i for n, i in enumerate(dct_lst) if i not in dct_lst[n + 1 :]]
    return res_lst


def gifthub(age, gender, relation, ocassion, interest1, interest2, budget):
    user_input = [[age, gender, relation, ocassion, interest1, interest2, budget]]
    df = pd.DataFrame(
        user_input, columns=["age", "gender", "relation", "occasion", "interest_1", "interest_2", "budget"]
    )
    output = dtree.predict(df)
    output = str(output[0])
    prediction = output
    output = output.split(",")  # output list ready ex. ['Audio Sunglasses', ' Gaming Console']

    out_lst = []
    for data in output:
        data = prepdata(data)  # prepping terms from output for scraping
        site = "https://www.google.com/search?q=" + data + "&source=lnms&tbm=shop&sa=X"
        lst = scraper(site)
        out_lst = out_lst + lst

    sor_out_lst = sorted(out_lst, key=lambda i: i["price_num"])  # sorting all the scraped items
    if user_input[0][6] == 0:
        return [prediction , sor_out_lst[: len(sor_out_lst) // 3]]
    elif user_input[0][6] == 1:
        return [prediction, sor_out_lst[len(sor_out_lst) // 3 : 2 * (len(sor_out_lst) // 3)]]
    else:
        return [prediction , sor_out_lst[2 * (len(sor_out_lst) // 3) :]]


# ghout = gifthub([[1,0,0,0,0,0,0]])[0:2]
# print(ghout)


@app.route("/api", methods=["GET", "POST"])
def api():
    # this is the array I am passing from frontend
    json_data = flask.request.json
    if json_data != None:
        age = int(json_data[0])
        gender = int(json_data[1])
        relation = int(json_data[2])
        ocassion = int(json_data[3])
        interest1 = int(json_data[4])
        interest2 = int(json_data[5])
        budget = int(json_data[6])
    else:
        return "MUFFIN OP"
    print(json_data)
    ghout = gifthub(age, gender, relation, ocassion, interest1, interest2, budget)[0:2]
    
    
    # Just trying to return something
    return {
        "output": ghout
    }

if __name__ == "__main__":
    app.run(debug=True)


import requests
from PIL import Image
import requests
from io import BytesIO

def movie_recommendations(age, gender):
    url = "https://streaming-availability.p.rapidapi.com/search/basic"
    movies_list = []
    age = "0-2"
    genre = []
    if age == "0-2" or age == "4-6" or age == "8-12":
        genre = ["16"]
    elif age == "15-20":
        if gender == "Male":
            genre = ["3", "5", "18", "27", "28", "80"]
        else:#female
            genre = ["10749", "10764"]
    else: #age >20:
        if gender == "Male":
            genre = ["1", "5", "27", "28", "80", "10752", "10763", "10767"]
        else: #female
            genre = ["4", "14", "18", "35", "10749", "10751", "10764", "10763", "10767"]
    for i in range (7):
        querystring = {"country": "us", "service": "netflix", "type": "movie", "genre": genre, "page": str(i+1), "language": "en"}
        headers = {
            'x-rapidapi-host': "streaming-availability.p.rapidapi.com",
            'x-rapidapi-key': "3260009288msh34c43c4c4859d04p17059ejsnb85a34409b8e"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)
        age_split = age.split('-')
        if int(age_split[0] )>= 18:
            age_split[0] = 18
            age_split[1] = 100
        for j in response.json()["results"]:
           if int(age_split[0]) <= (j["age"]) <= int(age_split[1]):
              movies_list.append(j["posterURLs"]["original"])

    return movies_list




import json
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import hashlib
import googletrans
from googletrans import Translator
import os
from dotenv import load_dotenv
import pymongo
from translate import Translator

load_dotenv()  # load variables from the .env file
db_url = os.getenv("DB_URL")

try:
    client = pymongo.MongoClient(db_url)
    db = client["newest"]
    collection = db["recipesSlo_filip3"]
    collection2 = db["recipesEng_filip3"]
    collection3 = db["recipesHash_filip3"]
    print("Connected to MongoDB!")
except Exception as e:
    print("MongoDB connectivity issue. Exception at " + str(e))
    exit(-1)

temp = True

translator = Translator(to_lang='en', from_lang='sl')

html_text=requests.get('https://www.okusno.je/iskanje')
#print(html_text.content)
recipes = []
recipesEng=[]
soup=BeautifulSoup(html_text.content,'lxml')
try:
  recipe_divs = soup.find_all('div',class_='md:w-1/3')
except Exception as e:
        print("Cant acquire the recepies at this moment")
        exit(-1)

for recipe_div in recipe_divs:
  try:
    #link=recipe_divs.find()
    recipe_url = recipe_div.find('a')['href']
    zacetek="https://www.okusno.je"
    full_url = urljoin(zacetek,recipe_url)
    recipe_response = requests.get(full_url)
    recipe_soup = BeautifulSoup(recipe_response.content,'lxml')
    try:
      imeRecepta=recipe_soup.find('h1',class_='font-bold').text
      #print(imeRecepta)
    except AttributeError:
      continue 

    recipe_data = {
              'name': imeRecepta,
              'type': "",
              'time': 0,
              'complexity': "",
              'description': "",
              'ingredients': []
              
          }
    
    translated_name = translator.translate(imeRecepta)

    recipe_dataEnglish = {
              'name': translated_name,
              'type': "",
              'time': 0,
              'complexity': "",
              'description': "",
              'ingredients': []
              
          }

    sestavine=recipe_soup.find_all('div',class_='ingredient')

    for sestavina in sestavine:
      deliSestavine = sestavina.stripped_strings
      # Join the text parts with a space character
      obdelanaSestavina = ' '.join(deliSestavine)
      #print(obdelanaSestavina)
      recipe_data['ingredients'].append(obdelanaSestavina)

      translated_obdelanaSestavina = translator.translate(obdelanaSestavina)
      recipe_dataEnglish['ingredients'].append(translated_obdelanaSestavina)

    #ne gre parsat 
    #cas=recipe_soup.find_all('div',class_='')
    #skupenCas=cas[2].text
    #print(cas)
    desc=""
    postopki=recipe_soup.find_all('div',class_='preparation__text')
    for postopek in postopki:
      opis=postopek.text
      #print(opis)
      desc = desc + opis + "\n"
      #recipe_data['description'].append(opis.text)
    recipe_data['description']=desc
    recipes.append(recipe_data)
    collection.insert_one(recipe_data)
    print("Recipe sent, ", recipe_data['name'])

    translated_desc = translator.translate(desc)
    recipe_dataEnglish['description']=translated_desc
    recipesEng.append(recipe_dataEnglish)
    collection2.insert_one(recipe_dataEnglish)

    recipe_string = str(recipe_data)

    # Hash the recipe string using SHA-256
    hash_object = hashlib.sha256(recipe_string.encode())
    hashed_recipe = hash_object.hexdigest()
    print("Hashed Recipe:", hashed_recipe)
    collection3.insert_one({"hashed_recipe": hashed_recipe})

  except AttributeError:
     continue
#json_data = json.dumps(recipes)
#json_dataEng = json.dumps(recipesEng)


#print(json_data)
#print(json_dataEng)


#dataT = "poper"
#translated_name = translator.translate(dataT)
#print(translated_name)
#with open('C:/Users/filip\Desktop/outFile.txt', 'w') as f:
 #   print(recipe_divs, file=f)

    #print(full_url, file=f)



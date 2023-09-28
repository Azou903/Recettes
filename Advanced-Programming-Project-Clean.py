#!/usr/bin/env python
# coding: utf-8

# In[94]:


from urllib.request import urlopen

import bs4
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd 
import numpy as np
import selenium



from selenium.webdriver.chrome.options import Options# for suppressing the browser
import time
from selenium.webdriver.common.by import By
import time
import pymongo
import urllib.request


from PIL import Image
from bson.objectid import ObjectId



from PIL import Image, ImageTk


from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


import pymongo
import pickle
import copy 
import re

import nltk
import json


import pipreqs


# # Scraping le site petitchef pour extraire les recettes

# In[65]:


def extract_type_plats_liens(driver)->list():
    """
    Cette fonction permet d'extraire trois liens qui menent vers les entrée, plats, et desserts 
    """
    driver.find_elements(By.CLASS_NAME,"sd-cmp-3V2Vm")[1].find_element(By.TAG_NAME,"button").click()
    #chrome_options.add_experimental_option("detach", True)
    return [i.text for i in driver.find_element(By.CLASS_NAME,"left").find_elements(By.TAG_NAME,"a")],[i.get_attribute('href') for i in driver.find_element(By.CLASS_NAME,"left").find_elements(By.TAG_NAME,"a")]


# In[21]:


def extract_plus_de_recettes(driver,recipes_per_country)->list():
    """
    Cette fonction permet d'extraire plus de recettes de type 'plat' qui sont catégorisées par pays
    """
    time.sleep(4)
    driver.get(driver.find_element(By.LINK_TEXT,'Cuisine du monde').get_attribute('href')) #open the link cuisintes du mondes
    time.sleep(4)
    countries = [i.text for i in driver.find_elements(By.TAG_NAME,'h2')[0:13]]
    #print(countries)
    plus_de_recettes = [i.find_elements(By.TAG_NAME,'a')[-1].get_attribute('href') for i in driver.find_elements(By.CLASS_NAME,'ss-item') ]
    #print(plus_de_recettes)
    return list(zip(countries,plus_de_recettes))


# In[22]:


def extract_recettes_links(driver,l:str)->list():
    """
    Permet d'extraire les liens qui menent vers les recettes 
    l: represente le lien d'une recette 
    """
    ### This function extracts all the links leading to recipes specific to each type of food (appéritif, plat, desser ...)
    driver.get(l)
    #recettes = [i.get_attribute('href') for i in driver.find_element(By.CLASS_NAME,"recipe-list").find_elements(By.TAG_NAME,"a")]
    recettes=list()
    #Loop over the pages of recipes and stops when the next button doesn't show up anymore
    while True: 
        try:         
            recettes.extend([i.get_attribute('href') for i in driver.find_element(By.CLASS_NAME,"recipe-list").find_elements(By.TAG_NAME,"a")])
            driver.find_element(By.CLASS_NAME, "next").click()
        except:
            return recettes


# In[23]:


# extraire les liens des recettes
def extract_links_of_3_meals()->dict():
    """
    Permet de parcourir toutes les pages de chaque type de recette (entrée, plats, ou desserts) et extraire tous les liens
    """
    driver = webdriver.Chrome(executable_path='chromedriver.exe')
    driver.get('https://www.ptitchef.com/recettes/aperitif')
    type_and_link = extract_type_plats_liens(driver)
    recettes = dict() ## {'entry':[....], 'apperitif':[...],plats:{'Recettes de cuisine italienne':[],'Recettes de cuisine tunisienne':[....],....},'desserts':[....],....}
    recipes_per_country = dict() ## 
    recettes_type=type_and_link[0]
    liens=type_and_link[1]
    #recettes[liens[0].split("/")[-1]] = extract_recettes_links(driver)

    for l in range(1,4):
        if liens[l].split("/")[-1] != "plat":
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            recettes[liens[l].split("/")[-1]] = extract_recettes_links(driver,liens[l])
        else:
            driver.get(liens[l])
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            recipes_per_country = extract_plus_de_recettes(driver,recipes_per_country)
            recipes_per_country = {i[0]:i[1] for i in recipes_per_country}
            recipes_per_country = {keys:extract_recettes_links(driver,values) for keys, values in recipes_per_country.items()}
            recettes['plat'] = recipes_per_country
    return recettes


# In[7]:


#delete irrelevant links:
"""
restructurer la dict des liens
"""
r2 = copy.copy(r)
r2['entree'] = [link for link in r['entree'] if 'ptitchef.com' in link]
r2['dessert'] = [link for link in r['dessert'] if 'ptitchef.com' in link]
r2['plat'] = {k:[link for link in v if 'ptitchef.com' in link] for k,v in r['plat'].items()}
print(r2['plat'])


# In[3]:


"""
sauvegarder le dict des liens dans un pickle
"""
with open('Recipes_store.pkl', 'rb') as filehandler:
    loaded_object = pickle.load(filehandler)


# # Extract Information from a recipe 

# In[24]:


def clean_one_ingred(string:str)->str:
    """
    nettoyer les ingrédients pour enlever certains mots tel que cl, ml, poignée et aussi les chiffre
    """
    pattern = r'\b\d+\b|\bcas\b|\bcl\b|\bcac\b|\bml\b|\bpoignée\b|\bgr\b'
    # Remove the specified patterns
    cleaned_string = re.sub(pattern, '', string)
    # Replace multiple spaces with a single space
    cleaned_string = re.sub(r'\s+', ' ', cleaned_string).strip()
    cleaned_string = cleaned_string.rstrip('.')
    return cleaned_string


# In[25]:


# Clean the ingredients: REMOVE words like cl, cas, cac et les quantités cette fonction permettera aussi d'enregistrer la liste d'ingredients 
# will take a list of unclean ingredients. it will return a list of clean ingerdients without duplicates

def clean_ingredients(list_ingr_new:list)->list():
    """
    Permet d'utiliser la fonction précedente sur une liste de chaines de characteres
    """
    global list_ingredient_full
    #The pattern should be extended to include more words that can be removed
    pattern = r'\b\d+\b|\bcas\b|\bcl\b|\bcac\b|\bml\b|\bpoignée\b|\bc/.\b'
    list_ingr_new = [clean_one_ingred(i) for i in list_ingr_new]
    return list_ingredient_full+[i for i in list_ingr_new if i not in list_ingredient_full]
    


# In[26]:


list_ingredient_full = list()

def extract_inf(link:str,country:str)->dict():
    """
    Extraire les informations d'une recette et les stocker dans un dictionnaire. tous les dictionnaires ont était sauvegardé dans 
    une base MongoDB
    """
    
    global recip_project
    global list_ingredient_full
    recettes_already_stored = [i['nom recette'] for i in recip_project.find()]
    #print(recettes_already_stored)
    driver.get(link)
    try:
        try:
            driver.find_elements(By.CLASS_NAME,"sd-cmp-3V2Vm")[1].find_element(By.TAG_NAME,"button").click()
            d_recettes['nom recette'] = nom


            d_recettes['pays'] = country

            inf = driver.find_elements(By.CLASS_NAME,'rdbsi-val')
            type_rec = inf[0].text
            d_recettes['Type de recette'] = type_rec

            nbr_personnes = inf[1].text
            d_recettes['nbr_personnes'] = nbr_personnes 

            duree_prep = inf[2].text
            d_recettes['duree_prep'] = duree_prep 


            duree_cuisson = inf[3].text
            d_recettes['durée_cuisson'] = duree_cuisson 


            diff = inf[4] .text
            d_recettes['difficulté'] = diff    


            ingredient_quant = [i.text for i in driver.find_element(By.CLASS_NAME,'ingredients-ul').find_elements(By.TAG_NAME,'label')]


            d_recettes['quantités et ingrédients'] = ingredient_quant 
            ingredient_clean = clean_ingredients(ingredient_quant)
            list_ingredient_full.extend(ingredient_clean)

            étapes_list = driver.find_element(By.CLASS_NAME,'rdisc-right').find_elements(By.TAG_NAME, 'li')
            étapes_dict = {str((i+1)):étapes_list[i].text for i in range(0,len(étapes_list))}

            img = [i.get_attribute('src') for i in driver.find_elements(By.TAG_NAME,'img')]

            d_recettes['image'] = img[7] 
            recip_project.insert_one(d_recettes)
            return d_recettes

        except:
            #print("test")
            d_recettes = {}
            nom = driver.find_element(By.TAG_NAME,'h1').text
            print(nom)
            if nom not in recettes_already_stored:
                d_recettes['nom recette'] = nom


                d_recettes['pays'] = country

                inf = driver.find_elements(By.CLASS_NAME,'rdbsi-val')
                type_rec = inf[0].text
                d_recettes['Type de recette'] = type_rec

                nbr_personnes = inf[1].text
                d_recettes['nbr_personnes'] = nbr_personnes 

                duree_prep = inf[2].text
                d_recettes['duree_prep'] = duree_prep 


                duree_cuisson = inf[3].text
                d_recettes['durée_cuisson'] = duree_cuisson 


                diff = inf[4] .text
                d_recettes['difficulté'] = diff    


                ingredient_quant = [i.text for i in driver.find_element(By.CLASS_NAME,'ingredients-ul').find_elements(By.TAG_NAME,'label')]


                d_recettes['quantités et ingrédients'] = ingredient_quant 
                ingredient_clean = clean_ingredients(ingredient_quant)
                list_ingredient_full.extend(ingredient_clean)
                list_ingredient_full = list(set(list_ingredient_full))

                étapes_list = driver.find_element(By.CLASS_NAME,'rdisc-right').find_elements(By.TAG_NAME, 'li')
                étapes_dict = {str((i+1)):étapes_list[i].text for i in range(0,len(étapes_list))}

                d_recettes['étapes'] = étapes_dict


                img = [i.get_attribute('src') for i in driver.find_elements(By.TAG_NAME,'img')]

                d_recettes['image'] = img[7] 

                recip_project.insert_one(d_recettes)
                return d_recettes
            else:
                pass
    except:
        pass


# # Extract information from all the recipes

# In[5]:


"""
extraire le liens des recettes à partir du pickle
"""
with open('Recipes_store.pkl', 'rb') as filehandler:
    loaded_object = pickle.load(filehandler)


# In[218]:


"""
Nous avons segmenter l'extraction des informations des recettes en trois parties. Nous avons commencé par extraire toutes les entrée ensuite tous les 
plats, ensuite tous les desserts. Le code ci-dessous représente l'extraction des desserts
"""
recettes_desserts = {}
option = webdriver.ChromeOptions()
driver = webdriver.Chrome(executable_path='chromedriver.exe',options=option)
links_plats = loaded_object['dessert']
recettes_desserts = [extract_inf(i,'None') for i in links_plats if i]
    
        
        
"""
list_ingredient_full étant definie comme une variable globale. Nous avons sauvegardé le contenu de cette variable dans un pickle 
Au tout début nous voulions aussi utiliser les ingrédients de cette liste comme input de l'interface mais nous avons abandonné l'idée 
au vu des besoins preprocessing requis afin d'éliminer tous les mots non pertinant (cuillere, rouge, rave, verte ...) à notre outil 
"""        
#Store the list of ingredients in a pickle 
object_to_pickle = list_ingredient_full
# Open the file in binary write mode 'wb'
with open('list_ingr.pkl', 'wb') as filehandler:
    pickle.dump(object_to_pickle, filehandler)
        
#recettes_plats = {k:[extract_inf(i) for i in v] for k,v in links_plats.items()}


# In[66]:


"""
Compter le nombre de recette dans la base de données
"""

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["Recipes_db"]
recip_project = mydb["Recipes"]

count = 0

for x in recip_project.find():
    count += 1
    print(x)


# # Extraire une liste d'ingrédients

# In[ ]:


"""
Extraire une liste d'ingrédients à partir du site qu'est ce que on mange
"""


option = webdriver.ChromeOptions()
driver = webdriver.Chrome(executable_path='chromedriver.exe',options=option)
driver.get('https://www.qu-est-ce-qu-on-mange.com/dans-mon-frigo')
links_to_scrap = [i for i in driver.find_element(By.ID,'les-ingredients_corps').find_elements(By.TAG_NAME,'DIV') if i.text
                  in ["Légumes","Viandes, poissons et oeufs","Féculents et légumineuses","Produits laitiers","Fruits et fruits secs","Autres","Charcuterie"]]



#print(links_to_scrap)
ingredients = list()

for i in range(0,len(links_to_scrap)):
    print(ingredients)
    time.sleep(5)
    links_to_scrap = [i for i in driver.find_element(By.ID,'les-ingredients_corps').find_elements(By.TAG_NAME,'DIV') if i.text
                  in ["Légumes","Viandes, poissons et oeufs","Féculents et légumineuses","Produits laitiers","Fruits et fruits secs","Autres","Charcuterie"]]

    links_to_scrap[i].click()

    #time.sleep(5)
    if links_to_scrap[i].get_attribute("id") == "categorie-2":
        time.sleep(5)
        for j in range(0,len(driver.find_element(By.XPATH,"//div[@id='modale-contenu']").find_elements(By.TAG_NAME,'img'))):
            time.sleep(2)
            driver.find_element(By.XPATH,"//div[@id='modale-contenu']").find_elements(By.TAG_NAME,'img')[j].click()
            time.sleep(5)

            ingredients.extend([i.text for i in driver.find_element(By.XPATH,"//div[@id='modale-contenu']").find_elements(By.XPATH,"//div[@class='ingredient-de-liste']")])
            time.sleep(2)
            driver.get('https://www.qu-est-ce-qu-on-mange.com/dans-mon-frigo')
            time.sleep(3)
            #driver.back()
            driver.find_element(By.ID,'les-ingredients_corps').find_elements(By.TAG_NAME,'DIV')[1].click()
        
        driver.get('https://www.qu-est-ce-qu-on-mange.com/dans-mon-frigo')


            
    elif links_to_scrap[i].get_attribute("id") == "categorie-6":
        time.sleep(5)
        for j in range(0,len(driver.find_element(By.XPATH,"//div[@id='modale-contenu']").find_elements(By.TAG_NAME,'img'))):
            time.sleep(5)
            driver.find_element(By.XPATH,"//div[@id='modale-contenu']").find_elements(By.TAG_NAME,'img')[j].click()
            time.sleep(5)

            ingredients.extend([i.text for i in driver.find_element(By.XPATH,"//div[@id='modale-contenu']").find_elements(By.XPATH,"//div[@class='ingredient-de-liste']")])
            time.sleep(2)
            driver.get('https://www.qu-est-ce-qu-on-mange.com/dans-mon-frigo')
            time.sleep(3)
            #driver.back()
            driver.find_element(By.ID,'les-ingredients_corps').find_elements(By.TAG_NAME,'DIV')[6].click()
        
        driver.get('https://www.qu-est-ce-qu-on-mange.com/dans-mon-frigo')

        
    else: 
        #i.click()
        print([i.text for i in driver.find_element(By.XPATH,"//div[@id='fenetre-modale']").find_elements(By.XPATH,"//div[@class='ingredient-de-liste']")])
        time.sleep(5)
        ingredients.extend([i.text for i in driver.find_element(By.XPATH,"//div[@id='modale-contenu']").find_elements(By.XPATH,"//div[@class='ingredient-de-liste']")])
        time.sleep(2)
        driver.find_element(By.CLASS_NAME,'modale-btn-close').click()
        


# In[ ]:


"""
Au vue de la maniere dont certains ingrédients sont écris nous avons du modifier un peu la liste d'ingrédients obtenues. En effet, 
sur le site 'é' a été codifiée par 'Ã©', 
"""

nouvelle_liste = list()

for element in ingr_list:
    nouvel_element = element.replace("Ã©", "é").replace("Ã¨", "è").replace("Ãª", "ê").replace("Ã¢","â").replace("Ã¯","ï").replace("Ã»","û").replace("Ã","à").replace("à´","ô")
    nouvelle_liste.append(nouvel_element)

    
"""
Stocker la nouvelle liste d'ingrédients dans un pickle
"""   
with open('Ingredients_clean.pkl', 'wb') as filehandler:
    pickle.dump(nouvelle_liste, filehandler)


# # Tkinter Interface

# In[90]:


"""
importer la liste d'ingrédients
"""
with open('Ingredients_clean.pkl', 'rb') as filehandler:
    ingr_list = pickle.load(filehandler)

#print(ingr_list)


# In[89]:


def interface():
"""
Creation de l'interface qui permet à l'utilisateur de choisir entre cusiner une entrée, un plat ou un dessert et d'entrer la liste des
ingredients
"""
    def add_item():
        selected_item = my_list.get(tk.ACTIVE)
        if selected_item not in selected_ingr:
            selected_ingr.append(selected_item)
            update(selected_ingr)

    def remove_item():
        selected_item = my_list.get(tk.ACTIVE)
        if selected_item in selected_ingr:
            selected_ingr.remove(selected_item)
            update(selected_ingr)

    def validate():
        global selected_types

        selected_types = [type_labels[i] for i, selected in enumerate(type_vars) if selected.get()]

        if len(selected_types) == 0:
            messagebox.showinfo("Validation Error", "Please select at least one type (Entrée, Plat, or Dessert).")
        elif len(selected_ingr) == 0:
            messagebox.showinfo("Validation Error", "Please select at least one ingredient.")
        else:
            root.destroy()

    def check_selected_items():
        selected_items = "\n".join(selected_ingr)
        if selected_items:
            messagebox.showinfo("Selected Items", "Selected ingrs:\n" + selected_items)
        else:
            messagebox.showinfo("Selected Items", "No ingrs selected.")

    root = tk.Tk()
    root.title("ingrs Selector")

    main_frame = ttk.Frame(root, padding=20)
    main_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    main_frame.columnconfigure(0, weight=1)
    main_frame.rowconfigure(1, weight=1)

    my_label = ttk.Label(main_frame, text="Choisir au moins un ingrédient et le type de plat souhaité", font=("Helvetica", 14), foreground="grey")
    my_label.grid(column=0, row=0, pady=(0, 20))

    my_entry = ttk.Entry(main_frame, font=("Helvetica", 20))
    my_entry.grid(column=0, row=1, sticky=(tk.W, tk.E))

    my_list = tk.Listbox(main_frame, width=50, selectmode=tk.SINGLE)  # Change selectmode to SINGLE
    my_list.grid(column=0, row=2, pady=20, sticky=(tk.W, tk.E, tk.N, tk.S))

    scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=my_list.yview)
    scrollbar.grid(column=1, row=2, sticky=(tk.N, tk.S))
    my_list.configure(yscrollcommand=scrollbar.set)

    add_button = ttk.Button(main_frame, text="Add", command=add_item)
    add_button.grid(column=0, row=3, pady=(0, 10), sticky=(tk.W, tk.E))

    remove_button = ttk.Button(main_frame, text="Remove", command=remove_item)
    remove_button.grid(column=0, row=4, pady=(0, 10), sticky=(tk.W, tk.E))

    validate_button = ttk.Button(main_frame, text="Validate", command=validate)
    validate_button.grid(column=0, row=5, pady=(0, 10), sticky=(tk.W, tk.E))

    check_selected_button = ttk.Button(main_frame, text="Check Selected Items", command=check_selected_items)
    check_selected_button.grid(column=0, row=6, pady=(0, 10), sticky=(tk.W, tk.E))

    ingrs = ingr_list

    selected_ingr = []

    def update(ingrs):
        my_list.delete(0, tk.END)
        for item in ingrs:
            my_list.insert(tk.END, item)

    update(ingrs)

    def check(e):
        typed = my_entry.get()

        if typed == '':
            data = ingrs
        else:
            data = []
            for item in ingrs:
                if typed.lower() in item.lower():
                    data.append(item)
        update(data)

    my_entry.bind("<KeyRelease>", check)

    type_labels = ["Entrée", "Plat", "Dessert"]
    type_vars = [tk.IntVar() for _ in type_labels]
    type_frame = ttk.Frame(main_frame)
    type_frame.grid(column=0, row=7, pady=10, sticky=(tk.W, tk.E))

    for i, type_label in enumerate(type_labels):
        ttk.Checkbutton(type_frame, text=type_label, variable=type_vars[i]).pack(side=tk.LEFT)

    root.mainloop()

    return selected_ingr, selected_types


# # Matching the list of ingredients with recipes 

# In[72]:


def stemming_l_w(l:str)->list():
    """
    Uniformiser l'ingrédient afin d'assurer une meilleure comparaison entre les ingrédients de l'interface et ceux de la recette
    """
    
    new_list_ingr = list()
    stemmer=nltk.stem.SnowballStemmer('french')

    if type(l)==list:
        for i in l:
            new_list_ingr.extend([stemmer.stem(j) for j in i.split()])
        return new_list_ingr
    else:
        return [stemmer.stem(i) for i in l.split()] 


# In[73]:


"""
Importer la liste des recettes
"""

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["Recipes_db"]
recip_project = mydb["Recipes"]

count = 0

for x in recip_project.find():
    count += 1
    print(x)


# In[74]:


def matching_count(db,selected_ingr:list())->dict():
    
    """
    compter pour chaque recette le nombre de matchs qui existent pour une liste d'ingrédients donnée
    """
    
    ### Matching evaluate the match of each recipe with my actual list of ingredients
    matching_dict = dict() # This dictionary will contain for each reciept the number of matches that occured with the list of ingredients that we have 
    #the comparison will be done by parsing through the list of ingredients and check if an ingredient appears in 
    #the list of ingeredients in the recipts. before comparing both the string ingredient and the strings in the list of ingredients in the recipet will be stemmed


    #myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    #mydb = myclient["Recipes_db"]
    recip_project = db
    
    for r in recip_project:
        count_nbr_match = 0
        for i in selected_ingr:
            if stemming_l_w(i)[0] in stemming_l_w(r['quantités et ingrédients']):
                count_nbr_match+=1
        matching_dict[r["_id"]] = count_nbr_match
        
    return  matching_dict


# In[75]:


def best_match_ids(matching_dict:dict())->list():
    """
    Trouve la position des recettes avec le plus haut matching score
    """
    max_count = max([v for v in matching_dict.values()])
    return [k for k,v in matching_dict.items() if v==max_count]
    


# In[76]:


def matched_recipes(db,best_match_ids):
    """
    retourne la liste des recettes qui vont etre suggérées à l'utilisateur
    """
    final_recettes = list()

    recip_project = db
    
    return [r for r in recip_project if r['_id'] in best_match_ids]


# In[77]:


def filter_recipes_database(recip_type:list())->list():
    
    """
    Permert de Filter la base de données MongoDb par plats, entrée ou desserts pour ne montrer
    """
    
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["Recipes_db"]
    recip_project = mydb["Recipes"]
    result = list()
    for rt in recip_type:
        result.extend(recip_project.find({'Type de recette':rt}))
        
    
    return [r for r in result]

    
    


# # Tkinter Final output 

# In[78]:


def display_recipes(recipes_data):
    """
    L'interface qui permet de visualiser les recettes retenues
    """
    
    def display_recipe_details(selected_recipe):
        title_label.config(text=selected_recipe['nom recette'])
        type_label.config(text=f"Type de recette: {selected_recipe['Type de recette']}")
        servings_label.config(text=f"Nombre de personnes: {selected_recipe['nbr_personnes']}")

        # Calculate the total preparation time and cooking time
        total_prep_time = selected_recipe['duree_prep']
        total_cooking_time = selected_recipe['durée_cuisson']

        preparation_time_label.config(text=f"Temps de préparation: {total_prep_time}")
        cooking_time_label.config(text=f"Durée de cuisson: {total_cooking_time}")
        difficulty_label.config(text=f"Difficulté: {selected_recipe['difficulté']}")

        ingredients_text.config(state=tk.NORMAL)
        ingredients_text.delete('1.0', tk.END)
        for ingredient in selected_recipe['quantités et ingrédients']:
            ingredients_text.insert(tk.END, f"{ingredient}\n")
        ingredients_text.config(state=tk.DISABLED)
        steps_text.config(state=tk.NORMAL)
        steps_text.delete('1.0', tk.END)
        for step_number, step_text in selected_recipe['étapes'].items():
            steps_text.insert(tk.END, f"Étape {step_number}:\n{step_text}\n\n")
        steps_text.config(state=tk.DISABLED)
        image_url = selected_recipe['image']
        image = Image.open(requests.get(image_url, stream=True).raw)
        image = image.resize((300, 300), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(image)
        image_label.config(image=photo)
        image_label.photo = photo

    root = tk.Tk()
    root.title("Recipe")

    listbox_frame = ttk.Frame(root)
    listbox_frame.pack(side=tk.LEFT, fill=tk.Y)

    recipes_listbox = tk.Listbox(listbox_frame, font=("Arial", 12), selectmode=tk.SINGLE)
    recipes_listbox.pack(fill=tk.BOTH, expand=True)

    for recipe in recipes_data:
        recipes_listbox.insert(tk.END, recipe['nom recette'])

    details_frame = ttk.Frame(root)
    details_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    title_label = ttk.Label(details_frame, text="", font=("Arial", 20))
    title_label.pack()

    type_label = ttk.Label(details_frame, text="", font=("Arial", 12))
    type_label.pack()

    servings_label = ttk.Label(details_frame, text="", font=("Arial", 12))
    servings_label.pack()

    preparation_time_label = ttk.Label(details_frame, text="", font=("Arial", 12))
    preparation_time_label.pack()
    cooking_time_label = ttk.Label(details_frame, text="", font=("Arial", 12))
    cooking_time_label.pack()
    difficulty_label = ttk.Label(details_frame, text="", font=("Arial", 12))
    difficulty_label.pack()

    ingredients_text = tk.Text(details_frame, height=10, width=45, font=("Arial", 12))
    ingredients_text.pack(fill=tk.BOTH, expand=True)
    ingredients_text.config(state=tk.DISABLED)

    steps_text = tk.Text(details_frame, height=15, width=45, font=("Arial", 12))
    steps_text.pack(fill=tk.BOTH, expand=True)
    steps_text.config(state=tk.DISABLED)

    image_label = ttk.Label(details_frame)
    image_label.pack()

    def on_select(event):
        selected_index = recipes_listbox.curselection()
        if selected_index:
            selected_index = int(selected_index[0])
            selected_recipe = recipes_data[selected_index]
            display_recipe_details(selected_recipe)

    recipes_listbox.bind('<<ListboxSelect>>', on_select)

    root.mainloop()


# # Final Code

# In[92]:


# Tomate, Ail, ognion: entrée, plat  
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["Recipes_db"]
recip_project = mydb["Recipes"]

selected_ingr,recipe_type=interface()
print(selected_ingr)
filtered_db = filter_recipes_database(recipe_type)

print(filtered_db)
count_matches = matching_count(filtered_db,selected_ingr) # This resutrns a dictionary that counts the occurence of each ingredients in each recipe 
match_ids = best_match_ids(count_matches) #Returns the mongodb ids of the recipes with the highest match. Those that contain most or all of the ingredients selected 
recipes_final = matched_recipes(filtered_db,match_ids)
display_recipes(recipes_final)


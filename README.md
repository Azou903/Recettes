# Recommendations de recettes
# Requirements

PIL==9.2.0
bs4==4.11.1
bson==0.5.10
nltk==3.7
numpy==1.21.5
pandas==1.4.4
pipreqs==0.4.13
pymongo==4.5.0
selenium==4.8.2
tkinter==8.6
json==2.0.9
re==2.2.1
pickle==3.0.1
urlib.request==3.9
time==3.6.0

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Selenium](https://img.shields.io/badge/-selenium-%43B02A?style=for-the-badge&logo=selenium&logoColor=white)
![PythonTkinter](https://img.shields.io/badge/pythonTkinter-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)

# Terminale utiliser

![Jupyter Notebook](https://img.shields.io/badge/jupyter-%23FA0F00.svg?style=for-the-badge&logo=jupyter&logoColor=Yellow)

# Description

Ce projet a été réalisé dans le cadre du cours de programmation avancée du M2 DS2E.Ce programme vise à suggérer des recettes suite à des ingrédients présélectionner

## Idée de projet

• Suggérer une liste de recettes à partir d’une liste d’ingredients

## Objectifs

• Manger! Manger! Manger! 

• Donner envie de cuisine et faciliter à trouver des recettes

• Diminuer le gaspillage alimentaire

## Les étapes

Notre projet est composé de trois étapes importantes :
- Webscraping (avec le package Selenium) puis nettoyage des données : de nos recettes dans le site web (https://www.ptitchef.com/recettes/entree) et de nos ingrédients dans le site web (https://www.qu-est-ce-qu-on-mange.com/dans-mon-frigo)

![cover](https://github.com/Azou903/Recettes/blob/main/recette.png)

- Creation d'une première interface web qui permet de selectionner les ingrédients afin d'avoir une suggetion de recette

![cover](https://github.com/Azou903/Recettes/blob/main/interface%201.png)

  
- création d'un second interface qui prend en compte la suggestion des différents recettes après selection des ingrédients en montrant les images des rectettes, le temps de préparation, la durée de cuisson, les ingrédients necessaires, les différentes étapes de préparation et la difficulté de préparation.

![cover](https://github.com/Azou903/Recettes/blob/main/interface%202.png)







## Contributeur

SOW Assane : [@Azou903](https://github.com/Azou903)

KEBIR Zied : [@ZiedKebir](https://github.com/ZiedKebir)

## Limites et Extensions
# Limites

➢ Recettes obtenues peuvent contenir plus d’ingredients que ceux suggérés

➢ Probléme avec les noms d’ingredients composés (exemple: oignion rouge, Asperge blanche…) : le prgramme ne peux considéré les noms composés mais à la place, il va considéré chaque mots : "oignon" et "rouge" et faire la recherche pour chaque mot.

➢ Liste d’ingredients non exhaustive 

# Extensions

➢ Filtrer les recettes par pays (Italian, Français...)

➢ Matching par mot composé (l’algorithme recherche oignion rouge au lieu de juste oignion)

➢ Envoyer la liste d’ingredients par email 

➢ Améliorer le design de l’interface


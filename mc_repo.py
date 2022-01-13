import json
import os
import requests
from os.path import exists

class MCRepo():

    __language = 'en'
    __deckIds = []

    __cardPath = "api/public/card"
    __deckPath = "api/public/deck"

    __translationMap = {
        'hero': {
            'de': 'Held',
            'es': 'H\u00e9roe',
            'fr': 'H\u00e9ro',
            'it': 'Eroe'
        },
        'ally': {
            'de': 'Verb\u00fcndeter',
            'es': 'Aliado',
            'fr': 'Ali\u00e9es',
            'it': 'Alleato'
        },
        'upgrade':{
            'de': 'Upgrade',
            'es': 'Mejora',
            'fr': 'Am\u00e9liorations',
            'it': 'Miglioria'
        },
        'event':{
            'de': 'Ereignis',
            'es': 'Evento',
            'fr':'\u00c9v\u00e8nements',
            'it': 'Evento'
        },
        'support':{
            'de': 'Vorteil',
            'es': 'Apoyo',
            'fr': 'Soutiens',
            'it': 'Supporto'
        },
        'resource':{
            'de': 'Ressource',
            'es': 'Recurso',
            'fr': 'Ressource',
            'it': 'Risorsa'
        },
        'other':{
            'de': 'Andere',
            'es': 'Otros',
            'fr': 'Autres',
            'it': 'Altro'
        }
    }
    
    def __init__(self, language, deckIds):
        self.__language = language
        self.__deckIds = deckIds

    #---------------------------------------------

    def __jwrite(self, fileName, json):
        dirName = os.path.dirname(fileName)
        if not os.path.exists(dirName):
            os.makedirs(dirName)
        with open(fileName, "w") as file:
            file.write(json)

    def __jread(self, fileName):
        with open(fileName, 'r') as file:
            return json.load(file)

    #---------------------------------------------
 
    def __getUrl(self, path, id):
        match self.__language:
            case 'en':
                prefix = ''
            case _:
                prefix = f"{self.__language}."
        return f"https://{prefix}marvelcdb.com/{path}/{id}"

    def __getFile(self, path, id):
        return  f'./cache/{self.__language}/{path}/{id}.json'

    #---------------------------------------------

    def __fetch(self, path, id):
        fileName = self.__getFile(path, id)
        if exists(fileName) :
            return self.__jread(fileName)
        else:
            response = requests.get(self.__getUrl(path, id))
            json_str = json.dumps(response.json(), sort_keys=True, indent=4)
            json_str = json_str.replace('\\u0152','OE').replace('\\u0153','oe')
            self.__jwrite(fileName, json_str)
            return json.loads(json_str)

    #---------------------------------------------

    def __localise(self, text: str):
        if text.lower() in self.__translationMap:
            translations = self.__translationMap[text.lower()]
            if self.__language in translations:
                return translations[self.__language]
        return text

    #---------------------------------------------

    def __buildCard(self, cardId, cardQuantity):
        cardResponse = self.__fetch(self.__cardPath, cardId)
    
        if cardResponse['faction_code']=='basic':
            if 'card_set_type_name_code' in cardResponse:
                icon = 'resources/hero-grey.png'
            else:
                icon = 'resources/basic.png'
        elif cardResponse['faction_code']=='justice':
            if 'card_set_type_name_code' in cardResponse:
                icon = 'resources/hero-yellow.png'
            else:
                icon = 'resources/justice.png'
        elif cardResponse['faction_code']=='aggression':
            if 'card_set_type_name_code' in cardResponse:
                icon = 'resources/hero-red.png'
            else:
                icon = 'resources/aggression.png'
        elif cardResponse['faction_code']=='protection':
            if 'card_set_type_name_code' in cardResponse:
                icon = 'resources/hero-green.png'
            else:
                icon = 'resources/protection.png'
        elif cardResponse['faction_code']=='leadership':
            if 'card_set_type_name_code' in cardResponse:
                icon = 'resources/hero-blue.png'
            else:
                icon = 'resources/leadership.png'
        else:
            icon = 'resources/hero-black.png'

        if 'card_set_type_name_code' in cardResponse:
            cardType = 'Hero'
        elif cardResponse['type_code']=='ally':
            cardType = 'Ally'
        elif cardResponse['type_code']=='upgrade':
            cardType = 'Upgrade'
        elif cardResponse['type_code']=='event':
            cardType = 'Event'
        elif cardResponse['type_code']=='support':
            cardType = 'Support'
        elif cardResponse['type_code']=='resource':
            cardType = 'Resource'
        else:
            cardType = 'Other'

        card = {
            "name": cardResponse["name"],
            "quantity": cardQuantity,
            "icon":icon
        }
        return card, cardType

    #---------------------------------------------

    def __buildDeck(self, deckId):

        deckResponse = self.__fetch(self.__deckPath, deckId)

        deck = {
            "name": "",
            "version": "",
            "url":"",
            "cards": {}
        }

        # add another cell
        deck["name"] = deckResponse["name"]
        deck["version"] = deckResponse["version"]
        deck["url"] = self.__getUrl("deck/view",deckId)

        # Initialize cards sections to fix order. (hero, ally, ...) 
        deck['cards'][self.__localise('hero')] = []
        deck['cards'][self.__localise('ally')] = []
        deck['cards'][self.__localise('upgrade')] = []
        deck['cards'][self.__localise('event')] = []
        deck['cards'][self.__localise('support')] = []
        deck['cards'][self.__localise('resource')] = []

        for cardId, cardQuantity in deckResponse["slots"].items():
            card, cardType = self.__buildCard( cardId, cardQuantity)

            cardType = self.__localise(cardType)

            if cardType not in deck['cards']:
                deck['cards'][cardType] = []

            deck['cards'][cardType].append(card)
            
        return deck

    #---------------------------------------------

    def buildDecks(self):
        decks = []
        for deckId in self.__deckIds:
            decks.append(self.__buildDeck(deckId))
        return decks

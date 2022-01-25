import json
import os
import requests
from os.path import exists
from mc_args import MCArgs
from mc_args import SortingMode
from mc_progress import MCProgress

class MCRepo():

    __args: MCArgs = None
    __progress: MCProgress = None
    
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
    
    def __init__(self, args, progress):
        self.__args = args
        self.__progress = progress

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
        match self.__args.language:
            case 'en':
                prefix = ''
            case _:
                prefix = f"{self.__args.language}."
        return f"https://{prefix}marvelcdb.com/{path}/{id}"

    def __getFile(self, path, id):
        return  f'./cache/{self.__args.language}/{path}/{id}.json'

    #---------------------------------------------

    def __fetch(self, path, id):
        fileName = self.__getFile(path, id)
        if exists(fileName) :
            return self.__jread(fileName)
        else:
            response = requests.get(self.__getUrl(path, id))
            try:
                json_str = json.dumps(response.json(), sort_keys=True, indent=4)
                json_str = json_str.replace('\\u0152','OE').replace('\\u0153','oe')
                json_str = json_str.replace("\\u2018","'" ).replace("\\u2019","'" )
                self.__jwrite(fileName, json_str)
                return json.loads(json_str)
            except Exception:
                raise
 
    #---------------------------------------------

    def __localise(self, text: str):
        if text.lower() in self.__translationMap:
            translations = self.__translationMap[text.lower()]
            if self.__args.language in translations:
                return translations[self.__args.language]
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

        packName = cardResponse["pack_name"]

        card = {
            "name": cardResponse["name"],
            "quantity": cardQuantity,
            "icon":icon
        }
        return card, cardType, packName

    #---------------------------------------------

    def __createSection(self, name):
       return {
            "name":self.__localise(name),
            "cout":0,
            "cards":{}
        } 

    #---------------------------------------------

    def __buildDeck(self, jdeck):

        deckId = jdeck['id']

        try:
            deckResponse = self.__fetch(self.__deckPath, deckId)
        except Exception:
            raise

        deckTitle = deckResponse["name"] if jdeck['title'] == None else jdeck['title']

        deck = {
            "name": "",
            "hero": "",
            "version": "",
            "url":"",
            "sections":{}
        }

        identitySectionName = self.__localise("Identity")

        # add another cell
        deck["name"] = deckTitle
        deck["hero"] = deckResponse["investigator_name"]
        deck["version"] = deckResponse["version"]
        deck["url"] = self.__getUrl("deck/view",deckId)

        # Initialize cards sections to fix order. (hero, ally, ...) 
        deck['sections'][identitySectionName] = {"count":0, "cards":[]}

        if self.__args.sortingMode == SortingMode.BY_TYPE:
            deck['sections'][self.__localise('Ally')] = {"count":0, "cards":[]}
            deck['sections'][self.__localise('Upgrade')] = {"count":0, "cards":[]}
            deck['sections'][self.__localise('Event')] = {"count":0, "cards":[]}
            deck['sections'][self.__localise('Support')] = {"count":0, "cards":[]}
            deck['sections'][self.__localise('Resource')] = {"count":0, "cards":[]}

        cards = deckResponse["slots"].items()
        for cardId, cardQuantity in self.__progress.apply(cards, desc="Loading Card", leave=False):
            card, cardType, packName = self.__buildCard( cardId, cardQuantity)

            if cardType == "Hero":
                section = deck['sections'][identitySectionName]
                section["count"]+=card["quantity"]
                if self.__args.unfold: 
                    section["cards"].append(card)
            else:
                sectionName = self.__localise(cardType) if self.__args.sortingMode == SortingMode.BY_TYPE else packName

                if sectionName not in deck['sections']:
                    deck['sections'][sectionName] = {"count":0, "cards":[]}

                section = deck['sections'][sectionName]
                section["cards"].append(card)
                section["count"]+=card["quantity"] 
            
        return deck

    #---------------------------------------------

    def buildDecks(self):
        decks = []
        for jdeck in self.__progress.apply(self.__args.jdecks, desc="Create Deck "):
            try:
                decks.append(self.__buildDeck(jdeck))
            except Exception:
                deckId = jdeck['id']
                print(f'\nInvalid deck Id: {deckId}')
        return decks

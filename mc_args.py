import argparse
import json
import os
import mc_version
from enum import Enum
from pathlib import Path

class SortingMode(Enum):
    BY_TYPE = 1
    BY_SET = 2

class MCArgs():
    language = ''
    sortingMode = SortingMode.BY_TYPE
    pageOrientation = 'P'
    pageFormat = 'A4'
    unfold = False
    background = False
    backgroundDir = 'ressources/background'
    itemFontStyle = ''
    output = ''
    #deckIds = []
    jdecks = []

    def __init__(self):
        parser = argparse.ArgumentParser(description='Generate deck cards pdf document from a marvelcdb.com deck ID list.')
        parser.add_argument('-l','--language',choices=['de','es','fr','it'], default='en', help='Language to use. By default \'en\'.')
        parser.add_argument('-s', '--sort',choices=['by_type','by_set'], default='by_type', help='How to sort sections.By default sort by type')
        parser.add_argument('-po','--page_orientation',choices=['P','L'], default='P', help='Default page orientation. Portrait or Landscape. By default Portrait (P)')
        parser.add_argument('-pf','--page_format',choices=['A3','A4','A5','Letter','Legal'], default='A4', help='The format used for pages. By default A4')
        parser.add_argument('-u', '--unfold', action='store_true', help='To unfold the identity section. By default the section is \'Folded\'.')
        parser.add_argument('-b', '--background', action='store_true', help='Set background feature to \'on\'. By default the feature is \'off\'')
        parser.add_argument('-bd', '--background_dir', default='resources/background', help='To specify where to find background Image. By default in \'resource/background\'')
        parser.add_argument('-ifs', '--item_font_style', choices=['B','I','BI'], default='', help='Set font style for item text. By default no style is applied.')
        parser.add_argument('-a','--api',choices=['public'], default='public', help='Kind of API endpoint to use. By default the \'public\' api is used. For instance only public api is supported.')
        parser.add_argument('-i', '--input', help='Input text file containing a list of deck Id. (One Id by line)')
        #parser.add_argument('-o','--output', default='output/output.pdf', help='Output pdf file. By default \'output/output.pdf\'')
        parser.add_argument('-v','--version', action='version', version='%(prog)s ' + mc_version.__version__)
        parser.add_argument('deckIds', metavar='ID', type=int, nargs='*', default=[], help='Optional list of deck Ids')

        args = parser.parse_args()

        self.language = args.language
        self.pageOrientation = args.page_orientation
        self.pageFormat = args.page_format
        self.unfold = args.unfold
        self.itemFontStyle = args.item_font_style
        self.background = args.background
        self.backgroundDir = args.background_dir
        #self.output = args.output 

        self.sortingMode =  SortingMode.BY_TYPE if args.sort=='by_type' else SortingMode.BY_SET
        
        #self.output += '.pdf' if not args.output.lower().endswith('.pdf') else ''
        self.output = 'output/'
        self.output += Path(args.input).stem if args.input is not None else 'output'
        self.output += '.pdf'

        directory = os.path.dirname(self.output)
        if os.path.isdir(directory) == False:
            os.mkdir(directory)

        for deckId in args.deckIds:
            self.jdecks.append({"id":f'{deckId}',"title":None})
        #self.deckIds = args.deckIds
        if args.input is not None:
            with open(args.input) as file:
                if args.input.endswith(".json"):
                    jdecks = json.load(file)
                    for jdeck in jdecks:
                        self.jdecks.append(jdeck)
                else:
                    while (line := file.readline()):
                        words = line.split()
                        if len(words) > 0 and not words[0].startswith('#'):
                            #self.deckIds.append(words[0])
                            self.jdecks.append({"id":words[0],"title":None})

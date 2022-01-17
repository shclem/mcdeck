import argparse
import os

class MCArgs():

    language = ''
    deckIds = []
    output = ''

    def __init__(self):
        parser = argparse.ArgumentParser(description='Generate deck cards pdf document from a marvelcdb.com deck ID list.')
        parser.add_argument('deckIds', metavar='ID', type=int, nargs='*', default=[], help='Optional list of deck Ids')
        parser.add_argument('-l','--language',choices=['de','es','fr','it'], default='en', help='Language or \'en\' by default')
        parser.add_argument('-a','--api',choices=['public'], default='public', help='Kind of API endpoint to use or \'public\' by default. For instance only public api is supported.')
        parser.add_argument('-o','--output', default='output/output.pdf', help='Output pdf file or by default \'output/output.pdf\'')
        parser.add_argument('-i', '--input', help='Input text file with list of deck Id. (One Id for each line)')

        args = parser.parse_args()

        self.language = args.language

        self.output = args.output 
        self.output += '.pdf' if not args.output.lower().endswith('.pdf') else ''
        directory = os.path.dirname(self.output)
        if os.path.isdir(directory) == False:
            os.mkdir(directory)

        self.deckIds = args.deckIds
        if args.input is not None:
            with open(args.input) as file:
                while (line := file.readline()):
                    words = line.split()
                    if len(words) > 0 and words[0] != '#':
                        self.deckIds.append(words[0])

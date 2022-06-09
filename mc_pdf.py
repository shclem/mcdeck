import os.path

from fpdf import FPDF
from mc_args import MCArgs
from mc_progress import MCProgress

class MCPdf(FPDF):
    
    __args: MCArgs = None
    __progress: MCProgress = None

    __alternativeHeroNames = {
        '27030a':'Spider-Man - Miles Morales'
    }

    def __init__(self, args, progress):
        FPDF.__init__(self, orientation=args.pageOrientation, unit='mm', format=args.pageFormat)
        self.__args = args
        self.__progress = progress
        self.pageMarginWidth = 10
        self.pageMarginHeight = 10
        self.cardIndexX = 0
        self.cardIndexY = 0
        self.cardWidth = 62
        self.cardHeight = 88
        self.columlIndexX = 0
        self.columnWidth = 31
        self.columnMarginTop = 9
        self.columnMarginStart = 2
        self.set_fill_color(230)
        self.set_font("Arial", size = 6)

        self.x = self.pageMarginWidth
        self.y = self.pageMarginHeight

        self.nbCardOnPageWidth  = int((self.w - 2*self.pageMarginWidth) // self.cardWidth)
        self.nbCardOnPageHeight = int((self.h - 2*self.pageMarginHeight) // self.cardHeight)
        self.nbCardOnPage = self.nbCardOnPageWidth * self.nbCardOnPageHeight

    def __drawCutLines(self):
        self.set_draw_color(128)
        for xIndex in range(self.nbCardOnPageWidth+1):
            x = self.pageMarginWidth + xIndex * self.cardWidth
            self.line(x,0, x, self.h)
        for yIndex in range(self.nbCardOnPageHeight+1):
            y = self.pageMarginHeight + yIndex * self.cardHeight
            self.line(0,y,self.w,y)

    def __drawDeckSection(self,title,cards,count):
        if count > 0:
            self.x = self.pageMarginWidth + self.cardIndexX*self.cardWidth + self.columlIndexX*self.columnWidth

            if (self.y-self.pageMarginHeight-self.cardIndexY*self.cardHeight) > self.cardHeight - 12:
                self.columlIndexX = 1
                self.y = self.pageMarginHeight + self.cardIndexY*self.cardHeight + self.columnMarginTop
                self.x = self.pageMarginWidth + self.cardIndexX*self.cardWidth + self.columlIndexX*self.columnWidth

            self.set_font("Arial", size = 6, style = 'B')
            self.cell(20, 3, txt = f"{title} ({count})",ln = 2, align = 'L')

            self.x = self.pageMarginWidth + self.cardIndexX*self.cardWidth + self.columlIndexX*self.columnWidth + self.columnMarginStart
            self.y += 0.7

            self.set_font("Arial", size = 6, style = self.__args.itemFontStyle)
            cards.sort(key=lambda card: 'a' if card['icon']=='resources/basic.png' else card['icon']) 
            for card in cards:
                if (self.y-self.pageMarginHeight-self.cardIndexY*self.cardHeight) > self.cardHeight - 8:
                    self.columlIndexX = 1
                    self.y = self.pageMarginHeight + self.cardIndexY*self.cardHeight + self.columnMarginTop
                    self.x = self.pageMarginWidth + self.cardIndexX*self.cardWidth + self.columlIndexX*self.columnWidth + self.columnMarginStart

                x = self.x
                y = self.y
                self.image(card['icon'], w=2, h=2)
                self.y = y

                self.x += 2
                self.cell(4, 2.8, txt = f"{card['quantity']}X",ln = 0, align = 'L')
                self.multi_cell(22, 2.8, txt = card['name'], align = 'L', border = 0)
                self.x = x
                self.y += 0.2
            self.y += 0.7

    def __drawDeck(self,deck):

        totalCount = 0
        for section in deck['sections'].values():
            totalCount += section["count"]

        deckName = deck["name"]
        heroName = self.__alternativeHeroNames.get(deck["code"], deck["hero"])

        self.x = self.pageMarginWidth + self.cardIndexX * self.cardWidth
        self.y = self.pageMarginHeight + self.cardIndexY * self.cardHeight

        if self.__args.background:
            dir = self.__args.backgroundDir
            imagePath = f"{dir}/{heroName}.png"
            if os.path.exists(imagePath):
                self.image(imagePath, w=self.cardWidth, h=self.cardHeight)        
                self.x = self.pageMarginWidth + self.cardIndexX * self.cardWidth
                self.y = self.pageMarginHeight + self.cardIndexY * self.cardHeight

        self.set_font("Arial", size = 6, style = 'UB')
        self.cell(62, 6, txt = f"{deckName}", ln = 0, align = 'C', border = 0)
        
        self.x = self.pageMarginWidth + self.cardIndexX*self.cardWidth
        self.y = self.pageMarginHeight + self.cardIndexY*self.cardHeight + 4
        self.set_font("Arial", size = 6, style = 'I')
        self.cell(62, 4, txt = f"{heroName} ({totalCount})", ln = 0, align = 'C', border = 0)
        
        self.columlIndexX = 0

        self.y = self.pageMarginHeight + self.cardIndexY*self.cardHeight + self.columnMarginTop

        for sectionType, section in deck['sections'].items():
            self.__drawDeckSection(sectionType, section["cards"], section["count"])

        self.x = self.pageMarginWidth + self.cardIndexX * self.cardWidth
        self.y = self.pageMarginHeight + (self.cardIndexY+1) * self.cardHeight - 5
        self.set_font("Arial", size = 5, style = 'I')
        self.cell(2, 6, txt = f"(v{deck['version']})",ln = 0, align = 'L', border = 0)
        self.cell(60, 6, txt = deck['url'],ln = 0, align = 'R', border = 0, link = deck['url'])

    def drawDecks(self,decks):
        count = 1
        for deck in self.__progress.apply(decks,desc="Create Pdf  "):
            if count > self.nbCardOnPage:
                self.__drawCutLines() # Draw cut lines before to add new one
                count = 1
            if count==1:
                self.add_page()
            self.cardIndexX = (count-1)%self.nbCardOnPageWidth
            self.cardIndexY = (count-1)//self.nbCardOnPageWidth
            self.rect(
                self.pageMarginWidth + self.cardIndexX*self.cardWidth,
                self.pageMarginHeight + self.cardIndexY*self.cardHeight,
                self.cardWidth,
                self.cardHeight,
                style = 'F'
            )
            self.__drawDeck(deck)
            count+=1
        if count>1:
            self.__drawCutLines()


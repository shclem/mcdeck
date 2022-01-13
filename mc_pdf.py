from fpdf import FPDF

class MCPdf(FPDF):
    def __init__(self):
        FPDF.__init__(self, orientation='P', unit='mm', format='A4')
        self.startX = 10
        self.startY = 10
        self.cardIndexX = 0
        self.cardIndexY = 0
        self.cardWidth = 62
        self.cardHeight = 88
        self.columlIndexX = 0
        self.columnWidth = 31
        self.columnMarginTop = 8
        self.columnMarginStart = 2
        self.set_fill_color(230)
        self.add_page()
        self.set_font("Arial", size = 6)

        self.x = self.startX
        self.y = self.startY

    def drawCutLines(self):
        self.set_draw_color(128)
        for xIndex in range(4):
            x = self.startX + xIndex * self.cardWidth
            self.line(x,0, x, 297)
        for yIndex in range(4):
            y = self.startY + yIndex * self.cardHeight
            self.line(0,y,210,y)

    def drawDecks(self,decks):
        count = 0
        for deck in decks:
            self.rect(
                self.startX + self.cardIndexX*self.cardWidth,
                self.startY + self.cardIndexY*self.cardHeight,
                self.cardWidth,
                self.cardHeight,
                style = 'F'
            )
            self.drawDeck(deck)
            count+=1
            if count > 8:
                count = 0
                self.drawCutLines()
                self.add_page()
            self.cardIndexX = count%3
            self.cardIndexY = count//3
        self.drawCutLines()

    def countCards(self, cards):
        count = 0
        for card in cards:
            count += card['quantity']
        return count

    def drawDeck(self,deck):

        totalCount = 0
        for cards in deck['cards'].values():
            totalCount += self.countCards(cards)

        self.x = self.startX + self.cardIndexX * self.cardWidth
        self.y = self.startY + self.cardIndexY * self.cardHeight
        self.set_font("Arial", size = 8, style = 'UB')
        deckName = deck["name"]
        self.cell(62, 6, txt = f"{deckName} ({totalCount})", ln = 0, align = 'C', border = 0)
 
        self.columlIndexX = 0

        self.y = self.startY + self.cardIndexY*self.cardHeight + self.columnMarginTop

        for cardType, cards in deck['cards'].items():
            count = self.countCards(cards)
            if count > 0:
                self.drawDeckSection(cardType, cards, count, totalCount)

        self.x = self.startX + self.cardIndexX * self.cardWidth
        self.y = self.startY + (self.cardIndexY+1) * self.cardHeight - 5
        self.set_font("Arial", size = 5, style = 'I')
        self.cell(2, 6, txt = f"(v{deck['version']})",ln = 0, align = 'L', border = 0)
        self.cell(60, 6, txt = deck['url'],ln = 0, align = 'R', border = 0, link = deck['url'])

    def drawDeckSection(self,title,cards,count,totalCount):

        self.x = self.startX + self.cardIndexX*self.cardWidth + self.columlIndexX*self.columnWidth

        if (self.y-self.startY-self.cardIndexY*self.cardHeight) > self.cardHeight - 13:
            self.columlIndexX = 1
            self.y = self.startY + self.cardIndexY*self.cardHeight + self.columnMarginTop
            self.x = self.startX + self.cardIndexX*self.cardWidth + self.columlIndexX*self.columnWidth

        self.set_font("Arial", size = 6, style = 'B')
        self.cell(20, 3, txt = f"{title} ({count})",ln = 2, align = 'L')

        self.x = self.startX + self.cardIndexX*self.cardWidth + self.columlIndexX*self.columnWidth + self.columnMarginStart
        self.y += 0.7

        self.set_font("Arial", size = 6)
        cards.sort(key=lambda card: 'a' if card['icon']=='resources/basic.png' else card['icon']) 
        for card in cards:
            if (self.y-self.startY-self.cardIndexY*self.cardHeight) > self.cardHeight - 8:
                self.columlIndexX = 1
                self.y = self.startY + self.cardIndexY*self.cardHeight + self.columnMarginTop
                self.x = self.startX + self.cardIndexX*self.cardWidth + self.columlIndexX*self.columnWidth + self.columnMarginStart

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

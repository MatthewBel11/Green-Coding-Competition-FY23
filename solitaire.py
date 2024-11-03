from card_elements import Card, Deck, Pile
from codecarbon import EmissionsTracker

with EmissionsTracker() as tracker:
    
    class Game:

        VALUES = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    
        SUITS = { #keys are unicode symbols for suits
            "S" : "B",
            "H" : "R",
            "C" : "B",
            "D" : "R",
        }
    
        # This creates the cars and the play piles
        def __init__(self):
            self.deck = Deck(self.VALUES,self.SUITS)
            self.playPiles = []
            
            # TODO another nested loop
            for i in range(7):
                thisPile = Pile()
                [thisPile.addCard(self.deck.takeFirstCard(flip=False)) for j in range(i+1)]
                thisPile.flipFirstCard()  
                self.playPiles.append(thisPile)
            self.blockPiles = {suit: Pile() for suit in self.SUITS}
            self.deck.cards[0].flip()
       



        def checkCardOrder(self,higherCard,lowerCard):
            suitsDifferent = self.SUITS[higherCard.suit] != self.SUITS[lowerCard.suit]
            valueConsecutive = self.VALUES[self.VALUES.index(higherCard.value)-1] == lowerCard.value
            return suitsDifferent and valueConsecutive
    




        def checkIfCompleted(self):
            deckEmpty = len(self.deck.cards)==0
            pilesEmpty = all(len(pile.cards)==0 for pile in self.playPiles)
            blocksFull = all(len(pile.cards)==13 for suit,pile in self.blockPiles.items())
            return deckEmpty and pilesEmpty and blocksFull
            



        def addToBlock(self, card):
            if card is None:
                return False
            elif len(self.blockPiles[card.suit].cards)>0:
                highest_value = self.blockPiles[card.suit].cards[0].value
                if self.VALUES[self.VALUES.index(highest_value)+1] == card.value:
                    self.blockPiles[card.suit].cards.insert(0,card)
                    return True
                else:
                    return False   
            else: 
                if card.value=="A":
                    self.blockPiles[card.suit].cards.insert(0,card)
                    return True
                else:
                    return False
        


        def takeTurn(self):
                
            # TODO this should probably just store indices, not duplicate objects
            empty_piles, non_empty_piles = [], []
            for pile in self.playPiles:
                if len(pile.cards)==0:
                    empty_piles.append(pile)
                else:
                    non_empty_piles.append(pile)

            #Pre: flip up unflipped pile end cards -> do this automatically
            [pile.cards[0].flip() for pile in non_empty_piles if not pile.cards[0].flipped]

            #1: check if there are any play pile cards you can play to block piles
            for pile in non_empty_piles:
                if self.addToBlock(pile.cards[0]):
                    card_added = pile.cards.pop(0)
                    return True

            first_in_deck = self.deck.getFirstCard()

            #2: check if cards in deck can be added
            if self.addToBlock(first_in_deck):
                card_added = self.deck.takeFirstCard()
                return True
            
            #3: move kings to open piles
            for pile in empty_piles:
                for pile2 in non_empty_piles:
                    if len(pile2.cards)>1 and pile2.cards[0].value == "K":
                        card_added = pile2.cards.pop(0)
                        pile.addCard(card_added)
                        return True
                    
                if first_in_deck is not None and first_in_deck.value == "K":
                    card_added = self.deck.takeFirstCard()
                    pile.addCard(card_added)
                    return True
            
            #4: add drawn card to playPiles
            if first_in_deck is not None:
                for non_empty_pile in non_empty_piles:
                    if self.checkCardOrder(non_empty_pile.cards[0],first_in_deck):
                        card_added = self.deck.takeFirstCard()
                        non_empty_pile.addCard(card_added) 
                        return True

            flipped_card_piles = [pile for pile in non_empty_piles if len(pile.getFlippedCards())]
                            
            #5: move around cards in playPiles
            for i, pile1 in enumerate(flipped_card_piles):
                pile1_flipped_cards = pile1.getFlippedCards()
                for j, pile2 in enumerate(flipped_card_piles):
                    if i == j:
                        continue
                    for transfer_cards_size in range(1,len(pile1_flipped_cards)+1):
                        cards_to_transfer = pile1_flipped_cards[:transfer_cards_size]
                        if self.checkCardOrder(pile2.cards[0],cards_to_transfer[-1]):
                            pile1_downcard_count = len(pile1.cards) - len(pile1_flipped_cards)
                            pile2_downcard_count = len(pile2.cards) - len(pile2.getFlippedCards())
                            if pile2_downcard_count < pile1_downcard_count:
                                [pile2.cards.insert(0,card) for card in reversed(cards_to_transfer)]
                                pile1.cards = pile1.cards[transfer_cards_size:]
                                return True
                            elif pile1_downcard_count==0 and len(cards_to_transfer) == len(pile1.cards):
                                [pile2.cards.insert(0,card) for card in reversed(cards_to_transfer)]
                                pile1.cards = []
                                return True
            return False
        

        def simulate(self):
            self.deck.cache = []
        
            while True:
                turnResult = self.takeTurn()

                if turnResult:
                    self.deck.cache = []
                elif len(self.deck.cards)>0:
                    currentCard = self.deck.cards[0]
                    if not currentCard in self.deck.cache:
                        self.deck.drawCard()
                        self.deck.cache.append(currentCard)
                        return
    

    if __name__ == "__main__":
        thisGame = Game()
        thisGame.simulate()

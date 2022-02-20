#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import os
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import *
import random
import copy
import linecache
from math import floor, ceil

try:
    from PIL import ImageTk, Image 
except ImportError: 
    print("\n\"PIL\" or \"ImageTk\" is missing from your system. \nPlease make sure they are installed and try again.\n")
    exit()   

preferences = {
    "options": ["Normal Blackjack Mode", "Statistics Mode"],
    "choices": [0, 0]
}

colors= {
    "bgcolor": ["#222222", "#000000", "#C0C0C0"],
    "highlights": ["#ff9000", "#00FFFF", "#00FF00", "#f600f6"],
    "fgcolor": "#FFFFFF"
}

font = {
    "font_family": "Arial", "title": 18, "text": 10, "note": 7
}

def create_main_dirs():
    names = ["configs", "assets"]
    for name in names:
        path = str(Path().absolute()) + '/'+ name
        if os.path.exists(path) is False: 
            os.mkdir(path)

def error_msg(type, filename, path, ext):
    msg = type + " \"" + filename + "\" could not be loaded. Make sure " + type.lower() + " is present in %projectfolder%/" + path + " and try again."
    messagebox.showerror(type + " Loading Failed", msg)
    if(ext == "exit"):
        exit()
    else:
        pass

def image_loader(img_path, w, h):
    try:
        raw = Image.open(img_path)
        resized = raw.resize((w, h), Image.ANTIALIAS)
        final = ImageTk.PhotoImage(resized)
        return final
    except:
        parts = img_path.split("/")
        filename = parts[-1]
        path=""
        for p in parts[:-1]:
            path += str(p) + "/"
        error_msg("Image", filename, path, "exit")


class Configuration():
    def __init__(self):
        self.configs_path = "configs/prefConfigs"

    def error(self):
        parts = self.configs_path.split("/")
        filename = parts[1]
        path = parts[0]
        error_msg("File", filename, path, None)

    def read_configs(self, line):
        # [:-1] ignore the '\n' at the end of each line
        l = linecache.getline(self.configs_path, line + 1)[:-1]
        if l == '':
            return None
        else:
            return int(l)

    def write_configs(self, line, output):
        create_main_dirs()
        try:
            with open(self.configs_path, 'r') as file:
                data = file.readlines()
            data[line] = str(output) + '\n'

            # Replace line
            with open(self.configs_path, 'w') as file:
                file.writelines(data)
        except:
            pass

    def load_configs(self):
        for i in range(len(preferences["choices"])):
            if(self.read_configs(i) == None):
                self.error()
            else:
                preferences["choices"][i] = self.read_configs(i)


class Cards():
    def __init__(self):
        self.figures = ["J", "Q", "K"]
        self.num_cards = [i for i in range(2, 11)]
        self.card_val = self.num_cards + self.figures + ["A"]
        self.group = ["H", "S", "C", "D"]
        self.deck= []
        self.create_deck()

    def create_deck(self):
        self.deck= []
        for i in self.group:
            for j in self.card_val:
                self.deck.append([i,j])

    def suffle_deck(self, cheat):
        random.shuffle(self.deck)
        if (cheat == 1):
            # Interfere with suffling mode
            # Recurse until player starts with figure or 10 and dealer never with figure or 10
            while((self.deck[0][1] not in self.figures + [10]) or (self.deck[1][1] in self.figures + [10])):
                self.suffle_deck(cheat)

        return self.deck


class Player():
    def __init__(self, parent, name):
        self.parent = parent
        self.player_cards = []
        self.cards_sum = 0
        self.ace_count = 0
        self.reduced_aces = 0
        self.card_img=[]
        self.card_labels = []
        self.card_img_path = "assets/images/cards/"
        if (name == "d"):
            self.posy = 0.12
        else:
            self.posy = 0.64
        self.posx = 0.22

    def display_card(self, card):
        name = str(card[0]) + '_' + str(card[1]) + ".png"
        self.card_img.append(image_loader(self.card_img_path + name, 70, 100))
        self.card_labels.append(tk.Label(self.parent, image=self.card_img[-1], width=66, height=90))
        self.card_labels[-1].place(relx=self.posx, rely=self.posy)
        self.posx +=0.085 

    def calc_sum(self, card_val):
        if (card_val in ["J", "Q", "K"]):
            self.cards_sum += 10
        elif(card_val == "A"):
            self.cards_sum += 1 #11
        else:
            self.cards_sum += card_val
    '''
    def ace_counter(self):
        self.ace_count = 0
        for card in self.player_cards:
            if card[1] == "A":
                self.ace_count +=1

    # Ace value can either be 1 or 11
    def decide_ace_value(self, limit):
        self.ace_counter()
        if (self.cards_sum > limit):
            i = 0
            while (self.cards_sum > limit and not(i > len(self.player_cards)-1) and self.reduced_aces < self.ace_count):
                if self.player_cards[i][1] == "A":
                    self.cards_sum -= 10
                    self.reduced_aces +=1
                i += 1
    '''
    def append_card(self, deck, limit):
        self.player_cards.append(deck.pop(0))
        self.calc_sum(self.player_cards[-1][1])
        #self.decide_ace_value(limit)
        self.display_card(self.player_cards[-1])

    # Draw to 16 and stand on 17
    def dealer_mode(self, deck):
        limit = 16
        while(self.cards_sum < limit):
            self.append_card(deck, limit)

    def __del__(self):
        try:
            for l in self.card_labels:
                l.destroy()
        except:
            pass


class Statistics(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.stats_board = None
        CHIP_VAL = 100 
        self.data = {"stats": ["Total Rounds: ", "Dealer Wins: ", "Draws: ", "Player Wins: ", "Player Chips ("+str(CHIP_VAL)+"$): \n"],
                     "stats_val": [0,0,0,0,20],
                     "stats_labels": []}

    def create_stats_board(self, r, c):
        self.stats_board = tk.Frame(self.parent, background=colors["bgcolor"][0])
        self.stats_board.grid(row=r, column=c , sticky='n')
        for l in range(len(self.data["stats"])):
            self.data["stats_labels"].append(tk.Label(self.stats_board, text=self.data["stats"][l] + str(self.data["stats_val"][l]), background=colors["bgcolor"][0], foreground=colors["fgcolor"], font=(font["font_family"], font["text"])))
            self.data["stats_labels"][-1].pack(ipady=5, anchor='w')

    def update_stats_board(self):
        for l in range(len(self.data["stats"])):
            self.data["stats_labels"][l].configure(text = self.data["stats"][l] + str(self.data["stats_val"][l]))

    def clear_stats_board(self):
        self.data["stats_val"] = [0,0,0,0,20]
        self.update_stats_board()


class GameControls(tk.Frame):
    def __init__(self, parent, stats):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.data = {"text": ["New Round", "Hit Me", "Stand", "Place Bet"],
                     "ctrl_attr":['-', '+'],
                     "bet_chip_num": 1,
                     "buttons": [], "bet_controls": []}
        self.colspan = len(self.data["text"])+1
        self.chip_num_lbl = None
        self.stats = stats

    def bet_field(self):
        bet_field = tk.Frame(self.parent, background=colors["bgcolor"][0])
        bet_field.grid(row= 4, column=self.colspan-1)
        self.chip_img = image_loader("assets/images/chips/BlackChip.png", 30, 30)
        tk.Label(bet_field, image=self.chip_img , background=colors["bgcolor"][0]).pack(side='left')
        self.chip_num_lbl = tk.Label(bet_field, text=self.data["bet_chip_num"], background=colors["bgcolor"][0], foreground=colors["fgcolor"], font=(font["font_family"], font["text"]))
        self.chip_num_lbl.pack(side='left', padx=10)
        for b in range(len(self.data["ctrl_attr"])):
            self.data["bet_controls"].append(Button(bet_field, text=self.data["ctrl_attr"][b], width=2, command = lambda x=b: self.bet_val(self.data["ctrl_attr"][x])))
            self.data["bet_controls"][-1].pack(side='left', padx=2)

    def bet_val(self, action):
        if (action == '-' and self.data["bet_chip_num"] > 1):
            a = -1
        elif (action == '+' and self.data["bet_chip_num"]< self.stats.data["stats_val"][4]): 
            a = 1
        else:
            a = 0
        self.data["bet_chip_num"] += a
        self.chip_num_lbl.configure(text=self.data["bet_chip_num"])

    def create_controls_bar(self):
        for b in range(len(self.data["text"])):
            self.data["buttons"].append(Button(self.parent, text=self.data["text"][b], width=15))
            self.data["buttons"][-1].grid(row=4, column= b, padx=20, ipady=5, pady=18, sticky='ew')
            self.bet_field()

    def controls_state(self, btn_lst, state):
        if (btn_lst == "all"):
            for btn in self.data["buttons"]:
                btn['state'] = state  
            for btn in self.data["bet_controls"]:
                        btn['state'] = state 
        else:
            for btn in btn_lst:
                if btn in self.data["text"]:
                    i = self.data["text"].index(btn)
                    self.data["buttons"][i]['state'] = state
                if btn == "Place Bet":
                    for btn in self.data["bet_controls"]:
                        btn['state'] = state
                else:
                    pass
            

class GameMode():
    def __init__(self, parent, outcome, stats, scroll_frame, controls):
        self.parent = parent
        self.cards = Cards()
        self.deck = []
        self.stats = stats
        self.outcome = outcome
        self.scroll_frame = scroll_frame
        self.controls = controls
        self.bet = 1

    def empty(self):
        pass
        
    def decide_winner(self):
        if (((self.player1.cards_sum <= 21) and (self.player1.cards_sum > self.dealer.cards_sum)) or self.dealer.cards_sum >21):
            self.outcome.configure(text = "Player won!")
            i = 3
        elif (self.player1.cards_sum == self.dealer.cards_sum):
            self.outcome.configure(text = "Draw!")
            i = 2
        else:
            self.outcome.configure(text = "Dealer won!")
            i = 1
        return i

    def player_lost(self):
        if (self.player1.cards_sum > 21):
            self.outcome.configure(text = "Dealer won!")
            self.stats.data["stats_val"][0] += 1
            self.stats.data["stats_val"][1] += 1  
            self.stats.data["stats_val"][4] -= self.bet
            self.stats.update_stats_board()
            self.controls.controls_state("all", "disabled")
            self.controls.controls_state(["New Round"], "normal")
            self.controls.data["buttons"][0].bind("<Button-1>", lambda e: self.new_round())
            self.controls.data["buttons"][1].bind("<Button-1>", lambda e: self.empty())
            self.controls.data["buttons"][2].bind("<Button-1>", lambda e: self.empty())
            self.controls.data["bet_chip_num"] == 1
            self.controls.chip_num_lbl.configure(text = 1)

    def gameplay(self, deck):
        try:
            self.player1 = Player(self.parent, "p")
            self.dealer = Player(self.parent, "d")
            self.player1.append_card(deck, 16)
            self.dealer.append_card(deck, 16)
            self.player1.dealer_mode(deck)
            if (self.player1.cards_sum <= 21):
                self.dealer.dealer_mode(deck)
            else:
                pass
            self.r = self.decide_winner()
        except:
            pass

    def new_round(self):
        self.controls.data["buttons"][0].bind("<Button-1>", lambda e: self.empty())
        self.controls.controls_state(["New Round"], "disabled")
        self.outcome.configure(text = "")
        if (self.stats.data["stats_val"][4] == 0):
            messagebox.showerror("Game Over", "Can't start new round with no chips to bet.\nCome back later with some chips to play.")
            exit()
        self.deck = []
        self.cards.create_deck()
        self.deck = self.cards.suffle_deck(preferences["choices"][1])
        self.player1 = Player(self.parent, "p")
        self.dealer = Player(self.parent, "d")
        self.controls.data["buttons"][3].bind("<Button-1>", lambda e: self.place_bet())
        self.controls.controls_state(["Place Bet"], "normal")

    def place_bet(self):
        self.controls.data["buttons"][3].bind("<Button-1>", lambda e: self.empty())
        self.controls.controls_state(["Place Bet"], "disabled")
        self.bet = self.controls.data["bet_chip_num"]
        self.player1.append_card(self.deck, 21)
        self.player1.append_card(self.deck, 21)
        self.dealer.append_card(self.deck, 21)
        self.controls.data["buttons"][1].bind("<Button-1>", lambda e: self.hit_me())
        self.controls.data["buttons"][2].bind("<Button-1>", lambda e: self.stand())
        self.controls.controls_state(["Hit Me", "Stand"], "normal")

    def hit_me(self):
        self.player1.append_card(self.deck, 21)
        self.player_lost()

    def stand(self):
        self.dealer.dealer_mode(self.deck)
        self.r = self.decide_winner()
        if (self.r == 1):
            self.stats.data["stats_val"][4] -= self.bet
        elif (self.r == 3):
            self.stats.data["stats_val"][4] += floor(3/2 * self.bet)
        self.stats.data["stats_val"][0] += 1
        self.stats.data["stats_val"][self.r] += 1   
        self.stats.update_stats_board()
        self.controls.controls_state("all", "disabled")
        self.controls.controls_state(["New Round"], "normal")
        self.controls.data["buttons"][0].bind("<Button-1>", lambda e: self.new_round())
        self.controls.data["buttons"][1].bind("<Button-1>", lambda e: self.empty())
        self.controls.data["buttons"][2].bind("<Button-1>", lambda e: self.empty())
        self.controls.data["bet_chip_num"] == 1
        self.controls.chip_num_lbl.configure(text = 1)
   
    def normal_blackjack_mode(self):
        for b in self.controls.data["buttons"]:
            b.bind("<Button-1>", lambda e: self.empty())
        self.controls.controls_state("all", "disabled")
        self.controls.controls_state(["New Round"], "normal")
        self.outcome.configure(text = "")
        self.scroll_frame.remove_buttons()
        self.scroll_frame.destroy_last_game()
        self.scroll_frame.button_list = []
        self.scroll_frame.history_deck = []
        self.stats.clear_stats_board()
        self.player1 = Player(self.parent, "p")
        self.dealer = Player(self.parent, "d")
        self.controls.data["buttons"][0].bind("<Button-1>", lambda e: self.new_round())
        
    def statistics_mode(self):
        for b in self.controls.data["buttons"]:
            b.bind("<Button-1>", lambda e: self.empty())
        self.controls.controls_state("all", "disabled")
        self.scroll_frame.remove_buttons()
        self.scroll_frame.button_list = []
        self.scroll_frame.history_deck = []
        self.stats.clear_stats_board()
        for i in range(100):
            self.deck = []
            self.cards.create_deck()
            self.deck = self.cards.suffle_deck(preferences["choices"][1])
            # Using copy to avoid creating reference to the object
            self.scroll_frame.history_deck.append(copy.copy(self.deck))
            self.gameplay(self.deck)
            self.stats.data["stats_val"][0] += 1
            self.stats.data["stats_val"][self.r] += 1   
            self.stats.update_stats_board()
            self.scroll_frame.append_button(i)
        self.player1 = Player(self.parent, "p")
        self.dealer = Player(self.parent, "d")
        self.outcome.configure(text = "")
    
    def selected_game_mode(self):
        if (preferences["choices"][0] == 0):
            self.normal_blackjack_mode()
        elif (preferences["choices"][0] == 1):
            self.statistics_mode()


class ScrollFrame(tk.Frame):
    def __init__(self, parent, canvas_w, canvas_h, outcome):
        tk.Frame.__init__(self, parent)  
        self.canvas_w = canvas_w 
        self.button_list = []
        self.history_deck = []
        self.game = GameMode(parent, outcome, None, None, None)

        self.canvas = tk.Canvas(self, borderwidth=0, background=colors["bgcolor"][2], width=canvas_w, height=canvas_h)      
        # Place a frame on the canvas, this frame will hold the child widgets     
        self.viewPort = tk.Frame(self.canvas, background=colors["bgcolor"][2])                    
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)   
        # Attach scrollbar action to scroll of canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)                            

        self.scrollbar.pack(side="right", fill="y")                                     
        self.canvas.pack(side="left", fill='y')                              
        self.canvas_window = self.canvas.create_window((4,4), window=self.viewPort, anchor="nw", tags="self.viewPort") #add view port frame to canvas

        # Bind an event whenever the size of the viewPort frame changes.
        self.viewPort.bind("<Configure>", self.onFrameConfigure)  
        # Bind an event whenever the size of the canvas frame changes.  
        self.canvas.bind("<Configure>", self.onCanvasConfigure)    

        # Perform an initial stretch on render, otherwise the scroll region has a tiny border until the first resize
        self.onFrameConfigure(None)                                 

    # Reset the scroll region to encompass the inner frame
    def onFrameConfigure(self, event):                                              
        self.canvas.configure(scrollregion=self.canvas.bbox("all")) 
    
    # Reset the canvas window to encompass inner frame when required
    def onCanvasConfigure(self, event):
        canvas_width = self.canvas_w
        self.canvas.itemconfig(self.canvas_window, width = canvas_width)

    def button_com(self, g):
        # Using deepcopy to avoid creating reference to the nested(!) object
        tmp = copy.deepcopy(self.history_deck)
        self.game.gameplay(tmp[g])

    def append_button(self, i):
        self.button_list.append(Button(self.viewPort, text="Game " + str(i+1), command= lambda g=i: self.button_com(g)))
        self.button_list[-1].pack(side="top", fill="x")

    def remove_buttons(self):
        for b in self.button_list:
            b.destroy()

    def destroy_last_game(self):
        self.game.gameplay([])


class RadioBar(tk.Frame):
    def __init__(self, parent, start_index, title, gamemode):
        tk.Frame.__init__(self, parent)
        self.i = self.s = start_index
        self.title = title
        self.gamemode = gamemode
        self.var = tk.StringVar()
        self.style = Style()

    def create_bar(self, options, active_btn):
        self.style.configure('TRadiobutton', background=colors["bgcolor"][0], foreground=colors["fgcolor"])
        radiobtns=[]
        for opt in options:
            radiobtns.append(Radiobutton(self, text = opt, value = self.i, variable= self.var, style='TRadiobutton', command= lambda: self.selected()))
            radiobtns[-1].pack(side = 'left', ipadx=5, ipady=5)
            self.i +=1
        radiobtns[active_btn].invoke()

    def selected(self):
        selection = int(self.var.get())-self.s
        conf = Configuration() 
        preferences["choices"][0] = selection
        conf.write_configs(0, selection)
        self.title.configure(text = preferences["options"][selection])
        self.gamemode.selected_game_mode()


class CheckButton(tk.Frame):
    def __init__(self, parent, mode):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.var = tk.IntVar()
        self.chk_btn = None
        self.gamemode = mode

    def create_chk_btn(self, txt, fnt):
        style = Style()
        style.configure("TCheckbutton", background=colors["bgcolor"][0], foreground=colors["fgcolor"], font=fnt, variable= self.var)
        self.chk_btn = Checkbutton(self.parent, text = txt, style="TCheckbutton", command= lambda: self.selected())
        self.chk_btn.pack()
        # To toggle checkbutton in code, first clear the "alternate" flag
        self.chk_btn.state(['!alternate'])

        if preferences["choices"][1] == 1:
            self.chk_btn.state(['selected'])
        else:
            self.chk_btn.state(['!selected'])

    def selected(self):
        if self.chk_btn.instate(['selected']):
            selection = 1
        else: 
            selection = 0

        conf = Configuration()
        preferences["choices"][1] = selection
        conf.write_configs(1, selection)
        self.gamemode.selected_game_mode()


class NewWindow(tk.Toplevel):
    def __init__(self, btn, dim, title, lbl, game):
        tk.Toplevel.__init__(self, None)
        self.geometry(dim)
        self.title(title)
        self.resizable(False, False)
        self.configure(background=colors["bgcolor"][0])
        self.lbl = lbl
        self.gamemode = game
        try:
            btn['state'] = 'disabled'
        except:
            pass
        self.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(btn))

    def on_closing(self, btn):
        try:
            btn['state'] = 'normal'
        except:
            pass
        self.destroy()

    def display_pref(self):
        radio_bar = RadioBar(self, 1, self.lbl, self.gamemode)
        radio_bar.create_bar(preferences["options"],  preferences["choices"][0])
        radio_bar.pack(padx = 10, pady = 10)
        chk_btn = CheckButton(self, self.gamemode)
        chk_btn.create_chk_btn("Interfere with deck suffling (Statistics Mode)", (font["font_family"], font["text"]))
        

def gui():
    root = tk.Tk()
    root.title("Simple Blackjack (Project 4)")
    root.geometry("950x580")
    try:
        root.iconphoto(True, tk.PhotoImage(file='assets/images/icon.png'))
    except:
        pass
    root.resizable(False, False)
    root.configure(background=colors["bgcolor"][0])

    conf = Configuration()
    conf.load_configs()
    del conf

    stats = Statistics(root)
    stats.create_stats_board(1, 5)

    controls = GameControls(root, stats)
    controls.create_controls_bar()
    
    mode_title = tk.Label(root, text=preferences["options"][preferences["choices"][0]], background = colors["bgcolor"][0], foreground=colors["fgcolor"], font=(font["font_family"], font["title"]))
    mode_title.grid(row=0, column=0, columnspan=ceil(controls.colspan/2), ipady=10)

    outcome = tk.Label(root, text="", background = colors["bgcolor"][0], foreground=colors["fgcolor"], font=(font["font_family"], font["title"]))
    outcome.grid(row=0, column=ceil(controls.colspan/2), columnspan=floor(controls.colspan/2), ipady=10)

    table_img = image_loader("assets/images/TableLayout.png", 800, 450)
    table = tk.Label(root, image = table_img, background = colors["bgcolor"][0])
    table.grid(row=1, column=0, rowspan=3, columnspan=controls.colspan)

    stats_ttl = tk.Label(root, text="Stats", background = colors["bgcolor"][0],  foreground=colors["fgcolor"], font=(font["font_family"], font["title"]), width=10)
    stats_ttl.grid(row=0, column=controls.colspan)

    history_ttl = tk.Label(root, text="History", background = colors["bgcolor"][0], foreground=colors["fgcolor"], font=(font["font_family"], font["title"]))
    history_ttl.grid(row=2, column=controls.colspan, )
    scroll_frame = ScrollFrame(root, 120, 210, outcome)
    scroll_frame.grid(row=3, column= controls.colspan, sticky="ns")

    pref_btn = Button(root, text ="Preferences", width=15, command=lambda: NewWindow(pref_btn, '350x100', 'Preferences', mode_title, game).display_pref())
    pref_btn.grid(row=4, column= controls.colspan, ipady=5)

    game = GameMode(root, outcome, stats, scroll_frame, controls)
    game.selected_game_mode()

    root.mainloop()


if __name__ == "__main__":
    gui()


#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import random
import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import *

try:
    from PIL import ImageTk, Image 
except ImportError: 
    print("\n\"PIL\" or \"ImageTk\" is missing from your system. \nPlease make sure they are installed and try again.\n")
    exit() 


preferences={
    "rows": 8, "cols": 8, "square_size": 50, #px
    "positions": 100, "num_of_pieces": 3, "margin": 2*" "
}

colors={
    "bgcolor": "#222222", "bgcolor2": "#C0C0C0", "fgcolor": "#FFFFFF",
    "square1": "#FFFFFF", "square2": "#8B4513", "outline": "#000000"
}

font={
    "font_familly": "Arial", "title": 16, "text": 13
}


def error_msg(type, filename, path, ext):
    msg = type + " \"" + filename + "\" could not be loaded. Make sure " + type.lower() + " is present in %projectfolder%/" + path + " and try again."
    messagebox.showerror(type + " Loading Failed", msg)
    if(ext == "exit"):
        exit()
    else:
        pass


class CanTakeDown:
    def __init__(self, a_r, a_c, op_r, op_c, oth_r, oth_c):
        attacker_row = a_r 
        attacker_col = a_c
        opponent_row = op_r
        opponent_col =  op_c
        other_row = oth_r
        other_col = oth_c

        # Distances
        self.d1 = attacker_row - other_row
        self.d2 = attacker_col - other_col
        self.d3 = attacker_row - opponent_row
        self.d4 = attacker_col - opponent_col

    def bishop(self):
        if (abs(self.d3) == abs(self.d4)):

            # abs(d1) == abs(d2): attacker and the other piece are on the same diagonal
            # abs(d1 < d3): attacker is closer to the other piece in the same diagonal
            # d1 * d3 > 0: both the opponent and the other piece are on the same side
            if (abs(self.d1) == abs(self.d2) and abs(self.d1) < abs(self.d3) and self.d1 * self.d3 > 0):
                return False
            else:
                return True

    def rook(self):
        # Rook and opponent are on the same column
        if (self.d4 == 0):
           
            # abs(d1) < abs(d3): attacker is closer to the other piece in the same column
            # d1 * d3 > 0: both the opponent and the other piece are either on the top or bottom side of the attacker  
            if (self.d2 == 0 and abs(self.d1) < abs(self.d3) and self.d1 * self.d3 > 0):
                return False
            else:
                return True

        # Rook and opponent are on the same row
        elif (self.d3 == 0):

            # abs(d2) < abs(d3): attacker is closer to the other piece in the same column
            # d2 * d4 > 0: both the opponent and the other piece are either on the left or right side of the attacker  
            if (self.d1 == 0 and abs(self.d2) < abs(self.d4) and self.d2 * self.d4 > 0):
                return False
            else:
                return True

    def queen(self):
        if(not self.bishop()):
            if(not self.rook()):
                return False
            else:
                return True
        else:
            return True


class ChessBoard(tk.Frame):
    def __init__(self, parent, rows, cols, size):   
        self.rows = rows
        self.cols = cols
        self.size = size
        self.color1 = colors["square1"]
        self.color2 = colors["square2"]

        board_width = cols * size
        board_height = rows * size

        tk.Frame.__init__(self, parent)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0,
        width=board_width, 
        height=board_height, background=colors["bgcolor"])

        self.canvas.grid(row = 0, column = 1, columnspan = 2)

        # This binding will cause a refresh if the user interactively changes the window size
        self.canvas.bind("<Configure>", self.refresh)   

    def add_piece(self, img, row, column):  
        x, y = self.place_piece(self.rows - row, column - 1)  
        return self.canvas.create_image(x, y, image=img, tags=("piece"), anchor="c")
        
    def place_piece(self, row, column):            
        x = (column * self.size) + int(self.size / 2)
        y = (row * self.size) + int(self.size / 2)
        return x, y

    def move_piece(self, item, row, column):
        coords = self.canvas.coords(item)
        x, y = self.place_piece(self.rows - row, column - 1) 
        return self.canvas.move(item, x - coords[0], y-coords[1])

    def duplicate_check(self, lst1, lst2):
        pairs = []
        if(len(lst1) != 0):
            for i in range(len(lst1)):
                x = lst1[i] 
                y = lst2[i]
                pairs.append([x,y])
        else:
            return True

        contains_duplicates = any(pairs.count(element) > 1 for element in pairs)

        if(contains_duplicates):
            return True
        else:
            return False

    def generate_random_pos(self, num_of_items):
        rand_col = []
        rand_row = []
        while(True):
            if(self.duplicate_check(rand_row, rand_col)): 
                rand_col = []
                rand_row = []
                for i in range (num_of_items):
                    rand_col.append(random.randint(1, self.cols))
                    rand_row.append(random.randint(1, self.rows))    
            else:
                break

        return rand_row, rand_col

    # Redraw the board, possibly in response to window being resized
    def refresh(self, event): 
        xsize = int((event.width-1) / self.cols)
        ysize = int((event.height-1) / self.rows)
        self.size = min(xsize, ysize)
        self.canvas.delete("square")
        color = self.color2
        for row in range(self.rows):
            color = self.color1 if color == self.color2 else self.color2
            for col in range(self.cols):
                x1 = (col * self.size)
                y1 = (row * self.size)
                x2 = x1 + self.size
                y2 = y1 + self.size
                self.canvas.create_rectangle(x1, y1, x2, y2, outline=colors["outline"], fill=color, tags="square")
                color = self.color1 if color == self.color2 else self.color2

        # Brings piece to foreground
        self.canvas.tag_raise("piece")\
        # Sends board square to background
        self.canvas.tag_lower("square")

    def load_pos(self, num, r, c, board_title, score, pieces):
        board_title.config(text="Position " + str(num + 1) + "  (W - B): " + str(score[num][0]) + "-" + str(score[num][1]))
        i=0
        for p in pieces:
            self.move_piece(p, r[i], c[i])
            i += 1

    def get_score(self, r, c, score):
        w = b = 0
        q_ind = 0
        b_ind = 1
        r_ind = 2

        bishop_to_queen = CanTakeDown(r[q_ind], c[q_ind], r[b_ind], c[b_ind], r[r_ind], c[r_ind])
        rook_to_queen = CanTakeDown(r[q_ind], c[q_ind], r[r_ind], c[r_ind], r[b_ind], c[b_ind])
        queen_to_bishop = CanTakeDown(r[b_ind], c[b_ind], r[q_ind], c[q_ind], r[r_ind], c[r_ind])
        queen_to_rook = CanTakeDown(r[r_ind], c[r_ind], r[q_ind], c[q_ind], r[b_ind], c[b_ind])

        # Queen attacks Bishop
        if queen_to_bishop.queen():
            b = b + 1
        # Queen attacks Rook
        if queen_to_rook.queen():
            b = b + 1
        # Bishop attacks Queen
        if bishop_to_queen.bishop():
            w = w + 1
        # Rook attacks Queen
        if rook_to_queen.rook():
            w = w + 1

        score.append([w,b])

        return w, b


class ChessPiece():
    def piece_img(name, w, h):
        src = 'assets/images/'
        try:
            img = Image.open(src + name + '.png')
        except:
            error_msg("Image", name + ".png", src, "exit")
        img = img.resize((w, h), Image.ANTIALIAS)
        piece = ImageTk.PhotoImage(img)
        return piece


class ScrollFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)   

        self.canvas = tk.Canvas(self, borderwidth=0, background=colors["bgcolor2"], width=120, height=300)      
        # Place a frame on the canvas, this frame will hold the child widgets     
        self.viewPort = tk.Frame(self.canvas, background=colors["bgcolor2"])                    
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)   
        # Attach scrollbar action to scroll of canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)                            

        self.scrollbar.pack(side="right", fill="y")                                     
        self.canvas.pack(side="left")                              
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
        canvas_width = 120
        self.canvas.itemconfig(self.canvas_window, width = canvas_width)


def gui():
    root = tk.Tk()
    root.title("Random Chess Positions (Project 6)")
    try:
        root.iconphoto(False, tk.PhotoImage(file='assets/images/icon.png'))
    except:
        pass
    root.resizable(False, False)
    root.configure(background=colors["bgcolor"])

    board = ChessBoard(root, preferences["rows"], preferences["cols"], preferences["square_size"])
    board_title = tk.Label(root, text = "Click a button to load position & score", bg=colors["bgcolor"], fg=colors["fgcolor"], font=(font["font_familly"], font["title"]))
    score = tk.Label(root, text = "Overall Score" + preferences["margin"], bg=colors["bgcolor"], fg=colors["fgcolor"], font=(font["font_familly"], font["title"]))
    history = tk.Label(root, text = "Position History" + preferences["margin"], bg=colors["bgcolor"], fg=colors["fgcolor"], font=(font["font_familly"], font["title"]))
    
    board_title.grid(row = 0, column = 0, pady = 8, columnspan = 9)
    score.grid(row = 0, column = 10, pady = 8, columnspan=2)
    board.grid(row = 1, column = 1, padx= 6, columnspan = 8, rowspan = 8)
    history.grid(row = 2, column = 10, columnspan=2)

    row_label=[]
    col_label =[]
    ch = 'A'
    for i in range (preferences["rows"]):
        row_label.append(tk.Label(root, text = preferences["margin"] + str(i+1), bg=colors["bgcolor"], fg=colors["fgcolor"]))
        col_label.append(tk.Label(root, text = ch, bg=colors["bgcolor"], fg=colors["fgcolor"]))
        row_label[i].grid(row = 8-i, column = 0, pady = 2)
        col_label[i].grid(row = 9, column = i+1)
        
        ch_index = ord(ch) + 1
        ch = chr(ch_index)
        
    button_frame = ScrollFrame(root)
    button_frame.grid(row=3, column= 10, rowspan=6, sticky="ns")

    bq_img = ChessPiece.piece_img("BQ", 45, 45)
    wb_img = ChessPiece.piece_img("WB", 45, 45)
    wr_img = ChessPiece.piece_img("WR", 39, 43)

    bq = board.add_piece(bq_img, 0, 0)
    wb = board.add_piece(wb_img, 0, 0)
    wr = board.add_piece(wr_img, 0, 0)  

    pieces = [bq, wb, wr]
    score = []
    overall_w_score = 0
    overall_b_score = 0
    buttons = []
    r_pos_lst = []
    c_pos_lst = []
    
    for i in range(preferences["positions"]):
        row_pos, col_pos = board.generate_random_pos(preferences["num_of_pieces"])
        r_pos_lst.append(row_pos)
        c_pos_lst.append(col_pos)

        w_s, b_s = board.get_score(r_pos_lst[i], c_pos_lst[i], score)
        overall_w_score += w_s
        overall_b_score += b_s

        # The use of a lambda function makes it possible to pass arguments to the attached command function  
        # It is also convenient to get the generated button's index in each round and reuse it later (otherwise all buttons get the index of the last one)
        buttons.append(Button(button_frame.viewPort, text="Position " + str(i+1), command= lambda btn_num=i: board.load_pos(btn_num, r_pos_lst[btn_num], c_pos_lst[btn_num], board_title, score, pieces)))
        buttons[-1].pack(side="top", fill="x")

    overall = tk.Label(root, text = "(W - B): "+ str(overall_w_score) +"-" + str(overall_b_score), bg=colors["bgcolor"], fg=colors["fgcolor"], font=(font["font_familly"], font["text"]))
    overall.grid(row=1, column=10, )

    root.mainloop()


if __name__ == "__main__":
    gui()

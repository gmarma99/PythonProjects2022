#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import os
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import *
import webbrowser
import linecache
import collections
from math import log, floor
import threading

try:
    from PIL import ImageTk, Image 
    import imageio
    import requests
except ImportError: 
    print("\n\"PIL\" or \"ImageTk\" or \"imageio\" or \"requests\" is missing from your system. \nPlease make sure they are installed and try again.\n")
    exit()   


DRAND_NUM_SYSTEM = 16  # Hexadecimal
MAX_LATEST_NUMBERS_RANGE = 300

preferences= {
    "num_systems": ['Default*', 'Binary', 'Decimal', 'Hexadecimal'],
    "lamp_colors": ['Orange','Blue', 'Green', 'Purple'],
    # Default values if importing configuration fails are: 0 (Number System), 0 (Lamp Color), 20 (Slider Value)
    "choices": [0, 0, 20]
}

colors= {
    "bgcolor": ["#222222", "#000000", "#C0C0C0"],
    "highlights": ["#ff9000", "#00FFFF", "#00FF00", "#f600f6"],
    "fgcolor": "#FFFFFF"
}

font = {
    "font_family": "Arial", "title": 15, "text": 12, "note": 7
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


class VideoPlayer():
    def __init__(self, vid_name):
        self.path = "assets/videos/"
        try:
            self.change(vid_name)
        except:
            error_msg("Video", vid_name, self.path, "exit")
        
    def change(self, vid_name):
        self.video_name = str(Path().absolute()) + '/' + self.path + vid_name
        self.video, self.delay = self.load()
    
    def load(self):
        vid = imageio.get_reader(self.video_name)
        frame_delay = int(600 / vid.get_meta_data()['fps'])
        return vid, frame_delay

    def stream(self, container):
        # Get next frame
        try:
            image = self.video.get_next_data()
        # If last frame is loaded create loop 
        except:
            # Close old video
            self.video.close()
            # Reload video
            self.video, self.delay = self.load()
            # Start streaming again
            image = self.video.get_next_data()

        container.after(self.delay, lambda: self.stream(container))
        frame_image = ImageTk.PhotoImage(Image.fromarray(image))
        container.config(image=frame_image)
        container.image = frame_image


class RadioBar(tk.Frame):
    def __init__(self, parent, start_index, bg, lbl):
        tk.Frame.__init__(self, parent)
        self.i = self.s = start_index
        self.bg = bg
        self.lbl = lbl
        self.var = tk.StringVar()
        self.style = Style()

    def create_bar(self, options, active_btn):
        self.style.configure('TRadiobutton', background=colors["bgcolor"][0], foreground=colors["fgcolor"])
        radiobtns=[]
        for opt in options:
            radiobtns.append(Radiobutton(self, text = opt, value = self.i, variable= self.var, style='TRadiobutton', command= lambda: self.selected()))
            radiobtns[-1].pack(side = 'left')
            self.i +=1
        radiobtns[active_btn].invoke()

    def selected(self):
        selection = int(self.var.get())-self.s
        conf = Configuration()
        if(self.s==1): 
            preferences["choices"][0] = selection
            conf.write_configs(0, selection)
        elif(self.s==5):
            preferences["choices"][1] = selection 
            conf.write_configs(1, selection)
            vid = preferences["lamp_colors"][preferences["choices"][1]] + ".mp4"
            self.bg.change(vid)
            self.lbl.configure(foreground=colors["highlights"][preferences["choices"][1]])
        else:
            pass
      

class ProgressBar(tk.Frame):
    def __init__(self, parent):
       tk.Frame.__init__(self, parent)
       self.parent = parent
       self.pbar = None
       self.style = Style()

    def create_pbar(self, len, thick, posx, posy):
        # Creating custom Progressbar layout to have label with percentage inside bar
        self.style.layout("LabeledProgressbar",[('LabeledProgressbar.trough', {'children': [('LabeledProgressbar.pbar',
                {'side': 'left', 'sticky': 'ns'}), ("LabeledProgressbar.label",   # label inside the bar
                {"sticky": ""})],'sticky': 'nsew'})])
        self.style.configure("LabeledProgressbar", thickness=thick, background=colors["highlights"][ preferences["choices"][1]], text="")
        self.pbar = Progressbar(self.parent, orient='horizontal', length=len, mode='determinate', style="LabeledProgressbar")
        self.pbar.place(relx=posx, rely = posy)

    def update_pbar(self, prog, i):
        self.pbar['value'] += prog
        self.style.configure("LabeledProgressbar", text= str(floor((i+1)*prog)) + "%          ")
        self.parent.update_idletasks() 

    # Destructor
    def __del__(self):
        self.pbar.destroy()


class Slider(tk.Frame):
    def __init__(self, parent, latest_range_btn):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.style = Style()
        self.slider = None
        self.label = None
        self.var = tk.IntVar()
        self.latest_range_btn = latest_range_btn

    def create_slider(self, lngth, ival, fval, ornt, posx, posy):
        self.style.configure('C.TButton', font=(font["font_family"], font["text"]-3))
        self.style.configure('TScale', background=colors["bgcolor"][0])  
        self.slide = Scale(self.parent, length=lngth, from_=ival, to=fval, orient=ornt, variable=self.var,style= "TScale", command= lambda val: self.update_slider_value(val))
        self.var.set(preferences["choices"][2])
        self.slide.place(relx=posx, rely=posy, height=17)
        self.label = Label(self.parent, text=preferences["choices"][2], background=colors["bgcolor"][0], foreground=colors["fgcolor"])
        self.label.place(relx=0.69, rely=posy)

        controls = []
        ctrl_attr={ "txt":['-', '+']}
        for b in range(len(ctrl_attr["txt"])):
            controls.append(Button(self.parent, text=ctrl_attr["txt"][b], width=2, style="C.TButton", command = lambda x=b: self.controls_val(ctrl_attr["txt"][x])))
            controls[-1].place(relx=0.77+b*0.07, rely=posy-0.01, height=24)

    def controls_val(self, action):
        if (action == '-' and preferences["choices"][2] > 1):
            a = -1
        elif (action == '+' and preferences["choices"][2] < MAX_LATEST_NUMBERS_RANGE): 
            a = 1
        else:
            a = 0
        new_val = preferences["choices"][2] + a
        self.var.set(new_val)
        self.update_slider_value(new_val)
        
    def update_slider_value(self, val):
        # To pass a string representation of a float to an int, convert to float first and then to int
        preferences["choices"][2] = int(float(val))
        conf = Configuration()
        conf.write_configs(2, preferences["choices"][2])
        self.label.configure(text=preferences["choices"][2])
        self.latest_range_btn.configure(text="Get Last "+ str(preferences["choices"][2]) +" As Hex Text")


class NewWindow(tk.Toplevel):
    def __init__(self, btn, dim, title, bg, lbl):
        tk.Toplevel.__init__(self, None)
        self.geometry(dim)
        self.title(title)
        try:
            self.iconphoto(False, tk.PhotoImage(file='assets/images/icon.png'))
        except:
            pass
        self.resizable(False, False)
        self.configure(background=colors["bgcolor"][0])
        btn['state'] = 'disabled'
        self.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(btn))
        self.bg = bg
        self.lbl = lbl

    def on_closing(self, btn):
        btn['state'] = 'normal'
        self.destroy()
        
    def display_about(self):
        txt=["Powered by ", "Cloudfare's LavaRand,", "and the other members of", "The League Of Entropy", "via", "Drand"]
        links = ['https://blog.cloudflare.com/lavarand-in-production-the-nitty-gritty-technical-details/', 'https://www.cloudflare.com/leagueofentropy/', 'https://drand.love/']
        crdts = []
        j=0
        for i in range(6):
            if (i % 2 != 0):
                crdts.append(tk.Label(self, text=txt[i], background= colors["bgcolor"][0], foreground=colors["highlights"][j], font=(font["font_family"], font["text"]), cursor="hand2"))
                crdts[i].bind("<Button-1>", lambda e, x=j: webbrowser.open_new(links[x]))
                crdts[i].bind("<Enter>", lambda e: e.widget.config(foreground= colors["highlights"][3]))
                crdts[i].bind("<Leave>", lambda e, x=j: e.widget.config(foreground=colors["highlights"][x]))
                j+=1
            else:
                crdts.append(tk.Label(self, text=txt[i], background= colors["bgcolor"][0], foreground=colors["fgcolor"], font=(font["font_family"], font["text"])))

            crdts[-1].pack(side="top", pady=2)
           
        try:
            img = Image.open("assets/images/LeagueOfEntropy.png")
            img = img.resize((200, 200), Image.ANTIALIAS)
            self.LoE_img = ImageTk.PhotoImage(img)

            LoE = tk.Label(self,image = self.LoE_img ,background = colors["bgcolor"][0], width=200)
            LoE.pack(side="top")
        except:
             error_msg("Image", img, "assets/images/", None)

    def display_pref(self, latest_range_btn):
        titles=["  Latest Number Output Number System  ", "  Lava Lamp Color  "]
        options = [preferences["num_systems"], preferences["lamp_colors"]]
        yplace= [0.447, 0.805]
        start=[1, len(options[0]) + 1]
        
        tk.LabelFrame(self, text="  Latest Numbers To Hex Text Range  ", background=colors["bgcolor"][0], foreground=colors["fgcolor"]).pack(fill="both", expand=1, padx=10, pady=4)
        slider = Slider(self, latest_range_btn)
        slider.create_slider(200, 1, MAX_LATEST_NUMBERS_RANGE, "horizontal", 0.1, 0.131)

        for title in titles:
            i=titles.index(title)
            tk.LabelFrame(self, text=title, background=colors["bgcolor"][0], foreground=colors["fgcolor"]).pack(fill="both", expand=1, padx=10, pady=12)
            radio_bar = RadioBar(self, start[i], self.bg, self.lbl)
            radio_bar.create_bar(options[i],  preferences["choices"][i])
            radio_bar.place(relx=0.095, rely=yplace[i])

        note = tk.Label(self, text="*Default value is the system in which drand provides random numbers", 
                        background=colors["bgcolor"][0], foreground=colors["fgcolor"], font=(font["font_family"], font["note"]))
        note.place(relx=0.03, rely=0.605)


class Converter():
    def __init__(self):
        self.sys = preferences["choices"][0]

    def to_bin(self, input, base):
        b = bin(int(input, base))
        return b[2:]

    def to_dec(self, input, base):
        dec = int(input, base)
        return dec

    def to_hex(self, input, base):
        hx = hex(int(input, base))
        return hx[2:]

    def convert(self, input):
        out = input
        if (self.sys == 1):
            out = self.to_bin(input, DRAND_NUM_SYSTEM)
        elif (self.sys == 2):
            out = self.to_dec(input, DRAND_NUM_SYSTEM)
        elif (self.sys == 3):
            out = self.to_hex(input, DRAND_NUM_SYSTEM)

        return out


class RandomNumbers():
    def __init__(self):
        self.url = 'https://drand.cloudflare.com/public/'
        self.headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20130401 Firefox/31.0'}
        self.error = "Connection Failed"
        self.num_dict = {}
        self.txt = ""

    def get_num(self, r):
        try:
            req = requests.get(self.url + str(r), self.headers)
            # Get json data as a dictionary
            data = req.json()
            # Return value using key  
            return data['randomness']
        except:
            return self.error
    
    def num_to_dict(self, r):
        self.num_dict[str(r)] = self.get_num(r)

    def get_latest_round(self):
        req = requests.get(self.url + "latest", self.headers)
        data = req.json()
        return data['round']

    def get_latest_20(self, frame):
        try:
            prog = 100/preferences["choices"][2]
            last_round = self.get_latest_round()

            pbar = ProgressBar(frame)
            pbar.create_pbar(160, 19, 0.05, 0.637)

            threads=[]
            for i in range(preferences["choices"][2]):
                # Multithreading is better than multiprocessing for I/O and network tasks
                # Passing numbers firstly to dict, to merge them later in order as hex text
                t = threading.Thread(target = self.num_to_dict, args=[last_round-i])
                t.start()
                threads.append(t)
                pbar.update_pbar(prog, i)

            for t in threads:
                t.join()

            self.txt = ""
            # Merging numbers to text in order, based on their round index
            for i in range(last_round-preferences["choices"][2], last_round):
                self.txt += str(self.num_dict[str(i+1)])

            pbar.destroy()           
            self.num_dict.clear()
            conv = Converter()
            return conv.to_hex(self.txt, DRAND_NUM_SYSTEM) 
        except:
            try:
                pbar.destroy()
            except:
                pass
            return self.error

    def shannon_entropy(self, txt):
        size = len(txt)
        symbols = collections.Counter([ch for ch in txt])
        entropy = 0
        for smbl in symbols:
            # Number of occurances of a symbol
            n_i = symbols[smbl]
            # Calculate propability for a symbol
            p_i = n_i / float(size)
            entropy_i = p_i * log(p_i, 2)
            entropy -= entropy_i
        return round(entropy, 4)

    def update_content(self, id, input_field, output_field, frame):
        if (id == 1):
            conv = Converter()
            val = self.get_num("latest")
            try:
                val = conv.convert(val)
            except:
                pass
        elif (id == 2):
            val = self.get_latest_20(frame)
        elif (id == 3):
            input_field.configure(state='normal')
            txt = input_field.get("1.0", tk.END)[:-1]
            input_field.configure(state='disabled')
            if (txt == self.error or txt == ""):
                val = '-'
            else:
                val = self.shannon_entropy(txt)
        else:
            pass
        
        if id == 3:
            output_field.configure(text= "Entropy: " + str(val), foreground=colors["highlights"][preferences["choices"][1]])
        else:
            output_field.configure(state='normal')
            output_field.delete('1.0', tk.END)
            output_field.insert(tk.INSERT, val)
            output_field.configure(state='disabled')


def copy_button(field):
    clip = tk.Tk()
    clip.withdraw()
    clip.clipboard_clear()
    field.configure(state='normal')
    content = field.get("1.0", tk.END)[:-1]
    clip.clipboard_append(content)
    field.configure(state='disabled')
    clip.destroy()


def gui():
    root = tk.Tk()
    root.title("Random Number Generator (Project 11)")
    root.geometry("550x480")
    try:
        root.iconphoto(False, tk.PhotoImage(file='assets/images/icon.png'))
    except:
        pass
    root.resizable(False, False)
    root.configure(background=colors["bgcolor"][0])

    create_main_dirs()
    conf = Configuration()
    conf.load_configs()
    vid_name = preferences["lamp_colors"][preferences["choices"][1]] + ".mp4"
    bg_vid = VideoPlayer(vid_name)
    # Delete unnecessary object
    del conf

    bg_label = Label(root, background=colors["bgcolor"][1])
    bg_label.place(relx=0, rely=0, width=550)
    bg_label.after(bg_vid.delay, lambda: bg_vid.stream(bg_label))

    rand = RandomNumbers()

    frame = tk.Frame(root, background= colors["bgcolor"][0], width=282, height=442)
    frame.place(relx=0.05, rely=0.04)

    title = tk.Label(frame, background=colors["bgcolor"][0], foreground=colors["fgcolor"],text="Random Number Generator", font=(font["font_family"], font["title"]))
    title.place(relx=0.055, rely=0.018)
   
    number_field = tk.Text(frame, width=31, height=3, background=colors["bgcolor"][2])
    number_field.place(relx=0.05, rely = 0.12)
    # Disable user input 
    number_field.configure(state='disabled')
    # Allow text highlighting by binding the <1> with a function that sets the focus on the text widget
    number_field.bind("<1>", lambda e: number_field.focus_set())

    get_num_btn = Button(frame, text="Get Latest Random Number", command= lambda: rand.update_content(1, None, number_field, None))
    get_num_btn.place(relx=0.05, rely = 0.26)
 
    copy_btn1 = Button(frame, text="Copy Number", command= lambda: copy_button(number_field))
    copy_btn1.place(relx=0.643, rely=0.26)

    txt_field = tk.Text(frame, width=31, height=6, background=colors["bgcolor"][2])
    txt_field.place(relx=0.05, rely = 0.385)
    txt_field.configure(state='disabled')
    txt_field.bind("<1>", lambda e: txt_field.focus_set())

    get_latest_range = Button(frame, text="Get Last "+ str(preferences["choices"][2]) +" As Hex Text", width= 25, command= lambda: rand.update_content(2, None, txt_field, frame))
    get_latest_range.place(relx=0.05, rely = 0.636)

    copy_btn2 = Button(frame, text="Copy Text", width=12, command= lambda: copy_button(txt_field))
    copy_btn2.place(relx=0.653, rely=0.636)

    calc_entropy_btn = Button(frame, text="Calculate Above Text's Entropy", width=40, command= lambda: rand.update_content(3, txt_field, entropy, None))
    calc_entropy_btn.place(relx=0.053, rely = 0.715)

    entropy = tk.Label(frame, background=colors["bgcolor"][0], foreground=colors["fgcolor"], text="", font=(font["font_family"], font["title"]))
    entropy.place(relx=0.05, rely=0.81, relwidth= 0.9)

    pref_btn = Button(frame, text ="Preferences", width=15, command=lambda: NewWindow(pref_btn, '350x280', 'Preferences', bg_vid, entropy).display_pref(get_latest_range))
    pref_btn.place(relx = 0.17, rely=0.92)

    about_btn = Button(frame, text ="About", command=lambda: NewWindow(about_btn, '300x375', 'About', None, None).display_about())
    about_btn.place(relx = 0.56, rely=0.92)
    
    root.mainloop()


if __name__ == "__main__":
    gui()

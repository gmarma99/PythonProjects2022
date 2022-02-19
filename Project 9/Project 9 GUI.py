#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import os
import re 
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter.ttk import *

try:
    from PIL import ImageTk, Image 
    import imageio
except ImportError: 
    print("\n\"PIL\" or \"ImageTk\" or \"imageio\" is missing from your system. \nPlease make sure they are installed and try again.\n")
    exit() 


preferences={
    # Export with space delimiter for optimum usability. 
    # Default value if importing configuration fails is: 1
    "delimiter": 1
}

colors= {
    "bgcolor": ["#222222", "#C0C0C0"],
    "fgcolor": "#FFFFFF"
}

font = {
    "font_family": "Arial", "title": 13, "text": 11, "margin": 7*" "
}


def create_main_dirs():
    names = ["samples", "exported", "configs", "assets", "utilities"]
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

    def read_configs(self):
        try:
            with open(self.configs_path, 'r') as file:
               l = file.readline()
            if l == '':
                return None
            else:
                return int(l)
        except:
            pass

    def write_configs(self, output):
        try:
            with open(self.configs_path, 'w') as file:
                file.writelines(str(output))
        except:
            pass

    def load_configs(self):
        configs = self.read_configs()
        if(configs == None):
            self.error()
        else:
            preferences["delimiter"] = configs


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


class File():
    def __init__(self):
        self.path = None
        self.exp_path = str(Path().absolute()) + "\\exported\\"
        self.filename =""
        self.lines = []
        self.content = ""
        self.binary_txt = ""
        self.loaded = False
        self.ttl = "Select An ASCII Text File"

    def get_filename(self, path):
        parts = path.split("/")
        self.filename = parts[-1]

    def read_file(self, path):
        try:
            with open(path,'r') as file:
                self.lines = file.readlines()
                for l in self.lines:
                    self.content +=l
            self.loaded = True
        except:
            msg = "Error! Text file must only contain ASCII characters.\n\nYou may use \"Simple Text To ASCII Converter.py\" in \"utilities\" subfolder and retry."
            messagebox.showerror("Not ASCII", msg)

    def export(self):
        create_main_dirs()
        new_file = self.filename[:-4] + " [Binary].txt"
        try: 
            with open(self.exp_path + new_file, 'w') as file:
                file.write(self.binary_txt)
            messagebox.showinfo(title="Success", message="Successfully converted and exported file as\n\"" + new_file + "\" at: \n\n" + self.exp_path)
        except:
            messagebox.showerror(title="Fail", message="Operation Failed!")

    def browse_files(self, lbl, txtfield, btn, rlist):
        self.content=self.binary_txt=""
        self.loaded = False
        btn["state"] = "disabled"
        lbl.configure(text=self.ttl)
        self.path = filedialog.askopenfilename(initialdir = os.getcwd(),title = self.ttl, filetypes =[('Text Files', '*.txt')])
        if (self.path) != "":
            self.get_filename(self.path)
            self.read_file(self.path)
            self.update_content(txtfield, self.content)
            self.results(rlist, "empty")
            if self.loaded:
                lbl.configure(text=self.filename)
                btn["state"] = "normal"

    def convert_to_bin(self, btn):
        btn["state"] = "disabled"
        self.binary_txt = ' '.join(format(ord(ch), '07b') for ch in self.content)
        if preferences["delimiter"] == 0:
            # Remove all spaces from self.binary_txt string
            self.binary_txt = re.sub(" +", "", self.binary_txt)
        self.export()
        self.binary_txt = re.sub(" +", "", self.binary_txt)

    def max_consecutive(self, d):
        count = 0
        max = 0
        for digit in self.binary_txt:
            if (digit == d):
                count+=1
                # If count is greater than max replace max with count
                max = count > max and count or max
            else:
                count=0
        return max

    def update_content(self, textfield, content):
        textfield.configure(state='normal')
        textfield.delete("1.0", tk.END)
        textfield.insert("1.0", content)
        textfield.configure(state='disabled')

    def results(self, rlist, action):
        for lbl in rlist:
            i = rlist.index(lbl)
            if (action == "show"):
                txt = str(self.max_consecutive(str(i)))
            elif (action == "empty"):
                txt = " "
            lbl.configure(text=txt)


class CheckButton(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.var = tk.IntVar()
        self.chk_btn = None

    def create_chk_btn(self, txt, fnt, r, c, colsp, rowsp, pdx, pdy):
        style = Style()
        style.configure("TCheckbutton", background=colors["bgcolor"][0], foreground=colors["fgcolor"], font=fnt, variable= self.var)
        self.chk_btn = Checkbutton(self.parent, text = txt, style="TCheckbutton", command= lambda: self.selected())
        self.chk_btn.grid(row=r, column=c, columnspan=colsp, rowspan=rowsp, padx=pdx, pady=pdy)
        # To toggle checkbutton in code, first clear the "alternate" flag
        self.chk_btn.state(['!alternate'])

        if preferences["delimiter"] == 1:
            self.chk_btn.state(['selected'])
        else:
            self.chk_btn.state(['!selected'])

    def selected(self):
        if self.chk_btn.instate(['selected']):
            selection = 1
        else: 
            selection = 0

        conf = Configuration()
        preferences["delimiter"] = selection
        conf.write_configs(selection)


def copy_button(field):
    clip = tk.Tk()
    clip.withdraw()
    clip.clipboard_clear()
    field.configure(state='normal')
    content = field.get("1.0", tk.END)
    clip.clipboard_append(content[:-1])
    field.configure(state='disabled')
    clip.destroy()


def gui():
    root = tk.Tk()
    root.title("Max Consecutive Binary Digits (Project 9)")
    root.geometry("650x480")
    try:
        root.iconphoto(True, tk.PhotoImage(file='assets/images/icon.png'))
    except:
        pass
    root.resizable(False, False)
    root.configure(background=colors["bgcolor"][0])

    create_main_dirs()
    conf = Configuration()
    conf.load_configs()
    del conf

    vid_name = "BinaryMatrix.mp4"
    bg_vid = VideoPlayer(vid_name)
    file = File()

    bg_label = Label(root, background=colors["bgcolor"][0])
    bg_label.pack()
    bg_label.after(bg_vid.delay, lambda: bg_vid.stream(bg_label))

    frame = tk.Frame(root, background= colors["bgcolor"][0])
    frame.place(anchor="c", relx=.5, rely=.5)

    title = tk.Label(frame, background=colors["bgcolor"][0], foreground=colors["fgcolor"],text=file.ttl, font=(font["font_family"], font["title"]), width=53)
    title.grid(row=1, column=1, columnspan=3, pady=5)

    txt_field = tk.Text(frame, width=54, height=10, background=colors["bgcolor"][1])
    txt_field.grid(row=3, column=1, columnspan=3, pady=5)
    txt_field.configure(state='disabled')
    txt_field.bind("<1>", lambda e: txt_field.focus_set())

    explore_btn = Button(frame, text = "Browse Files", command = lambda: file.browse_files(title, txt_field, convert_btn, results))
    explore_btn.grid(row=2, column=1, columnspan=3, ipadx=20, pady=5)

    convert_btn = Button(frame, text = "Convert ASCII Text To Binary And Export To File", command = lambda: file.convert_to_bin(convert_btn))
    convert_btn["state"] = "disabled"
    convert_btn.grid(row=4, column=1, columnspan=2, ipadx=21, pady=5, padx=27, sticky='e')

    copy_btn = Button(frame, text = "Copy Text", command = lambda: copy_button(txt_field))
    copy_btn.grid(row=4, column=3, ipadx=13, pady=5, sticky='w')

    chk_btn = CheckButton(frame)
    chk_btn.create_chk_btn("Export with space delimiter between binary numbers", (font["font_family"], font["text"]), 5, 1, 3, 1, 30, 10)

    fieldset = tk.LabelFrame(frame, text="  Consecutive Binary Digits (No Spaces)  ", labelanchor='n', background=colors["bgcolor"][0], foreground=colors["fgcolor"], font=(font["font_family"], font["title"]))  
    fieldset.grid(row=6, column=1, columnspan=3, pady=10, padx= 50, sticky='ew')

    results=[]

    for i in [0, 1]:
        tk.Label(fieldset, background=colors["bgcolor"][0], foreground=colors["fgcolor"],text= font["margin"] + "  Max Consecutive "+ str(i) +"'s:" + font["margin"], font=(font["font_family"], font["text"])).grid(row=1+i, column=1, pady=10)
        results.append(tk.Label(fieldset, background=colors["bgcolor"][0], foreground=colors["fgcolor"],text=" ", font=(font["font_family"], font["text"])))
        results[i].grid(row=1+i, column=2, pady=10)

    try:
        img_path = "assets/images/"
        img = "search.png"
        img_w = 40
        raw = Image.open(img_path + img)
        resized = raw.resize((img_w, img_w), Image.ANTIALIAS)
        search_icon = ImageTk.PhotoImage(resized)
    except:
        error_msg("Image", img, img_path, "exit")

    search_btn = Button(fieldset, image=search_icon, command= lambda: file.results(results, "show"))
    search_btn.grid(row=1, column=3, rowspan=2, ipadx=10, padx=40)

    root.mainloop()


if __name__ == "__main__":
    gui()

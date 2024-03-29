#!/usr/bin/env python3

# python2
try:
    from Tkinter import *
    import ttk
    import tkMessageBox


# python3
except ImportError:
    from tkinter import *
    from tkinter import ttk
    from tkinter import messagebox as tkMessageBox


from PIL import ImageTk, Image
from datetime import datetime
from models import manager
import handicap


class MainWindow(Tk):
    def __init__(self, wid, hei):
        Tk.__init__(self)

        self.title("Handicap Calculator")
        self.geometry("{}x{}".format(wid, hei))
        self.resizable(False, False)

        # main frame that each frame loads into
        self.container = Frame(self, width=wid, height=hei)
        self.container.pack(fill=BOTH, expand=True)

        # contains each frame
        # key is name of frame
        # value is the frame object
        self.frames = dict()
        self.frame = None

        for FrameClass in (Login, CreateAccount, MainScreen, CourseSearch, EnterScore):
            frame = FrameClass(self.container, self)
            frame.grid(row=0, column=0, sticky="nsew")
            self.frames[FrameClass] = frame
        
        self.course = None
        manager.login('jrundle', 'asdfghjkl1')
        self.set_frame(MainScreen)
        self.mainloop()

    def set_frame(self, title):
        """Receives Frame title, gets frame object, then raises it to screen """
        if hasattr(self.frame, 'forget_widgets'):
            self.frame.forget_widgets()

        self.frame = self.frames[title]
        self.frame.tkraise()
        
        if hasattr(self.frame, 'load_widgets'):
            self.frame.load_widgets()

    @staticmethod
    def disp_msg(msg):
        tkMessageBox.showinfo("Handicap Calculator", msg)


# noinspection PyAttributeOutsideInit
class Login(Frame):
    def __init__(self, parent_frame, window):
        Frame.__init__(self, parent_frame, width=800, height=500)
        self.window = window

    def load_widgets(self):

        image = ImageTk.PhotoImage(Image.open("img/golf.jpg"))
        pic_label = Label(self, image=image)
        pic_label.image = image
        pic_label.place(x=0, y=0, relwidth=1, relheight=1)

        label = Label(self, text="Handicap Calculator", font=('Calibri', 28),
                      bg="white", relief=RIDGE, borderwidth=2)
        label.place(anchor=CENTER, relx=0.5, rely=0.2)

        entry_frame = Frame(self, highlightbackground="grey", highlightthickness=2)

        label2 = Label(entry_frame, text="Username:", font=("Calibri", 15))
        label2.pack(side=TOP, anchor=W, ipady=2)

        self.username_entry = Entry(entry_frame, font=("Calibri", 15))
        self.username_entry.pack(side=TOP, fill=X, ipady=2, padx=10)
        self.username_entry.focus()

        label3 = Label(entry_frame, text="Password:", font=("Calibri", 15))
        label3.pack(side=TOP, anchor=W, ipady=2)

        self.password_entry = Entry(entry_frame, font=("Calibri", 15), show="*")
        self.password_entry.pack(side=TOP, fill=X, ipady=2, padx=10)
        self.password_entry.bind("<Return>", lambda *args: self.login())

        button = Button(entry_frame, text="Login",
                        font=("Calibri", 15),
                        command=self.login)
        button.pack(side=TOP, fill=X, pady=10, padx=10)

        button2 = Button(self, text="Create Account", font=("Calibri", 10, 'underline'),
                         command=lambda: self.window.set_frame(CreateAccount),
                         relief=GROOVE, borderwidth=1)
        button2.place(anchor=CENTER, relx=0.5, rely=0.75)

        entry_frame.place(anchor=CENTER, relx=0.5, rely=0.5)

    def login(self):
        username, password = self.get_info()

        if not username:
            self.window.disp_msg("Username entry is blank")
            return
        if not password:
            self.window.disp_msg("Password entry is blank")
            return

        try:
            manager.login(username, password)
            self.username_entry.delete(0, END)
            self.password_entry.delete(0, END)
            self.window.set_frame(MainScreen)
        except ValueError as e:
            self.password_entry.delete(0, END)
            self.window.disp_msg(e)

    def get_info(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        return username, password


class CreateAccount(Frame):
    def __init__(self, parent_frame, window):
        Frame.__init__(self, parent_frame)
        self.window = window

    def load_widgets(self):
        image = ImageTk.PhotoImage(Image.open("img/golf.jpg"))
        pic_label = Label(self, image=image)
        pic_label.image = image
        pic_label.place(x=0, y=0, relwidth=1, relheight=1)

        label = Label(self, text="Handicap Calculator", font=('Calibri', 28), bg="white", relief=RIDGE, borderwidth=2)
        label.place(anchor=CENTER, relx=0.5, rely=0.15)

        entry_frame = Frame(self, highlightbackground="grey", highlightthickness=2)
        f = ("Calibri", 14)

        first_name_label = Label(entry_frame, text="First Name:", font=f)
        first_name_label.grid(column=0, row=0)
        self.first_name_entry = Entry(entry_frame, font=f)
        self.first_name_entry.grid(row=0, column=1, padx=(0, 10), pady=(10, 5))

        last_name_label = Label(entry_frame, text="Last Name:", font=f)
        last_name_label.grid(row=1, column=0)
        self.last_name_entry = Entry(entry_frame, font=f)
        self.last_name_entry.grid(row=1, column=1, padx=(0, 10), pady=5)

        username_label = Label(entry_frame, text="Username:", font=f)
        username_label.grid(row=2, column=0)
        self.username_entry = Entry(entry_frame, font=f)
        self.username_entry.grid(row=2, column=1, padx=(0, 10), pady=5)

        password_label = Label(entry_frame, text="Password:", font=f)
        password_label.grid(row=3, column=0)
        self.password_entry = Entry(entry_frame, font=f, show="*")
        self.password_entry.grid(row=3, column=1, padx=(0, 10), pady=5)

        confirm_label = Label(entry_frame, text="Confirm Password:", font=f)
        confirm_label.grid(row=4, column=0)
        self.confirm_entry = Entry(entry_frame, font=f, show="*")
        self.confirm_entry.grid(row=4, column=1, padx=(0, 10), pady=(5, 10))

        self.gender = StringVar()
        self.gender.set("M")  # initialize
        male_button = Radiobutton(entry_frame, text="Male", variable=self.gender, value="M", font=f)
        male_button.grid(row=5, column=0)
        female_button = Radiobutton(entry_frame, text="Female", variable=self.gender, value="F", font=f)
        female_button.grid(row=5, column=1)

        button = Button(self, text="Create Account",
                        command=self.create_account,
                        width=20)
        button.place(anchor=CENTER, relx=0.5, rely=0.8)

        button2 = Button(self, text="Go Back",
                         command=lambda: self.window.set_frame(Login),
                         width=10)
        button2.place(anchor=CENTER, relx=0.5, rely=0.9)

        entry_frame.place(anchor=CENTER, relx=0.5, rely=0.5)

    def create_account(self):
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        gender = self.gender.get()[0]

        if not all([first_name, last_name, username, password, gender]):
            self.window.disp_msg("Please fill in each entry")
            return

        try:
            manager.create_user(username, password, first_name, last_name, gender)
            self.window.set_frame(Login)
        except ValueError as e:
            self.window.disp_msg(e)


class MainScreen(Frame):
    def __init__(self, parent_frame, window):
        Frame.__init__(self, parent_frame)
        self.window = window

    def load_widgets(self):
        acc = manager.get_account()

        self.topleft = Frame(self, bg='#8cd9b3', highlightbackground="grey", highlightthickness=2)
        label = Label(self.topleft,
                      text='{} {}\n{}'.format(acc.first_name, acc.last_name, acc.handicap),
                      font=("Calibri", 30), padx=10, relief=GROOVE)
        label.place(anchor=CENTER, relx=0.5, rely=0.25)
        button = Button(self.topleft, text='Edit Account',
                        font=("Calibri", 20))
        button.place(anchor=CENTER, relx=0.5, rely=0.6)
        button2 = Button(self.topleft, text='Log Out',
                         font=("Calibri", 20),
                         command=self.log_out)
        button2.place(anchor=CENTER, relx=0.5, rely=0.8)

        self.bottomleft = Frame(self, bg='#8cd9b3', highlightbackground="grey", highlightthickness=2)
        button = Button(self.bottomleft, text="Post Score",
                        font=("Calibri", 26),
                        command=lambda: self.window.set_frame(CourseSearch),
                        width=12)
        button.place(anchor=CENTER, relx=0.5, rely=0.5)

        self.right = Frame(self, highlightbackground="grey", highlightthickness=2)
        label = Label(self.right, bg='#d9f2e6', text="Recent Scores", font=("Calibri", 20), relief=GROOVE)
        label.pack(side=TOP, fill=X)

        canvas = Canvas(self.right, bg='#d9f2e6')
        self.canvas_frame = Frame(canvas)
        scrollbar = Scrollbar(self.right, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)
        canvas.create_window(230, 0, window=self.canvas_frame, anchor=CENTER)
        self.canvas_frame.bind("<Configure>", lambda x: canvas.configure(scrollregion=canvas.bbox("all")))

        for i in range(6):
            self.canvas_frame.grid_columnconfigure(index=i, weight=1)

        colors = ['#C2CAFD', '#8E9AE1']
        self.rounds = manager.get_rounds()
        for i, round in enumerate(self.rounds):
            color = colors[i % 2]
            info = [round.course.name,
                    round.date.strftime("%b %-d, %Y"),
                    str(round.tee.cr) + "/" + str(round.tee.sr),
                    str(round.score) + round.type,
                    round.differential]

            for j, item in enumerate(info):
                l = Label(self.canvas_frame, text=str(item), bg=color, font=("Calibri", 18), padx=7, wraplength=140)
                l.grid(row=i, column=j, sticky='nsew')
                # when a label is right-clicked, create an entry at that spot on grid
                # and set it with the same value as the label
                l.bind("<Button-2>",lambda e, row=i, col=j, value=item: self.create_entry(row, col, value=value))
                # when a label is left-clicked, get permission from user, then delete round
                l.bind('<Button-1>', lambda e, id=round.id: self.delete_round(id))

        self.topleft.place(anchor='nw', x=0, y=0, relwidth=0.4, relheight=0.7)
        self.bottomleft.place(anchor='nw', x=0, rely=0.7, relwidth=0.4, relheight=0.3)
        self.right.place(anchor='nw', relx=0.4, y=0, relwidth=0.6, relheight=1)

        canvas.yview_moveto(0)

    def create_entry(self, row, col, value=""):
        if col not in [1, 3]: return
        # if changing score, remove round type tag
        if col == 3 and len(value) > 2:
            value = value[:-1]

        text_var = StringVar()
        text_var.set(value)
        entry = Entry(self.canvas_frame, textvariable=text_var, font=("Calibri", 18), justify=CENTER)
        entry.focus()
        entry.grid(row=row, column=col, sticky='nsew')
        entry.bind('<Return>', lambda *args: self.change_text(text_var, row, col))
        entry.bind("<Button-2>", lambda e: entry.grid_forget())

    def change_text(self, text_var, row, col):
        round_id = self.rounds[row][0]
        
      # changing date column
        if col == 1:
            date = text_var.get()
            manager.update_round_info(round_id, date=date)

        # changing score column
        if col == 3:
            try:
                score = int(text_var.get())
            except ValueError:
                self.window.disp_msg("Score must be an integer")
                return
            manager.update_round_info(round_id, score=score)

        self.forget_widgets()
        self.load_widgets()

    def delete_round(self, id):
        round = manager.get_round(id)
        ans = tkMessageBox.askyesno("Handicap Calculator",
                                    "Would you like to delete this round?\n\n{}: {} ({})"
                                    .format(round.course_name, round.score, round.date))
        if ans:
            manager.delete_round(id)
            self.forget_widgets()
            self.load_widgets()
        else:
            pass

    def log_out(self):
        manager.log_out()

        self.forget_widgets()
        self.window.set_frame(Login)

    def forget_widgets(self):
        self.topleft.place_forget()
        self.bottomleft.place_forget()
        self.right.place_forget()


class CourseSearch(Frame):
    def __init__(self, parent_frame, window):
        Frame.__init__(self, parent_frame, bg='#d9f2e6')
        self.window = window

    def load_widgets(self):
        self.label = Label(self, text="Search Courses", bg='#8cd9b3', font=('Calibri', 20))
        self.label.pack(fill=X)

        course_search = StringVar()
        course_search.trace('w', lambda a, b, c: self.update_listbox(course_search.get()))
        self.course_entry = Entry(self, font=('Calibri', 24), bd=3, textvariable=course_search)
        self.course_entry.pack(fill=X, pady=10)
        self.course_entry.focus()

        self.subframe = Frame(self, highlightbackground="grey", highlightthickness=2)

        scrollbar = Scrollbar(self.subframe, orient=VERTICAL)
        self.listbox = Listbox(self.subframe, yscrollcommand=scrollbar.set, font=('Calibri', 22))
        self.listbox.bind('<<ListboxSelect>>', lambda a: self.search_course())
        scrollbar.config(command=self.listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
        self.load_suggested()

        self.subframe.pack(fill=BOTH, pady=30)

        self.button = Button(self, text='BACK', font=("Calibri", 25), width=6, bg='#8cd9b3', bd=3, command=lambda *args: (self.forget_widgets(), self.window.set_frame(MainScreen)))
        self.button.pack()
    
    
    def load_suggested(self):
        suggested = manager.get_suggested_courses()
        self.courses = map(lambda id: handicap.get_course_from_id(id), suggested)
        self.listbox.delete(0, END)
        for course in self.courses:
            option = "{} ({}, {})".format(course.name, course.city, course.state)
            self.listbox.insert(END, option)
    
    def update_listbox(self, text):
        if not text or text == " ":
            self.load_suggested()
            return
        self.courses = handicap.get_courses_from_name(text)
        self.listbox.delete(0, END)
        for course in self.courses:
            option = "{} ({}, {})".format(course.name, course.city, course.state)
            self.listbox.insert(END, option)

    def search_course(self):
        try:
            course = self.courses[self.listbox.curselection()[0]]
            self.course_entry.delete(0, END)
        except (IndexError, AttributeError):
            return

        self.window.course = course

        self.forget_widgets()
        self.window.set_frame(EnterScore)

    def forget_widgets(self):
        self.button.pack_forget()
        self.label.pack_forget()
        self.course_entry.pack_forget()
        self.subframe.pack_forget()


class EnterScore(Frame):
    def __init__(self, parent, window):
        Frame.__init__(self, parent)
        self.window = window

    def load_widgets(self):
        self.left_subframe = Frame(self)

        holes_frame = Frame(self.left_subframe)
        f = ("Calibri", 20)
        self.holes_count = StringVar()
        self.holes_count.set("18")  # initialize
        both = Checkbutton(holes_frame, text="18 Holes", variable=self.holes_count,
                           command=lambda *args: self.load_listbox(),
                           onvalue="18", font=f)
        both.grid(row=0, column=0, padx=5)
        front = Checkbutton(holes_frame, text="Front 9", variable=self.holes_count,
                            command=lambda *args: self.load_listbox(),
                            onvalue="9F", font=f)
        front.grid(row=0, column=1, padx=5)
        back = Checkbutton(holes_frame, text="Back 9", variable=self.holes_count,
                           command=lambda *args: self.load_listbox(),
                           onvalue="9B", font=f)
        back.grid(row=0, column=2, padx=5)
        holes_frame.pack(side=TOP)

        scrollbar = Scrollbar(self.left_subframe, orient=VERTICAL)
        self.listbox = Listbox(self.left_subframe, yscrollcommand=scrollbar.set, font=('Calibri', 24))
        scrollbar.config(command=self.listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.listbox.pack(side=LEFT, fill=BOTH, expand=True)

        self.course = self.window.course
        self.tees = handicap.get_course_tees(self.course.id, gender=manager.get_account().gender)
        max_len = 0
        for tee in self.tees:
            option = "{}: {}/{}".format(tee.color, tee.cr, tee.sr)
            self.listbox.insert(END, option)
            if len(option) > max_len:
                max_len = len(option)
        self.listbox.configure(width=max_len)

        self.left_subframe.pack(side=LEFT, fill=BOTH)

        self.right_subframe = Frame(self)

        type_frame = Frame(self.right_subframe)
        f = ("Calibri", 18)
        self.round_type = StringVar()
        self.round_type.set("Home")
        self.window.option_add('*TCombobox*Listbox.font', f)
        mo = ttk.Combobox(type_frame, value="Home Away Tournament", textvariable=self.round_type, font=f, justify=CENTER,
                          state='readonly')
        mo.pack()

        months = " ".join(map(str, range(1, 13)))
        days = " ".join(map(str, range(1, 32)))
        years = " ".join(map(str, range(2000, 2021)))
        today = datetime.today()

        date_frame = Frame(self.right_subframe)

        self.month = StringVar()
        self.month.set(today.month)
        mo = ttk.Combobox(date_frame, value=months, textvariable=self.month, font=f, width=3, justify=CENTER, state='readonly')
        mo.pack(side=LEFT, anchor='nw')

        self.day = StringVar()
        self.day.set(today.day)
        do = ttk.Combobox(date_frame, value=days, textvariable=self.day, font=f, width=3, justify=CENTER, state='readonly')
        do.pack(side=LEFT, anchor='nw')

        self.year = StringVar()
        self.year.set(today.year)
        yo = ttk.Combobox(date_frame, value=years, textvariable=self.year, font=f, width=5, justify=CENTER, state='readonly')
        yo.pack(side=LEFT, anchor='nw')

        score_frame = Frame(self.right_subframe)
        label = Label(score_frame, text="Score", font=("Calibri", 25))
        label.pack(side=TOP)
        self.score = Entry(score_frame, font=("Calibri", 50), bd=2, width=3, justify=CENTER)
        self.score.pack(side=TOP, ipady=3)

        button = Button(self.right_subframe, text="Upload", command=self.set_score, font=("Calibri", 20))

        type_frame.pack(side=TOP, pady=20)
        date_frame.pack(side=TOP, pady=20)
        score_frame.pack(side=TOP, pady=20)
        button.pack(side=TOP, pady=20)

        self.right_subframe.pack(side=LEFT, fill=BOTH, expand=True)

    def load_listbox(self):
        self.listbox.delete(0, END)
        holes = self.holes_count.get()
        max_len = 0
        for tee in self.tees:
            if holes == "18":
                option = "{}: {}/{}".format(tee.color, tee.cr, tee.sr)
            elif holes == "9F":
                option = "{}: {}/{}".format(tee.color, tee.front_cr, tee.front_sr)
            elif holes == "9B":
                option = "{}: {}/{}".format(tee.color, tee.back_cr, tee.back_sr)

            self.listbox.insert(END, option)
            if len(option) > max_len:
                max_len = len(option)

        self.listbox.configure(width=max_len)

    def set_score(self):
        try:
            tee = self.tees[self.listbox.curselection()[0]]
        except IndexError:
            return

        try:
            score = int(self.score.get())
            self.score.delete(0, END)
        except ValueError:
            return

        year = int(self.year.get())
        month = int(self.month.get())
        day = int(self.day.get())
        now = datetime.now()

        date = datetime(year, month, day, now.hour, now.minute, now.second).isoformat()

        round_type = self.round_type.get()[0]
        holes_count = self.holes_count.get()

        manager.upload_round_info(tee, score, date, holes_played=holes_count, round_type=round_type)

        # self.forget_widgets()
        self.window.set_frame(MainScreen)

    def forget_widgets(self):
        self.left_subframe.pack_forget()
        self.right_subframe.pack_forget()


if __name__ == "__main__":
    MainWindow(800, 500)

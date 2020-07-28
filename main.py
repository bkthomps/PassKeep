from tkinter import *

from account import Account

gui = Tk()
frame_welcome = Frame(gui)
frame_login = Frame(gui)
frame_signup = Frame(gui)
frame_dashboard = Frame(gui)


def frames_vanish():
    frame_welcome.pack_forget()
    frame_login.pack_forget()
    frame_signup.pack_forget()
    frame_dashboard.pack_forget()


def init_welcome(frame):
    t1 = Label(frame, text="")
    t2 = Label(frame, text="Welcome to PassKeep", font=("Arial", 28))
    b1 = Button(frame, text="Login", command=lambda: page_login(), width=10, height=2)
    b2 = Button(frame, text="Sign Up", command=lambda: page_signup(), width=10, height=2)
    t1.grid(row=0, column=0, columnspan=2, padx=0, pady=0)
    t2.grid(row=1, column=0, columnspan=2, padx=20, pady=20)
    b1.grid(row=2, column=0, padx=5, pady=5)
    b2.grid(row=2, column=1, padx=5, pady=5)


def init_login(frame):
    t1 = Label(frame, text="", fg='dark red')
    t2 = Label(frame, text="Username")
    t3 = Label(frame, text="Password")
    e1 = Entry(frame)
    e2 = Entry(frame)
    b1 = Button(frame, text="Back", command=lambda: page_welcome(t1, e1, e2), width=10, height=2)
    b2 = Button(frame, text="Login", command=lambda: login(t1, e1, e2), width=10, height=2)
    t1.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
    t2.grid(row=1, column=0, padx=5, pady=5)
    e1.grid(row=1, column=1, padx=5, pady=5)
    t3.grid(row=2, column=0, padx=5, pady=5)
    e2.grid(row=2, column=1, padx=5, pady=5)
    b1.grid(row=3, column=0, padx=10, pady=10)
    b2.grid(row=3, column=1, padx=10, pady=10)


def init_signup(frame):
    t1 = Label(frame, text="", fg='dark red')
    l1 = Label(frame, text="Username")
    l2 = Label(frame, text="Password")
    l3 = Label(frame, text="Confirm Password")
    e1 = Entry(frame)
    e2 = Entry(frame)
    e3 = Entry(frame)
    b1 = Button(frame, text="Back", command=lambda: page_welcome(t1, e1, e2, e3), width=10, height=2)
    b2 = Button(frame, text="Signup", command=lambda: signup(t1, e1, e2, e3), width=10, height=2)
    t1.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
    l1.grid(row=1, column=0, padx=5, pady=5)
    e1.grid(row=1, column=1, padx=5, pady=5)
    l2.grid(row=2, column=0, padx=5, pady=5)
    e2.grid(row=2, column=1, padx=5, pady=5)
    l3.grid(row=3, column=0, padx=5, pady=5)
    e3.grid(row=3, column=1, padx=5, pady=5)
    b1.grid(row=4, column=0, padx=10, pady=10)
    b2.grid(row=4, column=1, padx=10, pady=10)


def init_dashboard(frame):
    Label(frame, text="Dashboard").grid(row=0, column=0, padx=5, pady=5)


def page_welcome(text, *args):
    text["text"] = ""
    frames_vanish()
    for arg in args:
        arg.delete(0, 'end')
    frame_welcome.pack()


def page_login():
    frames_vanish()
    frame_login.pack()


def page_signup():
    frames_vanish()
    frame_signup.pack()


def page_dashboard():
    frames_vanish()
    frame_dashboard.pack()


def login(text, username, password):
    account = Account(username.get())
    try:
        account.login(password.get())
        page_dashboard()
        text["text"] = ""
        username.delete(0, 'end')
        password.delete(0, 'end')
    except Exception as e:
        text["text"] = str(e)


def signup(text, username, password, confirmPassword):
    account = Account(username.get())
    try:
        account.signup(password.get(), confirmPassword.get())
        page_dashboard()
        text["text"] = ""
        username.delete(0, 'end')
        password.delete(0, 'end')
        confirmPassword.delete(0, 'end')
    except Exception as e:
        text["text"] = str(e)


if __name__ == '__main__':
    init_welcome(frame_welcome)
    init_login(frame_login)
    init_signup(frame_signup)
    init_dashboard(frame_dashboard)
    frames_vanish()
    frame_welcome.pack()
    width = 400
    height = 225
    x = (gui.winfo_screenwidth() - width) // 2
    y = (gui.winfo_screenheight() - height) // 2
    gui.geometry("{}x{}+{}+{}".format(width, height, x, y))
    gui.title("PassKeep")
    gui.mainloop()

from tkinter import *

from account import Account

gui = Tk()
frame_logged_out = Frame(gui)
frame_login = Frame(gui)
frame_signup = Frame(gui)
frame_dashboard = Frame(gui)


def frames_vanish():
    frame_logged_out.pack_forget()
    frame_login.pack_forget()
    frame_signup.pack_forget()
    frame_dashboard.pack_forget()


def init_logged_out(frame):
    Button(frame, text="Login", command=lambda: page_login()).grid(row=0, column=0)
    Button(frame, text="Sign Up", command=lambda: page_signup()).grid(row=1, column=0)


def init_login(frame):
    text = Label(frame, text="")
    text.grid(row=0, column=0, columnspan=2)
    Label(frame, text="Username").grid(row=1, column=0)
    Label(frame, text="Password").grid(row=2, column=0)
    e1 = Entry(frame)
    e1.grid(row=1, column=1)
    e2 = Entry(frame)
    e2.grid(row=2, column=1)
    Button(frame, text="Back", command=lambda: page_logged_out(text, e1, e2)).grid(row=3, column=0)
    Button(frame, text="Login", command=lambda: login(text, e1, e2)).grid(row=3, column=1)


def init_signup(frame):
    text = Label(frame, text="")
    text.grid(row=0, column=0, columnspan=2)
    Label(frame, text="Username").grid(row=1, column=0)
    Label(frame, text="Password").grid(row=2, column=0)
    Label(frame, text="Confirm Password").grid(row=3, column=0)
    e1 = Entry(frame)
    e1.grid(row=1, column=1)
    e2 = Entry(frame)
    e2.grid(row=2, column=1)
    e3 = Entry(frame)
    e3.grid(row=3, column=1)
    Button(frame, text="Back", command=lambda: page_logged_out(text, e1, e2, e3)).grid(row=4, column=0)
    Button(frame, text="Signup", command=lambda: signup(text, e1, e2, e3)).grid(row=4, column=1)


def init_dashboard(frame):
    Label(frame, text="Dashboard").grid(row=0, column=0)


def page_logged_out(text, *args):
    text["text"] = ""
    frames_vanish()
    for arg in args:
        arg.delete(0, 'end')
    frame_logged_out.pack()


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
    init_logged_out(frame_logged_out)
    init_login(frame_login)
    init_signup(frame_signup)
    init_dashboard(frame_dashboard)
    frames_vanish()
    frame_logged_out.pack()
    width = 400
    height = 400
    x = (gui.winfo_screenwidth() - width) // 2
    y = (gui.winfo_screenheight() - height) // 2
    gui.geometry("{}x{}+{}+{}".format(width, height, x, y))
    gui.title("PassKeep")
    gui.mainloop()

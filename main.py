from tkinter import *

from account import Account

account = Account("")
gui = Tk()
frame_welcome = Frame(gui)
frame_login = Frame(gui)
frame_signup = Frame(gui)
frame_authenticated = Frame(gui)
frame_view_vaults = Frame(gui)
frame_create_vault = Frame(gui)


def frames_vanish():
    frame_welcome.pack_forget()
    frame_login.pack_forget()
    frame_signup.pack_forget()
    frame_authenticated.pack_forget()
    frame_view_vaults.pack_forget()
    frame_create_vault.pack_forget()


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
    e2 = Entry(frame, show="\u2022")
    b1 = Button(frame, text="Back", command=lambda: page_welcome(), width=10, height=2)
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
    t2 = Label(frame, text="Username")
    t3 = Label(frame, text="Password")
    t4 = Label(frame, text="Confirm Password")
    e1 = Entry(frame)
    e2 = Entry(frame, show="\u2022")
    e3 = Entry(frame, show="\u2022")
    b1 = Button(frame, text="Back", command=lambda: page_welcome(), width=10, height=2)
    b2 = Button(frame, text="Signup", command=lambda: signup(t1, e1, e2, e3), width=10, height=2)
    t1.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
    t2.grid(row=1, column=0, padx=5, pady=5)
    e1.grid(row=1, column=1, padx=5, pady=5)
    t3.grid(row=2, column=0, padx=5, pady=5)
    e2.grid(row=2, column=1, padx=5, pady=5)
    t4.grid(row=3, column=0, padx=5, pady=5)
    e3.grid(row=3, column=1, padx=5, pady=5)
    b1.grid(row=4, column=0, padx=10, pady=10)
    b2.grid(row=4, column=1, padx=10, pady=10)


def init_authenticated(frame, vaults_options):
    t1 = Label(frame, text="Hello")
    b1 = Button(frame, text="Back", command=lambda: page_welcome(), width=10, height=2)
    b2 = Button(frame, text="View Vaults", command=lambda: page_view_vaults(vaults_options), width=10, height=2)
    b3 = Button(frame, text="Create Vault", command=lambda: page_create_vault(), width=10, height=2)
    t1.grid(row=0, column=0, padx=5, pady=5)
    b1.grid(row=1, column=0, padx=5, pady=5)
    b2.grid(row=1, column=1, padx=5, pady=5)
    b3.grid(row=1, column=2, padx=5, pady=5)


def init_view_vaults():
    vaults_options = OptionMenu(frame_view_vaults, StringVar(), "")
    vaults_options.grid(row=0, column=0, padx=5, pady=5)
    return vaults_options


def init_create_vault(frame):
    t1 = Label(frame, text="Account Name")
    t2 = Label(frame, text="Description")
    t3 = Label(frame, text="Password")
    e1 = Entry(frame)
    e2 = Entry(frame)
    e3 = Entry(frame)
    b1 = Button(frame, text="Back", command=lambda: page_authenticated(), width=10, height=2)
    b2 = Button(frame, text="Add", command=lambda: add_vault(e1, e2, e3), width=10, height=2)
    t1.grid(row=0, column=0, padx=5, pady=5)
    e1.grid(row=0, column=1, padx=5, pady=5)
    t2.grid(row=1, column=0, padx=5, pady=5)
    e2.grid(row=1, column=1, padx=5, pady=5)
    t3.grid(row=2, column=0, padx=5, pady=5)
    e3.grid(row=2, column=1, padx=5, pady=5)
    b1.grid(row=3, column=0, padx=10, pady=10)
    b2.grid(row=3, column=1, padx=10, pady=10)


def page_welcome():
    frames_vanish()
    frame_welcome.pack()


def page_login():
    frames_vanish()
    frame_login.pack()


def page_signup():
    frames_vanish()
    frame_signup.pack()


def page_authenticated():
    frames_vanish()
    frame_authenticated.pack()


def view_vaults():
    frames_vanish()
    frame_view_vaults.pack()


def page_create_vault():
    frames_vanish()
    frame_create_vault.pack()


def page_view_vaults(vaults_options):
    frames_vanish()
    menu = vaults_options.children["menu"]
    menu.delete(0, "end")
    vaults = account.get_vaults()
    for value in vaults:
        (vault_id, vault_name) = value
        menu.add_command(label=vault_name, command=lambda v=vault_id: display_vault(v))
    frame_view_vaults.pack()


def login(text, username, password):
    temp = Account(username.get())
    try:
        global account
        temp.login(password.get())
        account = temp
        page_authenticated()
        text["text"] = ""
        username.delete(0, 'end')
        password.delete(0, 'end')
    except Exception as e:
        text["text"] = str(e)


def signup(text, username, password, confirmPassword):
    temp = Account(username.get())
    try:
        global account
        temp.signup(password.get(), confirmPassword.get())
        account = temp
        page_authenticated()
        text["text"] = ""
        username.delete(0, 'end')
        password.delete(0, 'end')
        confirmPassword.delete(0, 'end')
    except Exception as e:
        text["text"] = str(e)


def add_vault(account_name, description, password):
    account.add_vault(account_name.get(), description.get(), password.get())
    account_name.delete(0, 'end')
    description.delete(0, 'end')
    password.delete(0, 'end')


def display_vault(choice):
    # TODO: display this on the GUI
    print(choice)


if __name__ == '__main__':
    init_welcome(frame_welcome)
    init_login(frame_login)
    init_signup(frame_signup)
    user_vaults = init_view_vaults()
    init_authenticated(frame_authenticated, user_vaults)
    init_create_vault(frame_create_vault)
    frames_vanish()
    frame_welcome.pack()
    width = 400
    height = 225
    x = (gui.winfo_screenwidth() - width) // 2
    y = (gui.winfo_screenheight() - height) // 3
    gui.geometry("{}x{}+{}+{}".format(width, height, x, y))
    gui.title("PassKeep")
    gui.mainloop()

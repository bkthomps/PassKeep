import base64
from datetime import datetime
from tkinter import *
import secrets
import unicodedata as ud

# from Crypto.Cipher import AES
import keyring as keyring
from passlib.hash import pbkdf2_sha256
import sqlite3

gui = Tk()
frame_logged_out = Frame(gui)
frame_login = Frame(gui)
frame_signup = Frame(gui)
frame_dashboard = Frame(gui)

db = sqlite3.connect('passkeep.db')


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
    if len(username.get()) == 0 or len(password.get()) == 0:
        text["text"] = "Must fill in fields"
        return
    text["text"] = ""
    username.delete(0, 'end')
    password.delete(0, 'end')


def create_account(username, master_password):
    master_key = ud.normalize('NFKD', master_password)
    # Values used for authentication (logging in)
    auth = pbkdf2_sha256.using(rounds=250_000, salt_size=32).hash(master_key)
    auth_salt = auth.split("$")[3]
    auth_hashed = auth.split("$")[4]
    # Values used for encryption (encrypting the vault keys)
    crypt = pbkdf2_sha256.using(rounds=250_000, salt_size=32).hash(master_key)
    crypt_salt = crypt.split("$")[3]
    crypt_hashed = crypt.split("$")[4]
    # Create a secret key
    secret_key_bytes = secrets.token_bytes(32)
    secret_key = base64.b64encode(secret_key_bytes, b'./').decode('utf-8').replace("=", "")
    # Key used for authentication
    auth_bytes = base64.b64decode(auth_hashed + "===", "./")
    auth_xor = bytearray(32)
    for i in range(32):
        auth_xor[i] = secret_key_bytes[i] ^ auth_bytes[i]
    auth_key = base64.b64encode(auth_xor, b'./').decode('utf-8').replace("=", "")
    # Key used for encryption
    crypt_bytes = base64.b64decode(crypt_hashed + "===", "./")
    crypt_xor = bytearray(32)
    for i in range(32):
        crypt_xor[i] = secret_key_bytes[i] ^ crypt_bytes[i]
    crypt_key = base64.b64encode(crypt_xor, b'./').decode('utf-8').replace("=", "")
    c = db.cursor()
    now = datetime.now()
    insert = (username, auth_key, auth_salt, crypt_salt, now, now)
    c.execute("INSERT INTO account VALUES (?, ?, ?, ?, ?, ?)", insert)
    db.commit()
    c.close()
    keyring.set_password("bkthomps-passkeep", username, secret_key)
    page_dashboard()


def signup(text, username, password, confirmPassword):
    if len(username.get()) == 0:
        text["text"] = "Username must be filled in"
        return
    if password.get() != confirmPassword.get():
        text["text"] = "Password does not match confirmation"
        return
    if len(password.get()) < 8:
        text["text"] = "Password must be at least 8 characters"
        return
    if password.get() == username.get():
        text["text"] = "Password must not equal username"
        return
    c = db.cursor()
    c.execute("SELECT username, COUNT(username) FROM account WHERE username = ?", (username.get(),))
    entries = c.fetchone()
    c.close()
    if entries[1] > 0:
        text["text"] = "Username already exists"
        return
    create_account(username.get(), password.get())
    text["text"] = ""
    username.delete(0, 'end')
    password.delete(0, 'end')
    confirmPassword.delete(0, 'end')


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

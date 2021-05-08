from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.button import ButtonBehavior
from kivy.graphics import Rectangle, Color
from kivy.properties import ObjectProperty

import requests
from requests.auth import HTTPBasicAuth

from database import DB

file_temp = open("myName.txt", "r")
lines_temp = file_temp.readlines()
file_temp.close()
NEM = ""

try:
    NEM = lines_temp[0]
except:
    pass

def update_nem():
    file_temp = open("myName.txt", "r")
    lines_temp = file_temp.readlines()
    file_temp.close()
    global NEM
    NEM = lines_temp[0]
    MainWindow.nem = NEM


class FirstWindow(Screen):
    namee = ObjectProperty(None)

    def submit_name(self):
        with open("myName.txt", "w") as f:
            f.write(self.namee.text)
        update_nem()
        sm.current = "main"

    def reset(self):
        self.namee.text = ""

class MainWindow(Screen):
    mainLabel = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        self.nem = NEM
        print("name of user: " + self.nem)
        self.mainLabel.text = "Wecome " + self.nem + "! Feeling Down? Ask your friends to reach out!"

    def on_pre_enter(self, *args):
        self.nem = NEM
        self.mainLabel.text = "Wecome " + self.nem + "! Feeling Down? Ask your friends to reach out!"

    def contacts_btn(self):
        sm.current = "contacts"

    def change_name(self):
        sm.current = "first"

    def reach_out(self):
        db.load()
        auth_file = open("auth.txt", "r")
        l = auth_file.readlines()
        auth_file.close()
        auth = HTTPBasicAuth(l[0], l[1])
        res = {}
        for contact in db.contacts:
            message = "Hello " + contact + "! Your friend Neil is feeling down and wants to talk to someone. This is a message letting you know so you can reach out :). Have fun and take care of each other!"
            num = "+1" + str(db.contacts[contact])
            r = requests.post("https://api.twilio.com/2010-04-01/Accounts/AC111abf060be70483872f096ef66673df/Messages.json", data={'From': '+15128293644', 'Body': message, 'To': num}, auth=auth)
            res[contact] = r.status_code
            print("sent msg to: " + str(db.contacts[contact]))
            print(r.status_code, r.reason)
            print(r.text[:300] + "...")

        if 201 in res.values():
            msg_1 = "Successfully Reached: \n"
            msg_2 = "\nFailed to reach: \n"
            for r in res:
                if res[r] == 201:
                    msg_1 += r + "\n"
                else:
                    msg_2 += r + "\n"
            msg = msg_1 + msg_2
            pop = Popup(title="We've Reached out to your friends. Sit Tight.", content=Label(text=msg), size_hint=(None,None), size=(800,800))
            pop.open()

class ContactsWindow(Screen):
    layout_content = ObjectProperty(None)
    button_to_remove = ""
    added = []
    buttons = []

    def __init__(self, **kwargs):
        super(ContactsWindow, self).__init__(**kwargs)
        self.layout_content.bind(minimum_height=self.layout_content.setter('height'))

    def on_pre_enter(self, *args):
        if self.button_to_remove:
            self.remove_button(self.button_to_remove)
            self.just_removed = self.button_to_remove

        for contact in db.contacts:
            if contact not in self.added:
                btn = Button(text=contact, size_hint_y=None, height=30, on_press=self.contact_press)
                self.buttons.append(btn)
                self.layout_content.add_widget(btn)
                self.added.append(contact)

    def back_btn(self):
        sm.current = "main"

    def contact_press(self, btn):
        self.manager.transition.direction = "right"
        ContactWindow.current = btn.text
        sm.current = "contact"

    def new_contact_btn(self):
        sm.current = "newContact"

    def remove_button(self, name):
        br = 0
        for b in self.buttons:
            if b.text == name:
                self.layout_content.remove_widget(b)
                br = b
        if br not in self.buttons:
            return
        else:
            self.buttons.remove(br)
            self.added.remove(br.text)

class ContactWindow(Screen):
    current = ""
    n = ObjectProperty(None)
    num = ObjectProperty(None)

    def on_pre_enter(self, *args):
        numb = db.get_contact(self.current)
        self.n.text = self.current
        self.num.text = numb

    def delete_contact(self):
        ContactsWindow.button_to_remove = self.current
        numb = db.get_contact(self.current)
        db.delete_contact(self.current, numb)
        db.load()
        sm.current = "contacts"

    def back_btn(self):
        sm.current = "contacts"

class AddNewContactWindow(Screen):
    namee = ObjectProperty(None)
    pnumber = ObjectProperty(None)

    def back_btn(self):
        sm.current = "contacts"

    def submit_new_contact(self):
        if(self.namee.text != "" and self.pnumber.text != ""):
            res = db.add_contact(self.namee.text, self.pnumber.text)
            if res:
                self.reset()
                sm.current = "contacts"
            else:
                invalid_form()
        else:
            invalid_form()

    def reset(self):
        self.namee.text = ""
        self.pnumber.text = ""

class myApp(App):
    def build(self):
        return sm

def invalid_form():
    pop = Popup(title="Invalid Form", content=Label(text="Please fill in all fields with valid info.\n Names must be unique!"), size_hint=(None,None), size=(800,800))
    pop.open()

kv = Builder.load_file("my.kv")

db = DB("contacts.txt")
sm = ScreenManager()

screens = [FirstWindow(name="first"), MainWindow(name="main"), ContactsWindow(name="contacts"), AddNewContactWindow(name="newContact"), ContactWindow(name="contact")]
for screen in screens:
    sm.add_widget(screen)


if NEM:
    sm.current = "main"
else:
    sm.current = "first"

if __name__ == "__main__":
    myApp().run()

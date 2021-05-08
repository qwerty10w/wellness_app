class DB:
    def __init__(self, filename):
        self.filename = filename
        self.contacts = None
        self.file = None
        self.load()

    def load(self):
        self.file = open(self.filename, "r")
        self.contacts = {}

        for line in self.file:
            name, number = line.strip().split(";")
            self.contacts[name] = number

        self.file.close()

    def get_contact(self, name):
        if name in self.contacts:
            return self.contacts[name]
        else:
            return -1

    def delete_contact(self, name, number):
        contact_string = name + ";" + number
        file = open("contacts.txt", "r")
        lines = file.readlines()
        file.close()

        nf = open("contacts.txt", "w")
        for line in lines:
            if line.strip("\n") != contact_string:
                nf.write(line)
        nf.close()
        self.load()

    def add_contact(self, name, number):
        if name.strip() not in self.contacts:
            self.contacts[name.strip()] = number
            self.save()
            return True
        else:
            print("Email exists already")
            return False

    def save(self):
        with open(self.filename, "w") as f:
            for contact in self.contacts:
                f.write(contact + ";" + self.contacts[contact] + "\n")

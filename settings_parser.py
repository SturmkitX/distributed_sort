import re

class SettingsParser:
    def __init__(self):
        self.settings = dict()

    def loadSettings(self, file_url):
        with open(file_url, "r") as filein:
            read_line = filein.readline()
            pattern = re.compile("([^#=]+)=(.*)")
            while read_line != "":
                # print(read_line)
                found = re.match(pattern, read_line)
                if found is not None:
                    option, value = found.groups()
                    self.settings[option] = value
                read_line = filein.readline()

    def getValue(self, setting):
        return self.settings.get(setting, None)

    def addValue(self, key, value):
        self.settings[key] = value

if __name__ == "__main__":
    sets = SettingsParser()
    sets.loadSettings("settings.cfg")

import re


class config:
    def __init__(self, file):
        print(file)
        self.file = open(file, "r", encoding="utf-8").read()

    def get(self, key):
        try:
            return re.findall('{} = (.*?)\n'.format(key), self.file)[0]
        except IndexError:
            return ''

    def getint(self, key):
        try:
            return int(re.findall('{} = (.*?)\n'.format(key), self.file)[0])
        except IndexError: return ''

    def getboolean(self, key):
        return eval(re.findall('{} = (.*?)\n'.format(key), self.file)[0])

    def set(self, key, value):
        self.file = re.sub(key + ' = (.*?)\n', key + ' = ' + value + '\n', self.file)

    def write(self):
        with open(self.file, 'w', encoding='utf8') as cff:
            cff.write(self.file)

# configfile = 'config.ini'
# c1 = config(configfile)
# # Get value from key
# print(c1.get('user'))
#
# # Set value of key
# c1.set('dcom','1')
# c1.set('dcom','a2')
# c1.set('scriptfile','a3.js')
# c1.write()
#
#
#
# strconfig = """timeout = 9
# dcom = False
# scriptfile = lzd.js
#
#
# """
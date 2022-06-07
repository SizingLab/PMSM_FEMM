class Variable:

    def __init__(self, name, value, units, desc):
        self.name = name
        self.value = value
        self.units = units
        self.desc = desc

    def __str__(self):

        s = ''

        s += 'Name: ' + self.name + '\n'
        s += 'Value: ' + str(self.value) + '\n'
        s += 'Units: ' + self.units + '\n'
        s += 'Description: ' + self.desc + '\n'

        return s
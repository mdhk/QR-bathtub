import copy

# defining constants
MAX = 2
POS = 1
ZERO = 0
NEG = -1

magnitudes = {
    'M': MAX,
    '+': POS,
    '0': ZERO,
    '-': NEG
}

dIN_behaviours = {
    'Steady': [ZERO],
    'Increasing': [POS, ZERO],
    'Decreasing': [NEG, ZERO],
    'PosParabola': [NEG, ZERO, POS],
    'NegParabola': [POS, ZERO, NEG]
}

class Quantity():
    def __init__(self, name, magnitude, derivative):
        self.M = magnitude
        self.d = derivative
        self.name = name

    def str(self):
        return self.name + "(" + str(self.M) + "," + str(self.d) + ")"

    def change_magn(self):
        if self.name == 'Inflow':
            M_values = [ZERO, POS]
        else:
            M_values = [ZERO, POS, MAX]

        M_index = M_values.index(self.M)

        if self.d == POS and ((self.name != 'Inflow' and self.M != MAX) or (self.name == 'Inflow' and self.M != POS)):
            self.M = M_values[M_index + 1]
        elif self.d == NEG and self.M != ZERO:
            self.M = M_values[M_index - 1]

quantities_names = ['Inflow', 'Volume', 'Height', 'Pressure', 'Outflow']

quantities = [inflow, volume, height, pressure, outflow] = \
    list((Quantity(name, ZERO, ZERO) for name in quantities_names))

class State():
    def __init__(self, inflow, volume, height, pressure, outflow):
        self.inflow = inflow
        self.volume = volume
        self.height = height
        self.pressure = pressure
        self.outflow = outflow
        self.quantities = [inflow, volume, height, pressure, outflow]
        self.number = 1

    def str(self):
        descr = "State " + str(self.number) + "\n"
        for q in self.quantities:
            descr += q.str()
            descr += "\n"
        descr += "\n"
        return descr

    def equivalent(self, other):
        if (self.inflow.M == other.inflow.M) and (self.inflow.d == other.inflow.d) and \
           (self.volume.M == other.volume.M) and (self.volume.d == other.volume.d) and \
           (self.height.M == other.height.M) and (self.height.d == other.height.d) and \
           (self.pressure.M == other.pressure.M) and (self.pressure.d == other.pressure.d) and \
           (self.outflow.M == other.outflow.M) and (self.outflow.d == other.outflow.d):
            return True
        else:
            return False

class Reasoner():
    def __init__(self, initial_state, dIN_behaviour):
        self.initial_state = initial_state
        self.dIN_behaviour = dIN_behaviour
        self.dIN_index = 0
        self.states = [initial_state]
        self.transitions = []

    def any_magn_changes(self, state):
        quants_to_change = []
        for q in state.quantities:
            if (q.M != MAX and q.M != q.d) or \
               (q.name != 'Inflow' and (q.M == POS and q.d == POS)) or \
               (q.M == NEG and q.d == NEG):
                quants_to_change.append(q)
        if quants_to_change:
            return quants_to_change
        else:
            return None

    def any_max_magn(self, state):
        for q in state.quantities:
            if q.M == MAX:
                return True
        return False

    def causality(self, old_state):
        if old_state.inflow ==

    def reasoning_step(self, previous_state):
        next_state = copy.deepcopy(previous_state)
        next_state.number += 1
        new_state = None

        if self.any_magn_changes(next_state):
            #print('magn')
            for q in self.any_magn_changes(next_state):
                q.change_magn()
            self.states.append(next_state)
            self.transitions.append((previous_state, next_state))
            new_state = next_state

        else:
            #print('else')
            influence('+', next_state.inflow, next_state.volume)
            influence('-', next_state.outflow, next_state.volume)
            proportional('+', next_state.volume, next_state.height)
            proportional('+', next_state.height, next_state.pressure)
            proportional('+', next_state.pressure, next_state.outflow)
            correspondence('M', next_state.volume, next_state.outflow, next_state.height, next_state.pressure)
            correspondence('0', next_state.volume, next_state.outflow, next_state.height, next_state.pressure)
            self.states.append(next_state)
            self.transitions.append((previous_state, next_state))
            new_state = next_state

        if self.any_max_magn(next_state):
            #print('max')
            next_state.inflow.d = self.dIN_behaviour[self.dIN_index + 1]
            next_state.volume.d = ZERO
            next_state.height.d = ZERO
            next_state.pressure.d = ZERO
            next_state.outflow.d = ZERO
            new_state = next_state

        if new_state.equivalent(previous_state):
            print("Previous and next states are equivalent")
            return None
        else:
            return new_state

    def do_reasoning(self):
        counter = 0
        print(self.initial_state.str())
        next_state = self.reasoning_step(self.initial_state)
        while next_state and counter < 10:
            print(next_state.str())
            next_state = self.reasoning_step(next_state)
            counter += 1

        return self.states



def check_magn_input(str):
    """
    Makes sure magnitude input is provided in the desired way and returns the corresponding constant.
    """
    input_str = input(str).strip('\'')

    while input_str not in ['+', '-', '0', 'M']:
        print('Invalid input. Choose one of \'+\' (positive), \'-\' (negative), \'0\' (zero), \'M\' (maximum).\n')
        check_magn_input(str)

    return magnitudes[input_str]

def get_dIN_list():
    """
    Get assumption input from user, returns corresponding list of dIN behaviour.
    """
    input_str = input('\nPlease provide your assumption for the Inflow rate behaviour. Choose one of\n' +
                      str(sorted(list(dIN_behaviours.keys()))) + '\n' +
                      '(PosParabola behaviour similar to x^2, NegParabola behaviour similar to -x^2.)\n' +
                      '> Assumption: ').strip('\'')

    while input_str not in ['Steady', 'Increasing', 'Decreasing', 'PosParabola', 'NegParabola']:
        input_str = input('Invalid input. ' +
                          'Choose one of \'Steady\', \'Increasing\', \'Decreasing\', \'PosParabola\', \'NegParabola\'.\n')

    return dIN_behaviours[input_str]


def get_IN_VOL():
    """
    Get Inflow and Volume values from user.
    """
    print('Please provide the Inflow and Volume magnitudes. Choose from \n' +
          '\'+\' (positive), \'-\' (negative), \'0\' (zero), \'M\' (maximum).')
    IN = check_magn_input('> Inflow: ')
    VOL = check_magn_input('> Volume: ')
    return IN, VOL

def influence(sign, Q1, Q2):
    if sign == '+' and Q1.M == POS:
        Q2.d = POS
    elif sign == '-' and Q1.M == POS:
        Q2.d = NEG

def proportional(sign, Q1, Q2):
    if sign == '+':
        if Q1.d == POS:
            Q2.d = POS
        if Q1.d == ZERO:
            Q2.d = ZERO
    # elif sign == '-' and Q1.d == POS:
    #     Q2.d = NEG

def correspondence(value, quantity, *quants):
    if quantity.M == value:
        for q in quants:
            q.M = value


def main():
    inflow.M, volume.M = get_IN_VOL()
    dIN_list = get_dIN_list()
    inflow.d = dIN_list[0]

    initial_state = State(inflow, volume, height, pressure, outflow)

    reasoner = Reasoner(initial_state, dIN_list)
    reasoner.do_reasoning()
    # print(initial_state.str())
    # reasoner = Reasoner(initial_state)
    #
    # next_state = reasoner.reasoning_step(initial_state)
    # print(next_state.str())
    #
    # third_state = reasoner.reasoning_step(next_state)
    # print(third_state.str())

if __name__ == "__main__":
    main()

# defining constants
MAX = 2
POS = 1
ZERO = 0
NEG = -1

NUM_QUANTITIES = 5

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
    def __init__(self, magnitude, derivative):
        self.M = magnitude
        self.d = derivative

quantities = [inflow, volume, height, pressure, outflow] = list((Quantity(None, None) for i in range(NUM_QUANTITIES)))

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
    if sign == '+' and Q1.d == POS:
        Q2.d = POS
    elif sign == '-' and Q1.d == POS:
        Q2.d = NEG

def correspondence(value, quantity, *quants):
    if quantity.M == value:
        for q in quants:
            q.M = value

def main():
    inflow.M, volume.M = get_IN_VOL()
    dIN_list = get_dIN_list()
    inflow.d = dIN_list[0]


if __name__ == "__main__":
    main()
# This is for the QR Project, KR Course

# We aim to make an algorithm crating the state graph for modeling sink behaviour

import sys
import copy
from graphviz import Digraph
import random
random.seed(2)

def get_state ():
  '''This let the user specify the entire initial state'''
  
  inflw_mag = raw_input("Initial magnitude of the inflow: ")
  inflw_der = raw_input("Initial derivative of the inflow: ")
  inflw = {"mag": inflw_mag, "der": inflw_der}
  
  vol_mag = raw_input("Initial magnitude of the volume: ")
  vol_der = raw_input("Initial derivative of the volume: ")
  vol = {"mag": vol_mag, "der": vol_der}
  
  outflw_mag = raw_input("Initial magnitude of the outflow: ")
  outflw_der = raw_input("Initial derivative of the outflow: ")
  outflw = {"mag":  outflw_mag, "der": outflw_der}
  
  return {"inflow": inflw, "volume": vol, "outflow": outflw}

def value_cor (quant1, quant2, val, state, no_state):
  ''' Finds the state that has the value correspondance property between quant1
  and quant2, from state, that is not no_state'''
  
  if state[quant1]['mag'] != state[quant2]['mag']:
    if no_state[quant1]['mag'] == state[quant1]['mag']:
      state[quant1]['mag'] = state[quant2]['mag']
    else:
      state[quant2]['mag'] = state[quant1]['mag']

  if state[quant1]['der'] != state[quant2]['der']:
    if no_state[quant1]['der'] == state[quant1]['der']:
      state[quant1]['der'] = state[quant2]['der']
    else:
      state[quant2]['der'] = state[quant1]['der']
  
  return state

def stabilise_state (state, no_state):
  '''Make sure that the proportionality and influence relations were applied to 
  the state, so that it is stable away from no_state
  Ambiguity asks if there is ok to have <?>'''
  
  old_state = copy.deepcopy(state)
  
  # Volume P+ outflow
  state['outflow']['der'] = state['volume']['der']
  
  # Value correspondances between outflow and volume
  state = value_cor('volume', 'height', '0', state, no_state)
  state = value_cor('height', 'pressure', '0', state, no_state)
  state = value_cor('pressure', 'outflow', '0', state, no_state)
  state = value_cor('volume', 'height', 'M', state, no_state)
  state = value_cor('height', 'pressure', 'M', state, no_state)
  state = value_cor('pressure', 'outflow', 'M', state, no_state)
  
  # Inflow I+ volume and  Outflow I- vloume
  if state['inflow']['mag'] == '+': 
    if state['outflow']['mag'] == '0':
      state['volume']['der'] = '+'
    #elif:
      #state['volume']['der'] = '?'
      # so anything is good and no stabilisation is needed
      
  else:
    if  state['outflow']['mag'] == '0':
      state['volume']['der'] = '0'
    else:
      state['volume']['der'] = '-'

  state = value_cor('volume', 'height', '0', state, no_state)
  state = value_cor('height', 'pressure', '0', state, no_state)
  state = value_cor('pressure', 'outflow', '0', state, no_state)
  state = value_cor('volume', 'height', 'M', state, no_state)
  state = value_cor('height', 'pressure', 'M', state, no_state)
  state = value_cor('pressure', 'outflow', 'M', state, no_state)
  
  if old_state != state:
    state = stabilise_state (state, no_state)
  
  return state

def add_stabilised_state (l, state, quant_name, quant_val):
  '''This adds a states with the i^th quantity replaced by quant to l, if it was
  not already there
  Used for the next state function
  Ambiguity asks if there is ok to have <?>'''
    
  new_state = copy.deepcopy(state)
  new_state[quant_name] = quant_val
  new_state = stabilise_state(new_state, state)
  
  if new_state not in l and new_state != state:
    # Check the validity of the state
    is_valid = 1
    for q_name, q_val in new_state.items():
      if q_val['mag'] == '0' and q_val['der'] == '-':
        is_valid = 0
      elif q_val['mag'] == 'M' and q_val['der'] == '+':
        is_valid = 0
    if new_state['inflow'] == {'mag': '0', 'der': '0'} and new_state['volume']['der'] == '+':
        is_valid = 0
    if new_state['inflow']['der'] == '+' and new_state['volume']['mag'] == 'M':
        is_valid = 0
    if new_state['inflow'] == {'mag': '0', 'der': '0'} and new_state['volume'] == {'mag': '+', 'der': '0'} :
        is_valid = 0
    if new_state['inflow'] == {'mag': '+', 'der': '+'} and new_state['volume']['der'] == '-':
        is_valid = 0
    if new_state['inflow'] == {'mag': '+', 'der': '0'} and new_state['volume'] == {'mag': '0', 'der': '+'}:
        is_valid = 0
    if new_state['inflow'] == {'mag': '+', 'der': '0'} and new_state['volume'] == {'mag': '+', 'der': '-'}:
        is_valid = 0
    if new_state['inflow'] == {'mag': '+', 'der': '-'} and new_state['volume'] == {'mag': '0', 'der': '+'}:
        is_valid = 0
    if new_state['inflow'] == {'mag': '+', 'der': '0'} and new_state['volume'] == {'mag': 'M', 'der': '-'}:
        is_valid = 0
    if new_state['inflow'] == {'mag': '0', 'der': '0'} and new_state['volume'] == {'mag': 'M', 'der': '-'}:
        is_valid = 0
    if new_state['inflow'] == {'mag': '+', 'der': '-'} and new_state['volume'] == {'mag': '+', 'der': '+'}:
        is_valid = 0
    if new_state['inflow'] == {'mag': '0', 'der': '+'} and new_state['volume'] == {'mag': '+', 'der': '0'}:
        is_valid = 0
    if is_valid:
      l.append(new_state)
  
  return l

def illegal_transition(old_state, new_state):
  if old_state['inflow'] == {'mag': '+', 'der': '+'} and old_state['volume'] == {'mag': '+', 'der': '+'} \
          and new_state['inflow'] == {'mag': '+', 'der': '+'} and new_state['volume'] == {'mag': '+', 'der': '0'}:
    return True
  if old_state['inflow'] == {'mag': '+', 'der': '0'} and old_state['volume'] == {'mag': '+', 'der': '0'} \
          and new_state['inflow'] == {'mag': '+', 'der': '0'} and new_state['volume'] == {'mag': '+', 'der': '+'}:
    return True
  if old_state['inflow'] == {'mag': '+', 'der': '-'} and old_state['volume'] == {'mag': 'M', 'der': '0'} \
          and new_state['inflow'] == {'mag': '+', 'der': '0'} and new_state['volume'] == {'mag': 'M', 'der': '0'}:
    return True
  if old_state['inflow'] == {'mag': '+', 'der': '+'} and old_state['volume'] == {'mag': '+', 'der': '0'} \
          and new_state['inflow'] == {'mag': '+', 'der': '0'} and new_state['volume'] == {'mag': '+', 'der': '0'}:
    return True
  if old_state['inflow'] == {'mag': '+', 'der': '-'} and old_state['volume'] == {'mag': '+', 'der': '-'} \
          and new_state['inflow'] == {'mag': '+', 'der': '-'} and new_state['volume'] == {'mag': '+', 'der': '0'}:
    return True
  if old_state['inflow'] == {'mag': '+', 'der': '-'} and old_state['volume'] == {'mag': '+', 'der': '0'} \
          and new_state['inflow'] == {'mag': '+', 'der': '0'} and new_state['volume'] == {'mag': '+', 'der': '0'}:
    return True
  if old_state['inflow'] == {'mag': '+', 'der': '-'} and old_state['volume'] == {'mag': '+', 'der': '0'} \
          and new_state['inflow'] == {'mag': '+', 'der': '-'} and new_state['volume'] == {'mag': '+', 'der': '+'}:
    return True
  if old_state['inflow'] == {'mag': '+', 'der': '-'} and old_state['volume'] == {'mag': 'M', 'der': '0'} \
          and new_state['inflow'] == {'mag': '0', 'der': '0'} and new_state['volume'] == {'mag': 'M', 'der': '-'}:
    return True
  if old_state['inflow']['der'] == '+' and new_state['inflow']['mag'] == '0':
    return True
  if old_state['volume']['der'] == '+' and new_state['volume']['der'] == '-':
    return True
  return False

def next_state (state):
  '''Find possible next states from the current ones'''
  new_states = []
  
  # Add new state if derivative is positive, but value is 0
  for i, quanty in state.items():
    if quanty['der'] == '+' and quanty['mag'] == '0':
      new_states = add_stabilised_state(new_states, state, i, 
        {'mag': '+', 'der':'+'})
    elif quanty['der'] == '-' and quanty['mag'] == 'M':
      new_states = add_stabilised_state(new_states, state, i, 
        {'mag': '+', 'der':'-'})
  
  # If no such states can be added, then do other changes
  if len(new_states) == 0:
    # If derivative is positive, and quantity is at 0/+, then it can go to +/max
    # Similarly derivative is -, and quantity is +/M, then it can go to 0/+
    for quant_name, quant_val in state.items():
      if quant_name != 'inflow'and quant_val['der'] == '+' and quant_val['mag'] == '+':
        next_val = {'mag': 'M', 'der': '0'}
        new_states = add_stabilised_state(new_states, state, quant_name, next_val)
      elif quant_val['der'] == '+' and quant_val['mag'] == '0':
        next_val = {'mag': '+', 'der': '+'}
        new_states = add_stabilised_state(new_states, state, quant_name, next_val)
      elif quant_val['der'] == '-' and quant_val['mag'] == '+':
        next_val = {'mag': '0', 'der': '0'}
        new_states = add_stabilised_state(new_states, state, quant_name, next_val)
      elif quant_val['der'] == '-' and quant_val['mag'] == 'M':
        next_val = {'mag': '+', 'der': '-'}
        new_states = add_stabilised_state(new_states, state, quant_name, next_val)
    
    # Can change the derivative of the inflow from +/- to 0, and from 0 to either
    for quant_name, quant_val in state.items():
      if quant_val['der'] == '0':
        next_val = copy.deepcopy(quant_val)
        next_val['der'] = '+'
        new_states = add_stabilised_state(new_states, state, quant_name, next_val)
      
        next_val = copy.deepcopy(quant_val)
        next_val['der'] = '-'
        new_states = add_stabilised_state(new_states, state, quant_name, next_val)
      
      else:
        next_val = copy.deepcopy(quant_val)
        next_val['der'] = '0'
        new_states = add_stabilised_state(new_states, state, quant_name, next_val)
  
  return new_states




# From here on, all functions are for graph generation purposes
def start_state ():
  '''This returns the start state'''
  
  inflw = {"mag": '0', "der": '0'}
  vol = {"mag": '0', "der": '0'}
  height = {"mag": '0', "der": '0'}
  pressure = {"mag": '0', "der": '0'}
  outflw = {"mag":  '0', "der": '0'}
  
  return {"inflow": inflw, "volume": vol, "height": height, "pressure": pressure, "outflow": outflw}

def state_label(state):
  '''Returns the lable for the node representing that state'''
  
  label = ''
  for quant_name, quant_val in sorted(state.items()):
    label = label + quant_val['mag'] + quant_val['der']
  
  return label

def state_description (state):
  '''Retruns the description of a state'''
  
  descn = ''
  line_breake = 0

  descn += 'inflow: (' + state['inflow']['mag'] + ', ' + state['inflow']['der'] + ')\n'
  descn += 'volume: (' + state['volume']['mag'] + ', ' + state['volume']['der'] + ')\n'
  descn += 'height: (' + state['height']['mag'] + ', ' + state['height']['der'] + ')\n'
  descn += 'pressure: (' + state['pressure']['mag'] + ', ' + state['pressure']['der'] + ')\n'
  descn += 'outflow: (' + state['outflow']['mag'] + ', ' + state['outflow']['der'] + ')'

  # for quant_name, quant_val in state.items():
  #   if line_breake:
  #     descn = descn + '\\n'
  #   descn = descn + quant_name + ': (' +  quant_val['mag'] + ', ' + quant_val['der'] + ')  '
  #   line_breake = 1
  
  return descn

def create_trace(dot, queue):
  traced_states = []
  while len(queue):
    cur_state = queue[0]
    del queue[0]

    if cur_state not in traced_states:
      next_states = next_state(cur_state)
      new_state = random.choice(next_states)
      queue.append(new_state)
      if cur_state not in traced_states and (traced_states == [] or not illegal_transition(traced_states[-1], new_state)):
        desc = state_description(new_state)
        dot.node(state_label(new_state), desc, shape='box')
        dot.edge(state_label(cur_state), state_label(new_state), color='red')
      traced_states.append(cur_state)
    else:
      traced_states.append(cur_state)

  return dot, traced_states


def graph_gen(start=start_state(), trace=False):
  '''This creates the state graph with random variation of inflow'''

  dot = Digraph('State Graph')

  change = 1
  vizited = []
  in_graph = []
  queue = [start]
  dot.node(state_label(start), state_description(start))

  while len(queue):
    cur_state = queue[0]
    del queue[0]

    if cur_state not in vizited:
      vizited.append(cur_state)

      next_states = next_state(cur_state)
      queue = queue + next_states

      for state in next_states:
          if state not in in_graph:
            dot.node(state_label(state), state_description(state), shape='box')
            in_graph.append(state)

          if not illegal_transition(cur_state, state):
            dot.edge(state_label(cur_state), state_label(state))

  dot.edge('+-0++-+-+-', '+0+++0+0+0')
  dot.edge('+++0++++++', '+0+-+0+0+0')
  dot.edge('++++++++++', 'M0+0M0M0M0')
  dot.render('state_graph.gv')

  if trace:
    dot.clear()
    queue = [start]
    dot, traced_states = create_trace(dot, queue)
    counter = 0
    while (traced_states == [] or traced_states[-1]['inflow']['mag'] == '+' or {'inflow' : {'mag': '+', 'der': '+'}, 'volume': {'mag': '+', 'der': '0'}, 'height': {'mag': '+', 'der': '0'}, 'pressure': {'mag': '+', 'der': '0'}, 'outflow': {'mag': '+', 'der': '0'}} in traced_states) and counter < 100:
      queue = [start]
      dot.clear()
      dot, traced_states = create_trace(dot, queue)
      counter += 1
    if counter >= 100:
      exit("Unknown error while creating a trace, please try again.\n(This may happen many times, sorry)")

    dot.render('trace.gv')

    for i, traced_state in enumerate(traced_states):
      if i == 0:
        print("State 1 (starting state, all quantities are 0):\n" + state_description(traced_state))
      elif i > 0 and traced_state['inflow'] == {'mag': '0', 'der': '0'} and traced_state['volume'] == {'mag': '0', 'der': '0'}:
        print("\nState 1:\n" + state_description(traced_state) + "\n")
      else:
        print("\nState " + str(i+1) + ":\n" + state_description(traced_state) + "\n")

      if traced_states[i-1]['inflow']['der'] == '-' and traced_state['volume']['mag'] == 'M':
        print("Because inflow has decreased in state " + str(i) + ", but outflow is still maximum, volume decreases in state " +
        str(i+1) + ".")
      if traced_states[i-1]['volume']['der'] == '-' and traced_states[i-1]['volume']['mag'] == 'M':
        print("Because volume has decreased from the maximum in state " + str(i) + ", volume is + in state " + str(i+1) + ".")
      if i > 0 and traced_states[i-1]['inflow']['der'] == '+' and traced_state['inflow']['der'] == '0' and \
                      traced_state['inflow']['mag'] == '+':
        print("Inflow stopped increasing in state " + str(i+1) + ", but is still +, so volume remains increasing " +
              "(because of the positive influence (I+) from inflow to volume).")
      if traced_state['inflow']['der'] == '-' and traced_states[i-1]['inflow']['der'] != '-':
        print("Inflow starts decreasing in state " + str(i+1) + ".")
      if i > 0 and traced_states[i-1]['inflow']['der'] == '-' and traced_state['inflow']['mag'] == '0':
        print("Inflow reaches zero in state " + str(i+1) + " (and therefore stops decreasing).")
      if traced_state['volume'] == {'mag': 'M', 'der': '0'} and traced_states[i-1]['volume'] != {'mag': 'M', 'der': '0'}:
        print("Volume reaches the maximum in state " + str(i+1) + ", and therefore stops increasing.")
      if i < len(traced_states) - 1 and i != 0:
        for quant, val in traced_state.items():
          if quant == 'inflow' or quant == 'volume':
            if traced_state[quant]['der'] == '+' and traced_states[i+1][quant]['mag'] in '+M' and traced_state[quant]['mag'] != '+':
              print("Because " + quant + " is increasing (from " + traced_states[i][quant]['mag'] + ") in state " +
                    str(i+1) + ", " + quant + " is " + traced_states[i+1][quant]['mag'] + " in state " + str(i+2) + ".")
        if traced_states[i+1]['inflow']['mag'] == '+' and traced_states[i+1]['volume']['der'] == '+':
          print("Because inflow is + in state " + str(i+2) + ", volume is increasing in state " + str(i+2) +
                " (because of the positive influence (I+) from inflow to volume).")
      if i > 1 and traced_state['volume'] == {'mag': '0', 'der': '0'}:
        print("Volume has reached 0 (and therefore stops decreasing).")
      if i > 1 and traced_states[i-1]['volume'] != traced_state['volume']:
        print("Height, pressure and outflow are also (" + traced_state['volume']['mag'] + ", " + traced_state['volume'][
          'der'] + ") because of the value correspondence between volume, height, pressure and outflow.")
      if i > 0 and traced_state['inflow'] == {'mag': '0', 'der': '0'} and traced_state['volume'] == {'mag': '0', 'der': '0'}:
        print("All quantities have reached 0, thus we are at the starting state again.")

  return len(vizited)

graph_gen(trace=True)
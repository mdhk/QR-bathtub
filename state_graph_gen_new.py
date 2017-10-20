# This is for the QR Project, KR Course

# We aim to make an algorithm crating the state graph for modeling sink behaviour

import sys
import copy
from graphviz import Digraph

def get_state ():
  '''This let the user specify the entireinitial state'''
  
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
  
  if state[quant1]['mag'] != state[quant2]['mag'] and (
    state[quant1]['mag'] == val or state[quant2]['mag'] == val):
    if no_state[quant1]['mag'] == state[quant1]['mag']:
      state[quant1]['mag'] = state[quant2]['mag']
    else:
      state[quant2]['mag'] = state[quant1]['mag']
  
  return state

def stabilise_state (state, no_state):
  '''Make sure that the proportionality and influence relations were applied to 
  the state, so that it is stable away from no_state
  Ambiguity asks if there is ok to have <?>'''
  
  old_state = copy.deepcopy(state)
  
  # Volume P+ outflow
  state['outflow']['der'] = state['volume']['der']
  
  # Value correspondances between outflow and volume
  state = value_cor('volume', 'outflow', '0', state, no_state)
  state = value_cor('volume', 'outflow', 'M', state, no_state)
  
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
    for q_name, q_val in new_state.iteritems():
      if q_val['mag'] == '0' and q_val['der'] == '-':
        is_valid = 0
      elif q_val['mag'] == 'M' and q_val['der'] == '+':
        is_valid = 0
        
    if is_valid:
      l.append(new_state)
  
  return l

def next_state (state):
  '''Find possible next states from the current ones'''
  new_states = []
  
  # Add new state if derivative is positive, but value is 0
  for i, quanty in state.iteritems():
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
    for quant_name, quant_val in state.iteritems():
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
    for quant_name, quant_val in state.iteritems():
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
  outflw = {"mag":  '0', "der": '0'}
  
  return {"inflow": inflw, "volume": vol, "outflow": outflw}

def state_label (state):
  '''Returns the lable for the node representing that state'''
  
  label = ''
  for quant_name, quant_val in state.iteritems():
    label = label + quant_val['mag'] + quant_val['der']
  
  return label

def state_description (state):
  '''Retruns the description of a state'''
  
  descn = ''
  line_breake = 0
  for quant_name, quant_val in state.iteritems():
    if line_breake:
      descn = descn + '\\n'
    descn = descn + quant_name + ': (' +  quant_val['mag'] + ', ' + quant_val['der'] + ')  '
    line_breake = 1
  
  return descn

def graph_gen():
  '''This creates the state graph with random variation of inflow'''
  
  dot = Digraph(comment = 'State Graph')
  
  change = 1
  vizited = []
  in_graph = []
  start = start_state()
  queue = [start]
  dot.node (state_label(start), state_description(start))
   
  while len(queue):
    cur_state = queue[0]
    del queue[0]
    
    if cur_state not in vizited:
      vizited.append(cur_state)
      
      next_states = next_state(cur_state)
      queue = queue + next_states
      
      for state in next_states:
        if state not in in_graph:
          dot.node (state_label(state), state_description(state), shape = 'box')
          in_graph.append(state)
        
        dot.edge(state_label(cur_state), state_label(state), constraint='false')
  
  dot.render('state_graph.gv', view=True)
  
  return len(vizited)
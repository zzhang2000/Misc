# Given a list of positive numbers [x1,...,xn], and arithmetic operations +,-.*,/
# find the closest estimate to a target number t, or stop at a threshold epsilon
# e.g., use 1,2,...9 each once, find a close estimate to euler's number e, up to 1e-8

import itertools as it
import numpy as np
import time
import click

# Given a,b, there are effectively five results a+b, a*b, abs(a-b), a/b, b/a
# We use abs(a-b) because any negative intermediate result can be substituted by subtracting its abs value later
# We denote b/a by a\b
# This way we can apply operations to non-ordered pairs in the array, instead of ordered pairs, thus reduce search space
OPERATIONS_TO_USE = ['+', '-', '*', '/', '\\']


def eval_one_op(a: float, b: float, o: str):
    if   o == '+': r = a+b
    elif o == '-': r = abs(a-b)
    elif o == '*': r = a*b
    elif o == '/': r = a/b if b != 0 else 0
    elif o == '\\': r = b/a if a !=0 else 0
    return r


# output list of array of triples
# each triple is of form [i,j,o] where 0<i<j<=idx
# representing the ith and jth element to be replaced by applying operation o
# the upper bound idx starts with n and shrinks by 1
def all_ops_sequence(n: int):
    results = list()
    for idx in range(n,1,-1):
        triples = list()
        for i in range(idx):
            for j in range(idx):
                for o in OPERATIONS_TO_USE:
                    if i < j:
                        triples.append([ i, j, o])
        results.append( triples.copy())
    return results


# Input of n number: x
# Operation array (of triples) to be applied to x: ops_sequence
# Return the final number
def eval_ops_sequence(x, ops_sequence):
    y = np.array(x).astype(float)  # need array copy also avoid taking int array and mess up / operations!
    n = len(x)
    for idx, op in enumerate( ops_sequence):
        r = eval_one_op( y[op[0]], y[op[1]], op[2])
        # replace one element with new value,
        # effectively delete the other one by swapping with the last element in the array
        # as later operations are applied on a shrinking front end of the array, no actual deletions are need
        y[op[0]] = r
        y[op[1]] = y[n-idx-1]
    return y[0]

def add_parenthesis( x, symbols=['+','-'] ):
    add_p = False
    for s in symbols:
        if s in x: add_p = True
    return '(' + x +')' if add_p else x

def str_one_op(a: str, b: str, o: str):
    if   o == '+':
        r = a + '+' + b
    elif o == '-':
        r = a + '-' + add_parenthesis(b) if eval(a)-eval(b)>0 else b + '-' + add_parenthesis(a)
    elif o == '*':
        r = add_parenthesis(a) + '*' + add_parenthesis(b)
    elif o == '/':
        r = add_parenthesis(a) + '/' + add_parenthesis(b, ['+','-','*','/'])
    elif o == '\\':
        r = add_parenthesis(b) + '/' + add_parenthesis(a, ['+','-','*','/'])
    return r


def str_ops_sequence(x, ops):
    y = [ str(i) for i in x]
    len_y = len(y)
    for op in ops:
        r = str_one_op(y[ op[0]], y[op[1]], op[2])
        y[op[0]] = r
        y[op[1]] = y[len_y-1]
        len_y -= 1
    return y[0]


# Main algorithm is to consider the huge search space of operations that can be applied to the initial input array x
# Each operation consists of n-1 steps, n=len(x)
# At each step k, pick two indices i<j, apply operation o (one of +-*/) on ith and jth element,
#    and replace these two elements with result of this operation, shrinking the array size by 1
# Such operation is represented by n-1 triples and each triple is of the form [i,j,o] of type [int,int,str]
# The total iterations is 5^(n-1) * Prod C(k,2) (k from 2 to n)
#      Note 5 because there are effectively five operations a+b, abs(a-b), a*b, a/b, b/a for each non-ordered pair (a,b)
def find_best_estimates(x, target, epsilon =1e-8, test_only=False, find_all_solutions= False, print_progress=True ):
    start_time = time.time()
    n = len(x)
    all_ops = all_ops_sequence(n)
    best_est = -1
    best_ops = []
    count = 0
    solutions = []

    for ops in it.product( *all_ops):
        count +=1
        if test_only:
            continue
        est = eval_ops_sequence(x, ops)
        if abs(est-target) <= epsilon:
            best_est = est
            best_ops = ops
            str_ops = str_ops_sequence(x, best_ops)
            solutions.append(str_ops)
            if not find_all_solutions:
                break
        if best_est < 0 or abs(est - target) <= abs(best_est - target):
            best_est = est
            best_ops = ops
            str_ops = str_ops_sequence(x, best_ops)
            if print_progress:
                print(f"{str_ops} = {best_est}, error={abs(best_est-target)}, iteration={count:,}")
        if print_progress and count % 1e9 == 0:
            print( f"iteration={count:,}, time elapsed{time.time()-start_time}")
    if print_progress:
        print(f"{str_ops} = {best_est}, error={abs(best_est-target)}, total iterations={count:,}, time elapsed={time.time()-start_time}")
    return solutions
    #print(f"Test out by copy & paste the string, eval() in python or excel directly: {str_ops}")


def play_game24():
    while True:
        str_inputs = click.prompt('Please enter 4 integers or type Q to end')
        if str_inputs[0] in ['q', 'Q']:
            break
        str_inputs = str_inputs.split()
        int_inputs = [int(i) for i in str_inputs]
        solutions = find_best_estimates(int_inputs, 24, epsilon=0, find_all_solutions=True, print_progress=False)
        if len(solutions) == 0:
            print('No Solutions Found')
        for s in solutions:
            print(s)
    print( 'Thanks for playing 24')

@click.command()
@click.option('--interactive/--command', '-i', default=True, help='Interactive mode')
@click.option('--inputs', '-x', default='1 2 3 4 5 6',help='Input numbers')
@click.option('--target', '-t', default='np.e', help='Target')
@click.option('--epsilon', '-e', default=1e-8, help='Error bound')
@click.option('--findall/--first_only', default=False, help='find all or first solutions')
def run(interactive, inputs, target, epsilon, findall):
    if interactive:
        mode = click.prompt( 'Play game of 24 or solve general puzzle? Type one of y/Y/2/24 for 24')
        if mode in ['24','y','Y', '2']:
            play_game24()
        else:
            str_inputs = click.prompt( 'Please input list of numbers ')
            str_inputs = str_inputs.split()
            value_inputs = [float(i) for i in str_inputs]
            str_target = click.prompt( 'Please input target, use np.e or np.pi or e or pi ')
            value_target = eval( str_target )
            epsilon =  click.prompt( 'Please input error bound such as 1e-8', type=float)
            solutions = find_best_estimates(value_inputs, value_target, epsilon=epsilon, find_all_solutions=False, print_progress=True)
            if len(solutions) == 0:
                print('No Solutions Found')
            for s in solutions:
                print(s)
    else:
        str_inputs = inputs.split()
        value_inputs = [eval(i) for i in str_inputs]
        t = eval(target)
        solutions = find_best_estimates(value_inputs, t, epsilon=epsilon, find_all_solutions=findall)
        for s in solutions:
            print(s)


if __name__ == '__main__':
    # can remove/replace to reduce search space, e.g. drop 3 from input and change target to 3-np.e instead
    #input_x = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    #target_t = np.e
    #solutions= find_best_estimate(input_x, target_t)
    run()

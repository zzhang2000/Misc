# Given a list of positive numbers [x1,...,xn], and arithmetic operations +,-.*,/
# find the closest estimate to a target number t, or stop at a threshold epsilon
# e.g., use 1,2,...9 each once, find a close estimate to euler's number e, up to 1e-8

import itertools as it
import numpy as np
import time

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


def str_one_op(a: str, b: str, o: str):
    if   o == '+': r = a + '+' + b
    elif o == '-': r = 'abs(' + a + '-' + b + ')'
    elif o == '*': r = a + '*' + b
    elif o == '/': r = a + '/' + b
    elif o == '\\': r =  b + '/' + a
    return '(' + r + ')'


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
def main(x, target, epsilon =1e-8, test_only=False ):
    start_time = time.time()
    n = len(x)
    all_ops = all_ops_sequence(n)
    best_est = -1
    best_ops = []
    count = 0
    for ops in it.product( *all_ops):
        count +=1
        if test_only:
            continue
        est = eval_ops_sequence(x, ops)
        if abs( est-target) < epsilon:
            best_est = est
            best_ops = ops
            break
        if best_est < 0 or abs(est - target) < abs(best_est - target):
            best_est = est
            best_ops = ops
            print( str_ops_sequence(x, best_ops), '=', best_est, 'error=', abs(best_est-target), f"iteration={count:,}" )
        if count % 1e9 == 0:
            print( f"iteration={count:,}, time elapsed{time.time()-start_time}")
    print( f"{str_ops_sequence( x , best_ops )} = {best_est}, total iterations={count:,}, time elapsed={time.time()-start_time}" )


def solve_24(x):
    main( x, 24, epsilon=1e-10)


if __name__ == '__main__':
    # can remove/replace to reduce search space, e.g. drop 3 from input and change target to 3-np.e instead
    input_x = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    target_t = np.e
    main(input_x, target_t)


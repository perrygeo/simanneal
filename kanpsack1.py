# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 12:50:57 2019

@author: arush
"""
import math
import random
l=[]
l1=[]
l2=[]
l3=[]
def powerSet(items):
    """
    Power set generator: get all possible combinations of a list’s elements

    Input:
        items is a list
    Output:
        returns 2**n combination lists one at a time using a generator 

    Reference: edx.org 6.00.2x Lecture 2 - Decision Trees and dynamic programming
    """

    N = len(items)
    # enumerate the 2**N possible combinations
    for i in range(2**N):
        combo = []
        for j in range(N):
            # test bit jth of integer i
            if (i >> j) % 2 == 1:
                combo.append(items[j])
                
        yield combo
for i in powerSet(['a','b','c']):
        #print (i, ", ",  end="")
        l.append(i)
for i in powerSet([5,6,7]):
        #print (i, ", ",  end="")
        l1.append(i)
print(l)
print(l1)
wt=12;
a=0.9
t=100
eni=0
for i in range(1,5):
    x=sum(l1[i])
    if x<=wt:
        en=x
        endi=en-eni;
        if endi>=0:
            print("aa")
            l2.append(l[i])
            l3.append(en)
            eni=en
        elif endi<0 :
            print("b")
            q=math.exp(endi/t)
            if q>random.random():
                l2.append(l[i])
                l3.append(en)
    t=a*t            
    i=i+1;           
print(l2)
print(l3)           
            
        
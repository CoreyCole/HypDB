"""
@author: Kevin S. Brown, University of Connecticut

This source code is provided under the BSD-3 license, duplicated as follows:

Copyright (c) 2013, Kevin S. Brown
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this
list of conditions and the following disclaimer in the documentation and/or other
materials provided with the distribution.

3. Neither the name of the University of Connecticut  nor the names of its contributors
may be used to endorse or promote products derived from this software without specific
prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS
OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from numpy.random import randint

def randchoice(l):
    '''
    Returns and element from list l chosen at random.
    '''
    return l[randint(len(l))]

def randbit(size=None):
    '''
    Generates an array of shape size of random {0,1} bits.
    '''
    return randint(2,size=size)

def randspin(size=None):
    '''
    Generates an array of shape size of random {-1,1} spin variables.
    '''
    return 2*randbit(size=size) - 1

def randrot(dim=2):
    '''
    Grenerate a random rotation matrix drawn from the Haar distribution
    (the only uniform distribution on SO(n)). See:
    
    Stewart, G.W., 'The efficient generation of random orthogonal matrices with an
    application to condition estimators', SIAM Journal on Numerical Analysis, 17(3),
    pp. 403-409, 1980.

    For more details.

    INPUT:
        dim: int, optional
            the rotation matrix will be dim x dim
    '''
    H = eye(dim)
    D = ones((dim,))
    for n in range(1, dim):
        x = normal(size=(dim-n+1,))
        D[n-1] = sign(x[0])
        x[0] -= D[n-1]*sqrt((x*x).sum())
        # Householder transformation
        Hx = eye(dim-n+1) - 2.*outer(x, x)/(x*x).sum()
        mat = eye(dim)
        mat[n-1:,n-1:] = Hx
        H = dot(H, mat)
    # Fix the last sign such that the determinant is 1
    D[-1] = -D.prod()
    H = (D*H.T).T
    return H

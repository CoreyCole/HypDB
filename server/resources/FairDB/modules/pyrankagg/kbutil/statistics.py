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

from numpy import arange,correlate,newaxis,dot,sort,int,floor,log2,sqrt,abs,log
from numpy import ceil,interp,isnan,ones,asarray,argsort,zeros,linspace,power
from numpy import hanning,hamming,bartlett,blackman,r_,convolve,percentile
from numpy import histogram,argmin,argmax
from numpy.random import randint
from numpy.linalg import svd
from scipy.stats import pearsonr,spearmanr,kendalltau,skew
from scipy.special import gammaln


def iqr(x):
    """
    Computes the interquartile range of x.
    """
    q75,q25 = percentile(x,[75,25])
    return q75 - q25


def bin_calculator(x,method='sturges'):
    """
    Estimates the 'appropriate' number of bins for histograms of x, using a
    variety of rules in the literature. For methods which calculate the bin width,
    the number of bins can be computed via k = ceil((max(x) - min(x))/h).
    Supported methods (with N = len(x)) are:

    'sturges' : k = ceil(log2(N)) + 1

    'sqrt' : k = ceil(sqrt(N))

    'rice' : k = ceil(2*N^(1/3))

    'doane' : k = 1 + ceil(log2(N) + log2(1 + |s|/sigma_s))
        here s = skew(x), and sigma_s = sqrt(6*(N-1)/(N+1)(N+3))

    'scott' : h = 3.5*sigma/N^(1/3)
        here sigma is the sample standard deviation

    'fd' (Freedman-Diaconis) : h = 2*IQR(x)/N^(1/3)

    'meansq' : computes the optimal bin width (due to Stone) via minimization of
        mean squared error of the density estimate.  Numerically computes:
                        argmin_h J(h,x)
        where J(h,x) = {2/(h*(n-1)) - (n+1)/(n^2(n-1)h) sum_k N_k^2}.
        N_k is the number of samples in bin k.  This function is extremely noisy
        so a brute force search is performed.

    'bayes' : maximizes the log posterior of a piecewise constant model
        (following Knuth arXiv:physics/0605197v2); performs brute search in the
        range 1 to 100 bins.

    In all cases, this function returns the number of bins to use for the data
    in x.  Unsupported methods default to sturges.
    """
    N = len(x)
    if method is 'sturges':
        k = ceil(log2(N)) + 1
    elif method is 'sqrt':
        k = ceil(sqrt(N))
    elif method is 'rice':
        k = ceil(2*power(N,1./3.))
    elif method is 'doane':
        s = skew(x)
        sigma_s = sqrt((6.*(N-1))/((N+1)*(N+3)))
        k = ceil(1 + log2(N) + log2(1 + abs(s)/sigma_s))
    elif method is 'scott':
        h = 3.5*x.std()/power(N,1./3.)
        k = ceil((max(x) - min(x))/h)
    elif method is 'fd':
        h = 2*iqr(x)/power(N,1./3.)
        k = ceil((max(x) - min(x))/h)
    elif method is 'meansq':
        # define a function that computes J
        def J(h,x):
            N = len(x)
            k = ceil((max(x) - min(x))/h)
            Nk,_ = histogram(x,bins=k)
            return 2./(h*(N-1.)) - ((N+1.)/(h*(N-1.)*N**2))*(Nk**2).sum()
        # do a brute force search in h
        hmax = (max(x) - min(x))/5
        htry = linspace(0.01,hmax,256)
        jofh = zeros(len(htry))
        for i in xrange(len(htry)):
            jofh[i] = J(htry[i],x)
        hopt = htry[argmin(jofh)]
        k = ceil((max(x) - min(x))/hopt)
    elif method is 'bayes':
        maxk = 100
        logp = zeros(maxk)
        for M in xrange(1,maxk+1):
            Nk,_ = histogram(x,bins=M)
            logp[M-1] = N*log(M) + gammaln(M/2.) - gammaln(N+M/2.) - M*gammaln(1./2.) + gammaln(Nk + 0.5).sum()
        k = argmax(logp) + 1
    else:
        print('ERROR: Unsupported method.  Defaulting to \'sturges\'')
        k = ceil(log2(N)) + 1
    return int(k)


def spearman_footrule_distance(s,t):
    """
    Computes the Spearman footrule distance between two full lists of ranks:

        F(s,t) = sum[ |s(i) - t(i)| ]/S,

    the normalized sum over all elements in a set of the absolute difference between
    the rank according to s and t.  As defined, 0 <= F(s,t) <= 1.

    S is a normalizer which is equal to 0.5*len(s)^2 for even length ranklists and
    0.5*(len(s)^2 - 1) for odd length ranklists.

    If s,t are *not* full, this function should not be used. s,t should be array-like
    (lists are OK).
    """
    # check that size of intersection = size of s,t?
    assert len(s) == len(t)
    sdist = sum(abs(asarray(s) - asarray(t)))
    # c will be 1 for odd length lists and 0 for even ones
    c = len(s) % 2
    normalizer = 0.5*(len(s)**2 - c)
    return sdist/normalizer


def standardize(X,stype='row'):
    """
    Standardizes (mean subtraction + conversion to unit variance) the array X,
    according to either rows or columns.
    """
    if stype == 'row':
        return (X - X.mean(axis=1)[:,newaxis])/X.std(axis=1)[:,newaxis]
    return (X - X.mean(axis=0)[newaxis,:])/X.std(axis=0)[newaxis,:]


def autocovariance(X,norm=False):
    """
    Computes the autocovariance function of X:
        phi(T) = 1/(N-T) sum_i X'(t_i)*X'(t_i - T)
    As T gets closer and closer to N, the autocovariance becomes less and less well
    estimated, since the number of valid samples goes down.

    This version computes phi(T) at all T (0,...N-1).

    If norm = True, the autocorrelation (phi(T)/phi(0)), rather than the
    bare autocovariance is returned.
    """
    Xp = X - X.mean()
    phi = (1.0/(len(X) - arange(0,len(X))))*correlate(Xp,Xp,"full")[len(X)-1:]
    if norm:
        return phi/phi[0]
    return phi


def cross_corrmatrix(X,Y):
    """
    For two data matrices X (M x T) and Y (N x T), corrmatrix(X,Y) computes the M x N set
    of pearson correlation coefficients between all the rows of X and the rows of Y.  X and
    Y must have the same column dimension for this to work.
    """
    assert X.shape[1] == Y.shape[1]
    # row standardize X and Y
    X = (X - X.mean(axis=1)[:,newaxis])/X.std(axis=1)[:,newaxis]
    Y = (Y - Y.mean(axis=1)[:,newaxis])/Y.std(axis=1)[:,newaxis]
    return dot(X,Y.T)/X.shape[1]

def covmatrix(X):
    '''
    Computes the N x N covariance matrix for an N x p data matrix X.
    '''
    cX = X - X.mean(axis=1)[:,newaxis]
    return dot(cX,cX.T)/(cX.shape[0] - 1)


def corrmatrix(X):
    '''
    Computes the N x N correlation matrix for an N x p data matrix X.
    '''
    sX = (X - X.mean(axis=1)[:,newaxis])/X.std(axis=1)[:,newaxis]
    return dot(sX,sX.T)/(sX.shape[0] - 1)


def empirical_ci(x,alpha=0.05):
    """
    Computes an empirial (alpha/2, 1-alpha/2) confidence interval for the distributional data
    in x.  Returns a tuple (lb,ub) which are the lower and upper bounds for the coverage
    interval.
    """
    assert alpha > 0.0
    xtilde = sort(x)
    xl = (alpha/2)*len(x)
    xu = (1.0 - alpha/2)*len(x)
    l1 = int(floor(xl))
    l2 = int(ceil(xl))
    u1 = int(floor(xu))
    u2 = int(ceil(xu))
    lb = interp(xl,[l1,l2],[xtilde[l1],xtilde[l2]])
    up = interp(xu,[u1,u2],[xtilde[u1],xtilde[u2]])
    return lb,ub


def bootstrap_correlation(x,y,cType='pearson',p=0.05,N=5000):
    """
    Computes a simple bootstrap CI on simple correlation coefficients.  The CI is
    computed using the interval method.  This won't work properly if x or y are time-series
    with significant autocorrelation.  You need to downsample or use a more complicated
    bootstrap that preserves that structure.

    Parameters:
    ------------
    x,y   : (1D) lists or arrays of data
    cType : string, optional
            should be 'pearson', 'spearman', or 'kendall'
    p     : float, optional
            the coverage interval will cover 1-p of the cumulative distribution
    N     : integer, optional
            number of bootstrap replications

    Returns:
    ------------
    rho,rL,rU : r(x,y) and lower, upper bounds for 1-p CI

    """
    corrTable = {'pearson': pearsonr, 'spearman': spearmanr, 'kendall': kendalltau}
    try:
        corr = corrTable[cType]
    except KeyError:
        # default to pearson
        print 'WARNING: Correlation type not supported. Defaulting to Pearson.'
        corr = pearsonr
    rho = corr(x,y)[0]
    rhobs = list()
    nSamp = len(x)
    iB = 0
    while iB < N:
        randx = randint(nSamp,size=(nSamp,))
        val = corr(x[randx],y[randx])[0]
        if not isnan(val):
            rhobs.append(val)
            iB = iB + 1
    # obtain the coverage interval
    rL,rU = empirical_ci(rhobs,alpha=p)
    return rho,rL,rU


def smooth(x,wlen=11,window='flat'):
    """Smooth the data using a window with requested size.

    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.

    Parameters:
    ------------
     x      : array type, required
              the input signal to smoothed
     wlen   : integer, odd, optional
              the size of the smoothing window; should be an odd integer
     window : string, optional
              the type of window. allowed choices are:
                 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
              'flat' produces a moving average.

    Returns:
    ------------
    y : array type
        the smoothed signal

    Example:
    ------------
    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)

    Stolen from the scipy cookbook and modified.
    """
    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."
    if x.size < wlen:
        raise ValueError, "Input vector needs to be bigger than window size."
    if wlen < 3:
        return x
    # dictionary of allowed windows
    winTable = {'flat' : ones, 'hanning' : hanning, 'hamming' : hamming, 'bartlett' : bartlett, 'blackman' : blackman}
    try:
        w = winTable[window]
    except KeyError:
        # default to flat
        print 'WARINING: Unsupported window type. Defaulting to \'flat\'.'
        w = winTable['flat']
    w = w(wlen)
    # wrap ends around and convolve with the scaled window
    s=r_[2*x[0]-x[wlen-1::-1],x,2*x[-1]-x[-1:-wlen:-1]]
    y=convolve(w/w.sum(),s,mode='same')
    # return vector with bogus ends trimmed
    return y[wlen:-wlen+1]


def discrete_frequency_calculator(intList):
    '''
    Accepts a list of integer values, returning two numpy arrays of values and frequencies.
    The output frequencies are normalized so that sum(Pn) = 1.0.  Input values are requried
    to be integer; no binning is performed for floating point values.

    INPUT
    ------
    intList: list of integers, required
             input list of data of integer type

    OUTPUT
    ------
    n,Pn : two lists of values and freq(values)
           frequencies are normalized so that sum(Pn) = 1.0, and the two returned
           arrays are in 1-1 correspondence, sorted in order of increasing n

    '''
    assert all([type(x) == int for x in intList])
    freq = {}
    n = len(intList)
    for k in intList:
        pkinc = 1.0/n
        if not freq.has_key(k):
            freq[k] = pkinc
        else:
            freq[k] += pkinc
    # sorting
    indx = argsort(freq.keys())
    return asarray([freq.keys()[x] for x in indx]),asarray([freq.values()[x] for x in indx])


def cdf_sparse(data):
    '''
    Computes the (empirical) cumulative distribution F(x) of data, defined as:

                F(x) = int_a^b p(x) dx

    or as a sum.  This function only computes F(x) at the data values; to
    get a "stairstep" plot of the cdf use cdist_dense.

    INPUT
    ------
    data  : array-like, required
            input data

    OUTPUT
    ------
    dsort : array
            sorted data (increasing)

    cdf : array
          cdf, evaluated at the values in dsort
    '''
    # sort the data
    data_sorted = sort(data)
    # calculate the proportional values of samples
    p = 1. * arange(len(data)) / (len(data) - 1)
    return data_sorted,p


def cdf_dense(data,limits,npts=1024):
    '''
    Computes the (empirical) cumulative distribution F(x) of samples in data, over
    a specified range and number of support points. F(x) is defined as:

                F(x) = int_a^b p(x) dx

    or as a sum.

    INPUT
    ------
    data   : array-like, required
             input data

    limits : array-like, required
             cdf is computed for npts values between limits[0] and limits[1]

    npts   : int, optional
             number of support points to evaluate cdf

    OUTPUT
    ------
    x : array
        support for the cdf

    cdf : array
          cdf, evaluated at the values x
    '''
    # sort the data
    data_sorted = sort(data)
    x = linspace(limits[0],limits[1],npts)
    Fofx = zeros(len(x))
    for i in xrange(0,len(x)):
        Fofx[i] = sum(data_sorted <= x[i])
    return x,1.0*Fofx/len(data)


def pca(X,k):
    '''
    PCA decomposition of matrix X.  X is assumed to be N x p, where p is the
    number of samples (backwards from many PCA implementations).  If you want
    the p x N version, just transpose what comes out of this function.

    k is the number of components to retain  (probably determined by some PCA stopping rule).

    Returns the matrix of eigenvectors of X (the "mixing matrix") and the "signals"
    (projection of the data onto the first k components).
    '''
    # row center the data matrix
    cX = X - X.mean(axis=1)[:,newaxis]
    C = covmatrix(cX)
    # singular value decomp
    _,s,W = svd(C)
    # select first k columns
    W = W[:,:k]
    # compute signal matrix
    S = dot(W.T,X)
    # need to do something about the units
    return W,S

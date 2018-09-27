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

3. Neither the name of the University of Connecticut nor the names of its contributors
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

import pylab
from numpy import ceil,log2,histogram,abs,linspace,zeros,inf,log,vstack
from numpy import min as npmin
from numpy import max as mpmax
from numpy.random import randn
from scipy.stats import gaussian_kde
from matplotlib.ticker import FuncFormatter
from matplotlib import colors

_colors = ('k','r','orange','gold','g','b','purple','magenta',
           'firebrick','coral','yellow','limegreen','dodgerblue','indigo','orchid',
           'tomato','darkorange','greenyellow','darkgreen','deepskyblue','indigo','deeppink')
_symbols = ('o','s','^','<','>','x','D','h','p')
_lines = ('-','--','-.',':')

def color_wheel(colors=_colors,symbols=_symbols,lines=_lines):
    """
    Returns a generator that cycles through a selection of colors,symbols,
    lines styles for matplotlib.plot.  Thanks to Ryan Gutenkunst for this
    idiom.
    """
    if not colors:
        colors = ('',)
    if not symbols:
        symbols = ('',)
    if not lines:
        lines = ('',)

    while 1:
        for l in lines:
            for s in symbols:
                for c in colors:
                    yield (c,s,l)



def pylab_pretty_plot(lines=2,width=3,size=4,labelsize=16,markersize=10,fontsize=20,lfontsize=16,lframeon=False,usetex=True):
    """
    Changes pylab plot defaults to get nicer plots - frame size, marker size, etc.

    Parameters:
    ------------
    lines      : linewidth
    width      : width of framelines and tickmarks
    size       : tick mark length
    labelsize  : font size of ticklabels
    markersize : size of plotting markers
    fontsize   : size of font for axes labels
    lfontsize  : legend fontsize
    usetex     : use latex for labels/text?

    """
    pylab.rc("lines",linewidth=lines)
    pylab.rc("lines",markeredgewidth=size/3)
    pylab.rc("lines",markersize=markersize)
    pylab.rc("ytick",labelsize=labelsize)
    pylab.rc("ytick.major",pad=size)
    pylab.rc("ytick.minor",pad=size)
    pylab.rc("ytick.major",size=size*1.8)
    pylab.rc("ytick.minor",size=size)
    pylab.rc("xtick",labelsize=labelsize)
    pylab.rc("xtick.major",pad=size)
    pylab.rc("xtick.minor",pad=size)
    pylab.rc("xtick.major",size=size*1.8)
    pylab.rc("xtick.minor",size=size)
    pylab.rc("axes",linewidth=width)
    pylab.rc("text",usetex=usetex)
    pylab.rc("font",size=fontsize)
    pylab.rc("legend",fontsize=lfontsize)
    pylab.rc("legend",frameon=lframeon)


def plot_pylab_colormaps():
    """
    Makes a plot of all the pylab colormaps; useful for picking colormaps.
    Returns a figure to either save or show.
    """
    # get list of colormaps
    cmap_list = pylab.cm._cmapnames
    nrows = len(cmap_list)
    # set up a massive array of subplots
    gradient = vstack((linspace(0,1,256),linspace(0,1,256)))
    fig,axes = pylab.subplots(nrows=nrows)
    fig.subplots_adjust(top=0.95,bottom=0.01,left=0.2,right=0.99,wspace=1.0)
    # fill in the subplots
    for ax,name in zip(axes,cmap_list):
        ax.imshow(gradient,aspect='auto',cmap=getattr(pylab.cm,name))
        pos = list(ax.get_position().bounds)
        x_text = pos[0] - 0.01
        y_text = pos[1] + pos[3]/2
        fig.text(x_text,y_text,name,va='center',ha='right',fontsize=8)
    # turn off all the ticks on all the axes
    for ax in axes:
        ax.set_axis_off()
    # return the figure
    return fig


def plot_hist(x,nbins=None,kde=False,color='k',ax=None):
    """
    Plots a histogram (bar plot) of the data in x, with an optional kernel
    density estimate added.  Returns the axes object.

    Parameters:
    -------------
    x         : array-like, required
                    data to plot
    nbins     : integer, optional
                    if None, defaults to 1 + ceil(log2(len(x)))
    kde       : boolean, optional
                    set to True to overlay a kernel density estimate of x
    color     : string, optional
                    color for the bars and optional kde
    ax        : pylab axes object, optional
                    use to pass in a custom set of axes
    """
    if nbins is None:
        nbins = 1 + ceil(log2(len(x)))

    if ax is None:
        ax = pylab.axes(frameon=False)

    # compute bin counts
    counts,bin_edges = histogram(x,bins=nbins,density=True)
    bin_edges = bin_edges[0:-1]
    barwidth = 0.9*(bin_edges[1] - bin_edges[0])

    # bar plot
    ax.bar(bin_edges,counts,color=color,width=barwidth,alpha=0.5)
    lpoint = min(x) - 0.025*abs(min(x))
    rpoint = max(x) - 0.025*abs(max(x))

    # kde if desired
    if kde is True:
        kde = gaussian_kde(x)
        support = linspace(lpoint,rpoint,256)
        mPDF = kde(support)
        ax.plot(support,mPDF,color=color,lw=3)

    # pretty things up
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().set_visible(False)
    ax.set_xlim([lpoint,rpoint])
    ax.set_ylim(bottom=-0.01)

    return ax


def plot_points_plus_kde(xlist,labels,markx=False,lines=3,size=9,ax=None):
    """
    Accepts a list of one-dimensional densities and plots each as points on a line
    with a KDE on top.

    Parameters:
    -------------
    xlist : list of array-like objects
            data to produce density plot for

    labels : list of legend labels; len(labels) should equal len(xlist)

    markx : bool, optional
            put tick labels at the min/max values in x?

    lines : integer, optional
            line/marker edge thickness

    size  : integer, optional
            marker size

    color : string, optional
            color for points and kde

    ax    : pylab axes object, optional
    """
    if ax is None:
        ax = pylab.axes(frameon=False)

    # cycles through colors
    cw = color_wheel(lines=('-'),symbols=('o'))

    for i in xrange(0,len(xlist)):
        # spin the color wheel
        (c,s,l) = cw.next()

        # make the point plot
        ax.plot(xlist[i],zeros(xlist[i].shape),c+s,markersize=size,mew=lines,alpha=0.5)

        # kde
        kde = gaussian_kde(xlist[i])
        lpoint = min(xlist[i]) - 0.025*abs(min(xlist[i]))
        rpoint = max(xlist[i]) + 0.025*abs(max(xlist[i]))
        support = linspace(lpoint,rpoint,512)
        mPDF = kde(support)
        ax.plot(support,mPDF,color=c,lw=lines,label=labels[i])

    # prtty things up
    ax.get_yaxis().set_visible(False)
    ax.set_ylim(bottom=-0.1)
    if markx:
        major_formatter = pylab.FormatStrFormatter('%1.2f')
        ax.get_xaxis().set_major_formatter(major_formatter)
        ax.get_xaxis().tick_bottom()
        minx = min([min(x) for x in xlist])
        maxx = max([max(x) for x in xlist])
        ax.get_xaxis().set_ticks([minx,maxx])
    else:
        ax.get_xaxis().set_ticks([])
    # legend
    ax.legend(loc='best')

    return ax


def plot_scatter_plus_marginals(x,y,sColor='k',xColor='k',yColor='k',xlim=None,ylim=None):
    """
    Makes a scatter plot of 2D data along with marginal densities in each coordinate, drawn
    using kernel density estimates.

    Parameters:
    -------------
    x      : 1D array-like object
    y      : 1D array-like object
    sColor : string, optional
             color for scatterplot points
    xColor : string, optional
             color for KDE(x)
    yColor : string, optional
             color for KDE(y)
    xlim   : list, optional
             x limits for plot; computed from x if none provided
    ylim   : list, optional
             y limits for plot; computed from y if None
    """
    # axis formatter
    def my_formatter(x,pos):
        return '%2.2f'%x
    # kde/limits
    kdepoints = 512
    inflation = 0.25

    # compute axis limits if not provided
    if xlim is None:
        xlim = [0,0]
        xlim[0] = min(x) - inflation*abs(min(x))
        xlim[1] = max(x) + inflation*abs(max(x))
    if ylim is None:
        ylim = [0,0]
        ylim[0] = min(y) - inflation*abs(min(y))
        ylim[1] = max(y) + inflation*abs(max(y))

    # plot and axis locations
    left, width = 0.1,0.65
    bottom,height = 0.1,0.65
    bottom_h = left_h = left + width + 0.05
    mainCoords = [left,bottom,width,height]
    xHistCoords = [left,bottom_h,width,0.2]
    yHistCoords = [left_h,bottom,0.2,height]
    f = pylab.figure(1,figsize=(8,8))

    # scatter plot
    axMain = pylab.axes(mainCoords,frameon=False)
    axMain.scatter(x,y,c=sColor,marker='o',alpha=0.5)
    axMain.set_xlim(xlim)
    axMain.set_ylim(ylim)
    axMain.get_xaxis().set_visible(False)
    axMain.get_yaxis().set_visible(False)

    # x histogram
    axxHist = pylab.axes(xHistCoords,frameon=False)
    axxHist.get_yaxis().set_visible(False)
    kdex = gaussian_kde(x)
    xsupport = linspace(xlim[0],xlim[1],kdepoints)
    mPDF = kdex(xsupport)
    axxHist.plot(xsupport,mPDF,xColor,lw=3)
    # add axis line, clean up
    axxHist.plot(xlim,[0,0],'k-',lw=3)
    axxHist.set_xlim(xlim)
    axxHist.set_xticks(xlim)
    axxHist.tick_params(axis='x',direction='in',top=False)
    axxHist.xaxis.set_major_formatter(FuncFormatter(my_formatter))
    axxHist.set_yticks([])

    # y histogram
    axyHist = pylab.axes(yHistCoords,frameon=False)
    axyHist.get_xaxis().set_visible(False)
    kdey = gaussian_kde(y)
    ysupport = linspace(ylim[0],ylim[1],kdepoints)
    mPDF = kdey(ysupport)
    axyHist.plot(mPDF,ysupport,yColor,lw=3)
    # add axis line, clean up
    axyHist.plot([0,0],ylim,'k-',lw=3)
    axyHist.set_ylim(ylim)
    axyHist.set_yticks(ylim)
    axyHist.tick_params(axis='y',direction='in',right=False)
    axyHist.yaxis.set_major_formatter(FuncFormatter(my_formatter))
    axyHist.set_xticks([])

    return axMain

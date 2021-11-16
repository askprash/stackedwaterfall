import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb, to_hex
import pandas as pd
import functools
import itertools

class StackedWaterfalls():
    
    def __init__(self, data, datalabels = [], datacolors = [], barlst = []):
        
        self.rawdata = data
        self.nbars = len(data)
        self.maxlevs  = max([len(stack) for stack in self.rawdata]) #gives the max number of stack levels
        self.levnames = ['Level{0}'.format(x+1) for x in range(self.maxlevs)] #Assign temporary level names
        
        self.datalabels = datalabels
        
        
        self.colors = datacolors
        
        self.barlst = barlst
        self.namelst = []
        
        
    def prep_data(self):
        #Arrange data values

        self.df = pd.DataFrame(self.rawdata, columns = self.levnames).fillna(0)    
        #Prep data by adding additional columns
        self.df['Total']  = self.df.sum(axis=1)
        self.df['CumSum'] = self.df['Total'].cumsum()
        self.df['Bottom'] = self.df['CumSum'].shift(1).fillna(0)
        return self.df
    
    def arrange_labels(self):
        if self.datalabels:
            #Arrange names
            self.dfnames = pd.DataFrame(self.datalabels, columns = self.levnames).fillna(0)
        else:
            self.dfnames = pd.DataFrame(self.rawdata, columns = self.levnames).fillna(0)
            
        return self.dfnames
    
    def arrange_colors(self):
        if self.colors:
            self.dfcolors = pd.DataFrame(self.colors, columns = self.levnames).fillna('None')
            
    
    def stdcolors(self):
        n = len([x for x in list(itertools.chain(*self.rawdata))])
        phi = 0.618033988749895 #irrational number to use per equidistribution theorem, 
        # and supposedly the golden ratio is the best acc. to Fibonacci hashing.
        
        colors = [to_hex(hsv_to_rgb([(i * phi) % 1.0,0.7, np.sqrt(1.0 - (i*phi)%0.5)]))
                  for i in range(n)]
        return colors
            
    def plot(self, ax=None, xstart = 0, total=True, edgecolor = None, barwidth = 0.2, gap = 0.2,
             plotlinks = True,  totalcolor = 'dimgrey', shadecolor = 'None'):
        
        self.barwidth = barwidth
        self.gap = gap
        
        if ax is None:
            fig, ax = plt.subplots(dpi = 100, figsize = (8,5))
            
        if edgecolor is None:
            ecolor = totalcolor
        else:
            ecolor = edgecolor  

        if total:
            xtotal = xstart
            totalval = self.df['Total'].sum()
            self.barlst.append(ax.bar(x = xtotal, height = totalval,
                                 width = barwidth, color = totalcolor, edgecolor = ecolor,
                                      linewidth = 0.5, zorder = 10))
            self.namelst.append(["Total"])
            xstart = xstart+barwidth+gap #offset start to accomodate total bar
        
        xlocs = np.linspace(xstart, xstart+(self.nbars-1)*(barwidth+gap), self.nbars)
        
        cindexstart = 0
        prev_lev = [0]*self.nbars
        for lev in self.levnames:
            if self.colors:
                colors = self.dfcolors[lev].values
            else:
                colorlst = self.stdcolors() # Get unique colors that are spread across hue and brightness
                colors = colorlst[cindexstart : cindexstart + np.count_nonzero(self.df[lev])]
                cindexstart = cindexstart + np.count_nonzero(self.df[lev])

            if edgecolor is None:
                ecolor = colors
            else:
                ecolor = edgecolor    
            self.barlst.append(ax.bar(x = xlocs, height = self.df[lev], bottom = self.df['Bottom']+prev_lev,
                                 width = barwidth,color = colors , edgecolor = ecolor, linewidth = 0.5, zorder = 10))
            self.namelst.append(self.dfnames[lev].tolist())
            prev_lev = prev_lev + self.df[lev]
        
        if plotlinks:
            link_lines = self.df['CumSum'].repeat(3).shift(2)
            link_lines[1:-1:3] = np.nan
            link_lines = link_lines[1:-1]
            xs = [y + barwidth/2 if x%2==0 else y-barwidth/2 for (x,y) in zip(itertools.count(),(xlocs.repeat(3)[1:-1]))]

            ax.plot(xs, link_lines, lw = 0.5, ls = '--', color = 'k', zorder = 1)
            
        xshadestart = xlocs[0] - gap
        xshadeend   = xlocs[-1] + gap
        
        if total:
            ax.plot([xtotal, xlocs[-1]], [totalval, totalval], lw = 0.5, ls = '--', color = 'k', zorder = 1)
            xshadestart = xtotal - gap

        shade = ax.axvspan(xshadestart, xshadeend, facecolor = shadecolor, alpha = 0.1, zorder = 0)
            
        return ax
    

        

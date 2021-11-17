import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb, to_hex
import pandas as pd
import functools
import itertools

class StackedWaterfalls():
    
    def __init__(self, data, datalabels = [], datacolors = []):
        
        self.rawdata = data
        self.nbars = len(data)
        self.maxlevs  = max([len(stack) for stack in self.rawdata]) #gives the max number of stack levels
        self.levnames = ['Level{0}'.format(x+1) for x in range(self.maxlevs)] #Assign temporary level names
        
        self.datalabels = datalabels
        
        
        self.colors = datacolors
        
        self.barlst = []
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
        phi = 0.618033988749895         
        colors = [to_hex(hsv_to_rgb([(i * phi) % 1.0,0.7, np.sqrt(1.0 - (i*phi)%0.5)]))
                  for i in range(n)]
        return colors
            
    def plot(self, ax=None, xstart = 0, total=False, edgecolor = None, barwidth = 0.2, gap = 0.2, barkw={},
             plotlinks = True, linkskw={},  totalcolor = 'dimgrey', shadecolor = 'None', dropax = 0, legend = True, legkw={},
             grouplabel = None, grouplabelstyle = "|", grouplabelkw={}, barnames=[]):
        
        
        self.barwidth = barwidth
        self.gap = gap
        self.total = total
        self.barlst = []
        self.namelst = []
        
        self.prep_data()
        self.arrange_labels()
        self.arrange_colors()
        
        if ax is None:
            fig, ax = plt.subplots(dpi = 100, figsize = (8,5))
        self.ax = ax   
        if edgecolor is None:
            ecolor = totalcolor
        else:
            ecolor = edgecolor  

        if total:
            xtotal = xstart
            self.xtotal = xtotal
            totalval = self.df['Total'].sum()
            self.barlst.append(ax.bar(x = xtotal, height = totalval,
                                 width = barwidth, color = totalcolor, edgecolor = ecolor,
                                      linewidth = 0.5, zorder = 10))
            self.namelst.append(["Total"])
            xstart = xstart+barwidth+gap #offset start to accomodate total bar
        
        xlocs = np.linspace(xstart, xstart+(self.nbars-1)*(barwidth+gap), self.nbars)
        self.xlocs = xlocs
        
        cindexstart = 0
#         barkw['linewidth']=barkw.get('linewidth',0.5)
        
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
                
#             barkw['edgecolor']=barkw.get('edgecolor',ecolor)
            self.barlst.append(ax.bar(x = xlocs, height = self.df[lev], bottom = self.df['Bottom']+prev_lev,
                                 width = barwidth,color = colors , edgecolor = ecolor, linewidth = 0.5, zorder = 10, **barkw))
            self.namelst.append(self.dfnames[lev].tolist())
            prev_lev = prev_lev + self.df[lev]
        
        if plotlinks:
            link_lines = self.df['CumSum'].repeat(3).shift(2)
            link_lines[1:-1:3] = np.nan
            link_lines = link_lines[1:-1]
            xs = [y + barwidth/2 if x%2==0 else y-barwidth/2 for (x,y) in zip(itertools.count(),(xlocs.repeat(3)[1:-1]))]
            linkskw['color'] = linkskw.get('color', 'k')
            linkskw['ls']    = linkskw.get('ls', '--')
            linkskw['lw']    = linkskw.get('lw', '0.5')
            ax.plot(xs, link_lines, **linkskw, zorder = 1)
            
        xshadestart = xlocs[0] - gap
        xshadeend   = xlocs[-1] + gap
        
        if total:
            ax.plot([xtotal, xlocs[-1]], [totalval, totalval], **linkskw, zorder = 1)
            xshadestart = xtotal - gap

        shade = ax.axvspan(xshadestart, xshadeend, facecolor = shadecolor, alpha = 0.1, zorder = 0)
        
#         ax.set_xticks([])
        self.xaxlabeler(ax, grouplabel, barnames, grouplabelstyle)
               
        if legend:
            self.legendcreator(ax, legkw)

        return ax, xlocs[-1]
    
    def legendcreator(self, ax, legkw):
        rects = [x for x in list(itertools.chain(*self.barlst)) if x.get_height() != 0] # get only those rects that are non-zero heights
        labels = [x for x in list(itertools.chain(*self.namelst)) if x != 0]

        l = ax.legend(rects, labels, **legkw)
        l.set_zorder(30)
 
    
    def xaxlabeler(self, ax, grouplabel, barnames, grouplabelstyle):
        
        fs = ax.xaxis.label.get_size()
        # Set these in axes coords
        bracketheight = 0.015
        bracketoffset = 0.02
        transx = ax.get_xaxis_transform()
        
        xstart = self.xtotal if self.total else self.xlocs[0]
        xmid = (xstart + self.xlocs[-1])/2.0
        
        if barnames:
            if self.total:
                ax.set_xticks([self.xtotal] + list(self.xlocs))
                ax.set_xticklabels(["Total"]+barnames)
                
            else:
                ax.set_xticks(self.xlocs)
                ax.set_xticklabels(barnames)
                
                
            # Offset group labels by appropriate amount
            plt.tight_layout() # need this to get fig rendered. Should be a better way perhaps
            # get lower y lim
            yminlabel = max([abs(x.get_window_extent().transformed(transx.inverted()).y0) for x in ax.get_xticklabels()])
            bracketoffset = bracketoffset + yminlabel
        
        if grouplabel is not None:
            ygrplabel = 0
            
            # Group label styles:
            # |, ], ]-, |-
            if grouplabelstyle is not None:
                # endpt = datapt -+ gap +- offset
                xlineA = xstart  - self.gap + self.gap/5 #Start of label line
                xlineB = self.xlocs[-1] + self.gap - self.gap/5 #End of label line

                # Use get_xaxis_transform() so that x coords are in data coords and y are in axes coords
                ax.plot([xlineA, xlineB], [-bracketoffset,  -bracketoffset ], 
                        transform = transx, color = 'k', clip_on=False, lw = 0.8)
                ygrplabel = -bracketoffset-0.02

            if (grouplabelstyle == ']') or (grouplabelstyle == ']-'):
                ax.plot([xlineA, xlineA, np.nan, xlineB, xlineB],
                        [-bracketoffset, -bracketoffset+bracketheight, np.nan, 
                         -bracketoffset, -bracketoffset+bracketheight],
                       transform = transx, color = 'k', clip_on=False, lw = 0.8)
                ygrplabel = -bracketoffset-0.02

            if (grouplabelstyle == ']-') or (grouplabelstyle == '|-'):

                ax.plot([xmid, xmid],[-bracketoffset, -bracketoffset-bracketheight],
                       transform = transx, color = 'k', clip_on=False, lw = 0.8)
                ygrplabel = -bracketoffset-2*bracketheight


            ax.annotate(grouplabel, xy=(xmid, ygrplabel), xycoords = transx, 
                    ha='center', va='top', fontsize = fs,
                    bbox=dict(boxstyle='square', fc='None',ec = 'None'))
        

    

        

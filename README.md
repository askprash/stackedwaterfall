# Stacked Waterfalls

Simple utility to plot stacked waterfalls using `matplotlib`

Drew inspiration from [`waterfall_ax`](https://github.com/microsoft/waterfall_ax)

## Installation

```
pip install stackedwaterfalls
```

`stackedwaterfalls` expects a list of list, where each sublist represents a bar, and it's elements represent stacks within that bar.
Here's a simple example:
```python
from stackedwaterfalls import StackedWaterfalls as sw

aircomp  =  [[0.74] , [0.16], [0.05, 0.05]]
names = [['N$_2$'], ['O$_2$'], ['AR','H$_2$O']] # Labels of input values

air = sw(aircomp, names)
air.plot()
```

## Examples on group labels

## Examples on insets


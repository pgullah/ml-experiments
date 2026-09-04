import matplotlib.pyplot as plt
import numpy as np


def plot_sin():
    x = np.linspace(0, 10, 100)
    plt.plot(x, np.sin(x))
    plt.show()

def plot_sinV1():
    x = np.linspace(0, 10, 100)
    plt.plot(x, np.sin(x))
    
    plt.xlim([2, 8])
    plt.ylim([0, 0.75])

    plt.xlabel('x-axis')
    plt.ylabel('y-axis')

    plt.show()
    
def plot_sinV2():
    x = np.linspace(0, 10, 100)
    plt.plot(x, np.sin(x), 
             label=('sin(x)'), 
             linestyle='', 
             marker='o'
    )

    plt.ylabel('f(x)')
    plt.xlabel('x')

    plt.legend(loc='lower left')
    plt.show()


def plot_scatter():
    rng = np.random.RandomState(123)
    x = rng.normal(size=500)
    y = rng.normal(size=500)


    plt.scatter(x, y)
    plt.show()
    
def plot_barchart():
    means = [5, 8, 10]
    stddevs = [0.2, 0.4, 0.5]
    bar_labels = ['bar 1', 'bar 2', 'bar 3']

    # plot bars
    x_pos = list(range(len(bar_labels)))
    plt.bar(x_pos, means, yerr=stddevs)

    plt.show()
    

def plot_histogram():
    rng = np.random.RandomState(123)
    x = rng.normal(0, 20, 1000) 

    # fixed bin size
    bins = np.arange(-100, 100, 5) # fixed bin size

    plt.hist(x, bins=bins)
    plt.show()
    
def plot_multi_histogram():
    rng = np.random.RandomState(123)
    x1 = rng.normal(0, 20, 1000) 
    x2 = rng.normal(15, 10, 1000)

    # fixed bin size
    bins = np.arange(-100, 100, 5) # fixed bin size

    plt.hist(x1, bins=bins, 
             alpha=0.5
             )
    plt.hist(x2, bins=bins, 
             alpha=0.5
             )
    plt.show()
    

def plot_subplots():
    x = range(11)
    y = range(11)

    _, ax = plt.subplots(nrows=2, ncols=3,
                        sharex=True, sharey=True)

    for row in ax:
        for col in row:
            col.plot(x, y)
            
    plt.show()
    
def plot_color_markers():
    x = np.linspace(0, 10, 100)
    plt.plot(x, np.sin(x),
            color='blue',
            marker='^',
            linestyle='')
    plt.show()

if __name__ == "__main__":
    # plot_sin()
    # plot_sinV1()
    # plot_sinV2()
    # plot_scatter()
    # plot_barchart()
    # plot_histogram()
    # plot_multi_histogram()
    plot_subplots()
    plot_color_markers()
import os
import subprocess
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import glob
import numpy as np
import math

def create_bash_script(num, edr_file, option):
    script_content = f'''#!/bin/bash
    printf "{option}\\n0\\n" | gmx energy -f {edr_file} -o {option}.xvg
    '''
    with open(f'bash{num}.sh', 'w') as file:
        file.write(script_content)

    os.chmod(f'bash{num}.sh', 0o755)  # set execute permissions

def run_bash_script(num):
    subprocess.run([f'./bash{num}.sh'])

def read_and_plot_xvg(file, ax):
    with open(file, 'r') as f:
        lines = f.readlines()
        start_line = 0
        for line in lines:
            if line[0] != '#' and line[0] != '@':
                break
            start_line += 1

    data = pd.read_csv(file, skiprows=start_line, delim_whitespace=True, header=None)
    ax.plot(data[0], data[1])

    x_label = None
    y_label = None
    for i in range(start_line - 1, -1, -1):
        if 'xaxis' in lines[i]:
            x_label = lines[i].split('"')[1]
        elif 'yaxis' in lines[i]:
            y_label = lines[i].split('"')[1]
        if x_label and y_label:
            break

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

def animate(i):
    for i, (ax, option) in enumerate(zip(axs, plot_numbers), 1):
        ax.clear()
        run_bash_script(i)
        read_and_plot_xvg(f'{option}.xvg', ax)

def remove_bash_scripts():
    for file in glob.glob("bash*.sh"):
        os.remove(file)
        

def remove_xvg_files():
    for file in glob.glob("#*.xvg.*#"):
        os.remove(file)

def main():
    
    global axs, plot_numbers
    num_plots = int(input("How many plots do you want to see? "))
    edr_file = input("Please provide the name of the .edr file: ")
    plot_numbers = input("Enter plot numbers (separated by space): ").split()

    dim = math.ceil(math.sqrt(num_plots))
    fig, axs = plt.subplots(dim, dim, figsize=(8*dim, 6*dim))

    # reshape axs to 1-D array
    axs = axs.flatten()

    # then remove extra subplots
    for i in range(num_plots, dim*dim):
        fig.delaxes(axs[i])

    for i, option in enumerate(plot_numbers, 1):
        create_bash_script(i, edr_file, option)

    ani = animation.FuncAnimation(fig, animate, interval=15000)

    plt.tight_layout()
    plt.show()

    remove_bash_scripts()
    remove_xvg_files()

if __name__ == "__main__":
    main()


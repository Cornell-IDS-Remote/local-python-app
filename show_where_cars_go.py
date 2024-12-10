import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Load the processed CSV files for lines and arcs
lines_df = pd.read_csv('Processed_Lines.csv')
arcs_df = pd.read_csv('Processed_Arcs.csv')

def calculate_endpoint(row):
    if row['direction'] == '+X':
        return row['x'] - row['length'], row['y']
    elif row['direction'] == '-X':
        return row['x'] + row['length'], row['y']
    elif row['direction'] == '+Y':
        return row['x'], row['y'] - row['length']
    elif row['direction'] == '-Y':
        return row['x'], row['y'] + row['length']

def plot_line(row, color, plot, width=1):
    x_start, y_start = row['x'], row['y']
    x_end, y_end = calculate_endpoint(row)
    line, = plot.plot([-x_start, -x_end], [-y_start, -y_end], color=color, linewidth=width)
    return line

def plot_arc(row, color, plot, width=1):
    theta = np.linspace(row['angleStart'], row['angleEnd'], 100)
    if row['Rotation'] == 'CW':
        theta = np.flip(theta)
    x_arc = row['x'] + row['radius'] * np.cos(theta)
    y_arc = row['y'] + row['radius'] * np.sin(theta)
    arc, = plot.plot(-x_arc, -y_arc, color=color, linewidth=width)
    return arc


def plot_all(plot):
    for _, row in lines_df.iterrows():
        plot_line(row,'black',plot)
    
    # Plot arcs
    for _, row in arcs_df.iterrows():
        plot_arc(row,'black',plot)
    
    plt.xlabel('X')
    plt.ylabel('Y')

    plt.title('Interactive Plot of Lines and Arcs')
    plt.grid(True)


def highlight_segments(segment_list,plot):
    unique_colors = plt.cm.get_cmap('tab10', len(segment_list))  # Generate a colormap
    legend_elements = []

    for i, segment in enumerate(segment_list):
        color = unique_colors(i)
        if segment in lines_df['index'].values:
            row = lines_df[lines_df['index'] == segment].iloc[0]
            line = plot_line(row, color, plot,3)
            legend_elements.append(line)
        elif segment in arcs_df['index'].values:
            row = arcs_df[arcs_df['index'] == segment].iloc[0]
            arc = plot_arc(row, color, plot,3)
            legend_elements.append(arc)
        else:
            print(f"Segment {segment} not found in data.")

    plot.legend(legend_elements, [f"Vehicle{i} ~ {segment_list[i]}" for i in range(len(segment_list))])
    plot.grid(True)

def show(plot,segments_to_highlight):
    plot_all(plot)
    highlight_segments(segments_to_highlight,plot)



#%%
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import math
# # Define your categories and colors
# labels = ['Residential', 'Commercial', 'Industrial', 'Transport', 'Own-use', 'Power', 'Other']
# colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']  # Match your color palette

# # Create legend handles
# handles = [Patch(facecolor=color, edgecolor='none', label=label) for label, color in zip(labels, colors)]

# # Create a standalone legend
# fig, ax = plt.subplots(figsize=(6, 1))  # Adjust size as needed
# ax.axis('off')  # No axes

# def calculate_space(num_boxes, font_size, box_size, padding):

#     total_width = (num_boxes * box_size) + ((num_boxes - 1) * padding)
#     return total_width

# #create method that identifies the number of boxes and letters and calcultes the spacethat will take up given the font size , box size and paddings

# # Customize the legend
# # legend = ax.legend(
# #     handles=handles,
# #     loc='center',
# #     frameon=False,
# #     ncol=4,  # Number of columns
# #     fontsize=8,  # Control text size
# #     handlelength=0.7,  # Length of color boxes
# #     handleheight=0.7,  # Height of boxes (may need tweaking)
# #     borderpad=0,  # Padding inside the legend
# #     columnspacing=0.3  # Space between columns
    
# # )

# legend = ax.legend(
#     handles=handles,
#     loc='center',
#     bbox_to_anchor=(0.5, 0.5),  # manually position if needed
#     ncol=4,
#     fontsize=8,
#     frameon=True,
#     facecolor='none',
#     edgecolor='none',
#     framealpha=1,
#     fancybox=True,
#     shadow=False,
#     borderpad=0,
#     labelspacing=0,
#     handlelength=1,
#     handleheight=1,
#     handletextpad=0.1,
#     columnspacing=0.3,
#     borderaxespad=0,
#     title="",
#     title_fontsize=10,
#     alignment='center'
# )


# %%


# def compute_optimal_ncol(labels, fontsize=9, max_width_px=500,
#                          box_length_px=15, handletextpad_px=5, columnspacing_px=10):
#     char_width_px = fontsize * 0.6  # average width per character
#     label_widths = []

#     for label in labels:
#         text_width = len(label) * char_width_px
#         total = box_length_px + handletextpad_px + text_width + columnspacing_px
#         label_widths.append(total)

#     # Now simulate placing labels in a row until width is exceeded
#     best_ncol = len(labels)
#     for trial_ncol in range(1, len(labels) + 1):
#         rows = (len(labels) + trial_ncol - 1) // trial_ncol  # ceiling division
#         max_row_width = 0
#         for r in range(rows):
#             row_width = sum(label_widths[i] for i in range(r * trial_ncol, min((r + 1) * trial_ncol, len(labels))))
#             max_row_width = max(max_row_width, row_width)
#         if max_row_width >= max_width_px:
#             breakpoint()
#             best_ncol = trial_ncol
#             break

#     return best_ncol

#%%
# # Define your categories and colors
# labels =['Biomass']#, 'Coal', 'Gas', 'Geothermal', 'Heat', 'Hydrogen', 'Oil', 'Electricity', 'Other renewables', 'Total', 'Others','Biomass', 'Coal', 'Gas', 'Geothermal', 'Heat', 'Hydrogen', 'Oil', 'Electricity', 'Other renewables', 'Total', 'Others']
# colors = ['#1CA05A']#, '#0D0D0D', '#000099', '#7030A0', '#CC0049', '#F67AA3', '#007370', '#00B9CC', '#ABD7F5', '#323232', '#2b3b5e','#1CA05A', '#0D0D0D', '#000099', '#7030A0', '#CC0049', '#F67AA3', '#007370', '#00B9CC', '#ABD7F5', '#323232', '#2b3b5e']
# FONTSIZE = 15
# # Create legend handles
# handles = [Patch(facecolor=color, edgecolor='none', label=label) for label, color in zip(labels, colors)]

# # Create a standalone legend
# width_inches = 10
# height_inches = 0.7
# dpi=300
# width_pixels = width_inches * dpi
# height_pixels = height_inches * dpi
# fig, ax = plt.subplots(figsize=(width_inches, height_inches), dpi=dpi)
# ax.axis('off')  # No axes

# # Dynamically calculate optimal number of columns
# ncol = compute_optimal_ncol(labels, fontsize=FONTSIZE, max_width_px=width_pixels)

# legend = ax.legend(
#     handles=handles,
#     loc='upper left',
#     bbox_to_anchor=(0,1),
#     ncol=ncol,  # ← now using dynamic value!
#     fontsize=FONTSIZE,
#     frameon=True,
#     facecolor='none',
#     edgecolor='none',
#     framealpha=1,
#     fancybox=True,
#     shadow=False,
#     borderpad=0,
#     labelspacing=0,
#     handlelength=1,
#     handleheight=1,
#     handletextpad=0.2,
#     columnspacing=0.3,
#     borderaxespad=0,
#     title="",
#     title_fontsize=10,
#     alignment='center'
# )

# plt.tight_layout()
# # plt.show()

# plt.savefig('../output/plotting_output/legend.png')#, bbox_inches='tight')  
# plt.close()  
# %%



labels =['Biomass', 'Coal', 'Gas', 'Geothermal', 'Heat', 'Hydrogen', 'Oil', 'Electricity', 'Other renewables', 'Total']#, 'Others','Biomass', 'Coal', 'Gas', 'Geothermal', 'Heat', 'Hydrogen', 'Oil', 'Electricity', 'Other renewables', 'Total', 'Others']
colors = ['#1CA05A', '#0D0D0D', '#000099', '#7030A0', '#CC0049', '#F67AA3', '#007370', '#00B9CC', '#ABD7F5', '#323232']#, '#2b3b5e','#1CA05A', '#0D0D0D', '#000099', '#7030A0', '#CC0049', '#F67AA3', '#007370', '#00B9CC', '#ABD7F5', '#323232', '#2b3b5e']

labels =['Biomass', 'Coal', 'Gas', 'Geothermal', 'Heat', 'Hydrogen', 'Oil', 'Electricity', 'Other renewables', 'Total', 'Others','Biomass', 'Coal', 'Gas', 'Geothermal', 'Heat']#, 'Hydrogen', 'Oil', 'Electricity', 'Other renewables', 'Total', 'Others']
colors = ['#1CA05A', '#0D0D0D', '#000099', '#7030A0', '#CC0049', '#F67AA3', '#007370', '#00B9CC', '#ABD7F5', '#323232', '#2b3b5e','#1CA05A', '#0D0D0D', '#000099', '#7030A0']#, '#CC0049', '#F67AA3', '#007370', '#00B9CC', '#ABD7F5', '#323232', '#2b3b5e']

def compute_optimal_ncol(
    labels,
    fontsize=9,
    fig_width_inches=10,
    dpi=300,
    left_margin=0,
    right_margin=0,
    handlelength=1.0,        # Matplotlib legend default (in font units)
    handletextpad=0.2,       # space between box and text (also in font units)
    columnspacing=0.3,       # space between columns (in font units)
    max_rows=4,
    char_width_multiplier = 3.5
):
    # Convert figure width to usable width in pixels
    total_width_px = fig_width_inches * dpi
    usable_width_px = total_width_px * (1 - left_margin - right_margin)

    # Convert font-relative units into pixels
    char_width_px = fontsize * char_width_multiplier
    handlelength_px = handlelength * fontsize
    handletextpad_px = handletextpad * fontsize
    columnspacing_px = columnspacing * fontsize

    label_widths = []
    for label in labels:
        text_width = len(label) * char_width_px
        total_width = handlelength_px + handletextpad_px + text_width + columnspacing_px
        label_widths.append(total_width)

    total_labels = len(labels)
    
    # Try all possible column layouts
    for trial_ncol in range(total_labels, 0, -1):
        rows = (total_labels + trial_ncol - 1) // trial_ncol
        if rows > max_rows:
            continue
        
        fits = True
        for r in range(rows):
            row_labels = label_widths[r * trial_ncol : min((r + 1) * trial_ncol, total_labels)]
            row_width = sum(row_labels)
            if row_width > usable_width_px:
                fits = False
                break

        if fits:
            
            return trial_ncol
    
    raise ValueError(
        f"Legend cannot fit within {max_rows} rows for width={fig_width_inches} inches and fontsize={fontsize}."
    )

def reorder_handles_row_major(handles, ncol):
    """
    Given a list of legend handles and a desired number of columns (ncol),
    reorder the handles so that when Matplotlib arranges them (columnwise by default)
    the visual order is row-major (i.e., items are read left-to-right, top-to-bottom).
    
    Parameters:
        handles (list): The list of legend handle objects in natural (row-major) order.
        ncol (int): The number of columns for the legend.
        
    Returns:
        list: A new list of handles reordered for row-major display.
    """
    n = len(handles)
    nrow = int(math.ceil(n / ncol))
    
    # Create a grid (list of rows) in row-major order.
    grid = [handles[i * ncol : (i + 1) * ncol] for i in range(nrow)]
    
    # Pad the last row if needed so every row has ncol elements.
    if len(grid[-1]) < ncol:
        grid[-1].extend([None] * (ncol - len(grid[-1])))
    
    # Now transpose the grid.
    new_handles = []
    for col in range(ncol):
        for row in range(nrow):
            item = grid[row][col]
            if item is not None:
                new_handles.append(item)
                
    return new_handles

FONTSIZE = 15
# Create legend handles
chart_type_to_label_type_dict = {
    'percentage_bar': 'box',
    'line': 'line',
    'bar': 'box',
    'scatter': 'dot',
    'area': 'box',
    'combined_line_bar': 'box'
}
handles = [Patch(facecolor=color, edgecolor='none', label=label) for label, color in zip(labels, colors)]
        
width_inches = 10
height_inches = 0.7
dpi=300
width_pixels = width_inches * dpi
height_pixels = height_inches * dpi
fig, ax = plt.subplots(figsize=(width_inches, height_inches), dpi=dpi)   # Adjust of actual image so the user doent need to crop it. 
ax.axis('off')  # No axes

# Force axes to fill the figure:
ax.set_position([0, 0, 1, 1])
fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
# if len(handles)>=8:
#     breakpoint()
# Dynamically calculate optimal number of columns
ncol = compute_optimal_ncol(
    labels,
    fontsize=FONTSIZE,
    fig_width_inches=width_inches, 
    dpi=dpi,
    handlelength=1,
    handletextpad=0.2,
    columnspacing=0.3,
    char_width_multiplier = 3.5
)
handles_ordered = reorder_handles_row_major(handles, ncol)

legend = ax.legend(
    handles=handles_ordered,
    loc='upper left',
    bbox_to_anchor=(0, 1),
    ncol=ncol,
    fontsize=FONTSIZE,
    frameon=True,
    facecolor='none',
    edgecolor='none',
    framealpha=1,
    fancybox=True,
    shadow=False,
    borderpad=0,
    labelspacing=0,
    handlelength=1,
    handleheight=1,
    handletextpad=0.2,
    columnspacing=0.3,
    borderaxespad=0,
    title="",
    title_fontsize=10,
    alignment='center'
)

# Save with no extra padding:
plt.savefig('legend.png', dpi=dpi, pad_inches=0)
# plt.savefig('legend_figure2.png')
plt.show()
# %%

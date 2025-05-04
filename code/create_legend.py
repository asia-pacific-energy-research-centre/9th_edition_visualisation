import time
import uuid
import pandas as pd
import math
import numpy as np
import ast
import os
import shutil
from utility_functions import *
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import random
from matplotlib.lines import Line2D
import workbook_creation_functions


def create_legend(colours_dict, patterns_dict, plotting_name_column, table, plotting_specifications, chart_positions, worksheet, ECONOMY_ID,total_plotting_names,chart_types, plotting_name_to_chart_type=None):
    
    table_copy = table.copy()
    #check the colors here again, jsut in case since its really tough to spot the error if the colors are wrong:
    colours_dict = workbook_creation_functions.check_plotting_names_in_colours_dict(table_copy, colours_dict, plotting_name_column=plotting_name_column)
    patterns_dict = workbook_creation_functions.check_plotting_names_in_patterns_dict(patterns_dict)
    #identify year cols as those that have 4 digits in them
    year_cols = [col for col in table_copy if re.search(r'\d{4}', str(col))]
    #drop any rows that are all 0s from the table
    table_copy = table_copy[~(table_copy[year_cols] == 0).all(axis=1)]
    #then create legend:
    plotting_names_in_charts_mapping = table_copy[plotting_name_column].unique()
    plotting_names_in_charts_mapping_new = []
    #drop any rows that are all 0s from the table
    colors_dict_in_charts_mapping = {}
    
    for plotting_name in plotting_names_in_charts_mapping:
        if plotting_name in total_plotting_names:
            # breakpoint()
            continue
        colors_dict_in_charts_mapping[plotting_name] = colours_dict.get(plotting_name)
        plotting_names_in_charts_mapping_new.append(plotting_name)
    #now create the legend
    # breakpoint()
    if len(plotting_names_in_charts_mapping_new)==0:
        
        return worksheet
    # Define your categories and colors
    labels = plotting_names_in_charts_mapping_new
    colors = [colours_dict.get(label) for label in labels]
    FONTSIZE = plotting_specifications['LEGEND_FONTSIZE']
    # Create legend handles
    chart_type_to_label_type_dict = {
        'percentage_bar': 'box',
        'line': 'line',
        'bar': 'box',
        'scatter': 'dot',
        'area': 'box',
        'combined_line_bar': 'box'
    }
    handles_list = []
    if plotting_name_to_chart_type == None:
        for chart_type in chart_types:
            try:
                label_type = chart_type_to_label_type_dict[chart_type]
            except KeyError:
                breakpoint()
                raise KeyError(f"Chart type '{chart_type}' not found in chart_type_to_label_type_dict.")        
            handles = []
            for label, color in zip(labels, colors):
                if label_type == 'line':
                    if label =='Net emissions':
                        
                        #make it a dashed line
                        handles.append(Line2D([0], [0], color=color, lw=2, linestyle='--', label=label))
                    else:
                        handles.append(Line2D([0], [0], color=color, lw=2, label=label))
                elif label_type == 'box':  # Default to box for other chart types
                    if label in patterns_dict.keys():
                        pattern = patterns_dict.get(label)
                        if pattern =='wide_downward_diagonal':
                            handles.append(
                                Patch(
                                    facecolor='none',   # no fill
                                    edgecolor=color,    # hatch colour
                                    hatch='\\\\',
                                    label=label
                                )
                            )
                        else:
                            raise NotImplementedError(f"Pattern '{pattern}' is not implemented.")
                    else:
                        handles.append(Patch(facecolor=color, edgecolor='none', label=label))#can we specify if its a line or box based on chart type?
                else:
                    breakpoint()
                    raise NotImplementedError(f"Chart type '{label_type}' is not implemented.")
                
            handles_list.append(handles)
    else:
        #we will have unique handles for each label/color combination as set out in chart type to label mapping
        handles = []
        for label, chart_type in plotting_name_to_chart_type.items():
            if label not in labels:
                continue
            color = colours_dict.get(label)
            label_type = chart_type_to_label_type_dict.get(chart_type)
            if label_type == 'line':
                if label =='Net emissions':
                    # breakpoint()
                    #make it a dashed line
                    handles.append(Line2D([0], [0], color=color, lw=2, linestyle='--', label=label))
                else:
                    handles.append(Line2D([0], [0], color=color, lw=2, label=label))
            elif label_type == 'box':
                if label in patterns_dict.keys():
                    pattern = patterns_dict.get(label)
                    if pattern =='wide_downward_diagonal':
                        handles.append(
                            Patch(
                                facecolor='none',   # no fill
                                edgecolor=color,    # hatch colour
                                hatch='\\\\',
                                label=label
                            )
                        )
                    else:
                        raise NotImplementedError(f"Pattern '{pattern}' is not implemented.")
                else:
                    handles.append(Patch(facecolor=color, edgecolor='none', label=label))
            else:
                breakpoint()
                raise NotImplementedError(f"Chart type '{label_type}' is not implemented.")
        handles_list.append(handles)
            
    for handles in handles_list:
        # Create a standalone legend
                
        width_inches = 10
        height_inches = 0.8
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
        # breakpoint() #test this https://chatgpt.com/share/6800c138-de0c-8000-b0d7-a47e0f69a1d2
        # ncol = compute_optimal_ncol(
        #     labels,
        #     fontsize=FONTSIZE,
        #     fig_width_inches=width_inches, 
        #     dpi=dpi,
        #     handlelength=1,
        #     handletextpad=0.2,
        #     columnspacing=0.3,
        #     char_width_multiplier=plotting_specifications['LEGEND_FONTSIZE_MULT']#dont know why but sometimes need to set this to 3.5, but sometimes not. 
        # )
        # inside create_legend(), after you have `labels` and created your `handles` list:
        # breakpoint()
        ncol, rows = compute_optimal_ncol(
            labels,
            fontsize=FONTSIZE,
            fig_width_inches=width_inches,
            dpi=dpi,
            handlelength=1,
            handletextpad=0.2,
            columnspacing=0.3,
            max_rows=plotting_specifications.get('MAX_LEGEND_ROWS', 3),
            char_width_multiplier=plotting_specifications['LEGEND_FONTSIZE_MULT']
        )
        # breakpoint()
        # Now build the column-major ordering of indices:
        nrow = len(rows)
        # pad each row to length ncol with None
        padded = [row + [None]*(ncol - len(row)) for row in rows]

        # flatten by columns, skipping None
        order = []
        for c in range(ncol):
            for r in range(nrow):
                idx = padded[r][c]
                if idx is not None:
                    order.append(idx)
        
        # reorder your handles
        try:
            handles_ordered = [handles[i] for i in order]
        except:
            breakpoint()#chances are its an issue where you ahve rerun the mapping functions after changing a plotting name
            handles_ordered = [handles[i] for i in order]
        # handles_ordered = reorder_handles_row_major(handles, ncol)

        legend = ax.legend(
            handles=handles_ordered,
            loc='upper left',
            bbox_to_anchor=(0, 1),
            ncol=ncol,
            fontsize=FONTSIZE,
            prop={'size': FONTSIZE, 'family': 'Calibri'},
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
        # plt.tight_layout()
        folder_path = f'../output/plotting_output/{ECONOMY_ID}'
        file_path = folder_path + f'/legend_{uuid.uuid4()}.png'  
        #save it to plotting output  with a unique id in the economy foldder so we can load it and save it to the xlsx
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        plt.savefig(file_path, dpi=dpi, pad_inches=0)#bbox_inches='tight', 
        plt.close()
                
        # # 3. Reopen and resize to fixed pixel size
        # from PIL import Image
        # img = Image.open(file_path)
        # img = img.resize((int(width_pixels), int(height_pixels)), Image.LANCZOS)
        # img.save(file_path)
        while not os.path.exists(file_path):
            #wait a second and then check
            time.sleep(1)
        worksheet.insert_image(chart_positions[0], file_path)
        
    return worksheet

def compute_optimal_ncol(
    labels,
    fontsize=9,
    fig_width_inches=10,
    dpi=300,
    left_margin=0,
    right_margin=0.1,
    handlelength=1.0,
    handletextpad=0.2,
    columnspacing=0.3,
    max_rows=3,
    char_width_multiplier=2.5
):
    # 1) pixel geometry
    total_px = fig_width_inches * dpi
    usable_px = total_px * (1 - left_margin - right_margin)

    # 2) compute each label’s width in px
    cw = fontsize * char_width_multiplier
    hl = handlelength * fontsize
    htp = handletextpad * fontsize
    cs = columnspacing * fontsize

    label_widths = [
        hl + htp + len(lbl)*cw + cs
        for lbl in labels
    ]

    # 3) find a valid row‑packing
    rows = _pack_labels_into_rows(label_widths, usable_px, max_rows, labels)

    # 4) derive ncol as the longest row
    ncol = max(len(r) for r in rows)
    return ncol, rows


# def _pack_labels_into_rows(label_widths, usable_width_px, max_rows, labels):
#     """
#     Try 1 row, 2 rows, ..., up to max_rows.
#     For each r, best‑fit‑decreasing into r bins of capacity usable_width_px.
#     Return the first successful assignment: a list of r rows, each row is a list of label-indices.
#     """
#     n = len(label_widths)

#     for r in range(1, max_rows+1):
#         # skip impossible ncol < 1
#         if r > n:
#             break

#         # initialize empty rows
#         rows = [[] for _ in range(r)]
#         widths = [0.0]*r

#         # sort labels by descending width
#         for idx in sorted(range(n), key=lambda i: label_widths[i], reverse=True):
#             w = label_widths[idx]
#             # find the row that leaves the least leftover space ≥ 0
#             best = None
#             best_left = None
#             for i in range(r):
#                 left = usable_width_px - (widths[i] + w)
#                 if left >= 0 and (best_left is None or left < best_left):
#                     best_left, best = left, i
#             if best is None:
#                 break  # fails for this r
#             rows[best].append(idx)
#             widths[best] += w
#         else:
#             # all labels placed
#             return rows
    
#     # Build a best‑guess fallback: assign each label, largest first,
#     # into the row with the smallest current width (ignoring the capacity).
#     bins = [[] for _ in range(max_rows)]
#     widths = [0.0] * max_rows
#     for idx in sorted(range(n), key=lambda i: label_widths[i], reverse=True):
#         # pick the row that’s currently shortest
#         i = min(range(max_rows), key=lambda j: widths[j])
#         bins[i].append(labels[idx])
#         widths[i] += label_widths[idx]

#     # Compose an informative message
#     msg = [
#         f"Cannot pack {n} labels into ≤{max_rows} rows of width {usable_width_px:.0f}px.",
#         "Best guess row layout:"
#     ]
#     for row_i, row_labels in enumerate(bins, start=1):
#         msg.append(f"  Row {row_i}: {row_labels!r}")
#     breakpoint()
#     raise ValueError("\n".join(msg))
# # if we get here no packing was possible
# raise ValueError(f"Cannot pack {n} labels into ≤{max_rows} rows of width {usable_width_px:.0f}px, for labels {labels}")
def _pack_labels_into_rows(label_widths, usable_width_px, max_rows, labels):
    """
    1) Try the order-preserving wrap-and-fill (row 1, then 2, …) for each r.
    2) If that fails, do an order-preserving best-fit: for each label in its original
       sequence, place it into the row which, after adding it, leaves the smallest
       leftover space ≥ 0.  This keeps labels in order but still packs tightly.
    """
    n = len(label_widths)

    # 1) Sequential wrap-and-fill
    for r in range(1, max_rows+1):
        rows = [[] for _ in range(r)]
        widths = [0.0]*r
        row = 0
        ok = True
        for idx, w in enumerate(label_widths):
            if widths[row] + w <= usable_width_px:
                rows[row].append(idx)
                widths[row] += w
            else:
                row += 1
                if row >= r:
                    ok = False
                    break
                rows[row].append(idx)
                widths[row] = w
        if ok:
            return rows

    # 2) Order-preserving best-fit
    for r in range(1, max_rows+1):
        rows = [[] for _ in range(r)]
        widths = [0.0]*r
        for idx, w in enumerate(label_widths):
            # find the row that will have the minimal leftover after placing this label
            candidates = [
                (usable_width_px - (widths[j] + w), j)
                for j in range(r)
                if widths[j] + w <= usable_width_px
            ]
            if not candidates:
                break
            # pick the candidate with smallest leftover; ties → lowest row index
            _, best_row = min(candidates)
            rows[best_row].append(idx)
            widths[best_row] += w
        else:
            return rows

    # 3) Last-resort fallback (just evenly distribute biggest first)
    bins = [[] for _ in range(max_rows)]
    widths = [0.0]*max_rows
    for idx in sorted(range(n), key=lambda i: label_widths[i], reverse=True):
        j = min(range(max_rows), key=lambda x: widths[x])
        bins[j].append(labels[idx])
        widths[j] += label_widths[idx]

    msg = [f"Cannot pack {n} labels into ≤{max_rows} rows of width {usable_width_px:.0f}px.",
           "Best guess row layout:"]
    for i, lab in enumerate(bins, 1):
        msg.append(f"  Row {i}: {lab!r}")
    raise ValueError("\n".join(msg))


# def compute_optimal_ncol(
#     labels,
#     fontsize=9,
#     fig_width_inches=10,
#     dpi=300,
#     left_margin=0,
#     right_margin=0,
#     handlelength=1.0,        # Matplotlib legend default (in font units)
#     handletextpad=0.2,       # space between box and text (also in font units)
#     columnspacing=0.3,       # space between columns (in font units)
#     max_rows=4,
#     char_width_multiplier=2.5
# ):
#     # Convert figure width to usable width in pixels
#     total_width_px = fig_width_inches * dpi
#     usable_width_px = total_width_px * (1 - left_margin - right_margin)

#     # Convert font-relative units into pixels
#     cw = fontsize * char_width_multiplier
#     hl = handlelength * fontsize
#     htp = handletextpad * fontsize
#     cs = columnspacing * fontsize

#     # Compute each label’s total width
#     label_widths = [
#         hl + htp + len(label)*cw + cs
#         for label in labels
#     ]
#     total_labels = len(labels)

#     # Try all possible column counts, from most columns (fewest rows) downward
#     for trial_ncol in range(total_labels, 0, -1):
#         rows = math.ceil(total_labels / trial_ncol)
#         if rows > max_rows:
#             continue

#         # if any single label is already too wide, skip
#         if max(label_widths) > usable_width_px:
#             continue

#         # Prepare empty rows (bins)
#         bins = [0.0]*rows

#         # Best‑Fit‑Decreasing: place largest labels first into the tightest fitting row
#         for w in sorted(label_widths, reverse=True):
#             # find the row that, after adding w, leaves the smallest leftover space ≥ 0
#             best_i = None
#             best_leftover = None
#             for i, current in enumerate(bins):
#                 leftover = usable_width_px - (current + w)
#                 if leftover >= 0 and (best_leftover is None or leftover < best_leftover):
#                     best_leftover = leftover
#                     best_i = i
#             if best_i is None:
#                 break  # this label won’t fit in any row
#             bins[best_i] += w
#         else:
#             # if we never broke out early, every label found a home
#             return trial_ncol

#     raise ValueError(
#         f"Legend cannot fit within {max_rows} rows "
#         f"for width={fig_width_inches}″ and fontsize={fontsize} "
#         f"with {total_labels} labels."
#     )
    
# def reorder_handles_row_major(handles, ncol):
#     """
#     Given a list of legend handles and a desired number of columns (ncol),
#     reorder the handles so that when Matplotlib arranges them (columnwise by default)
#     the visual order is row-major (i.e., items are read left-to-right, top-to-bottom).
    
#     Parameters:
#         handles (list): The list of legend handle objects in natural (row-major) order.
#         ncol (int): The number of columns for the legend.
        
#     Returns:
#         list: A new list of handles reordered for row-major display.
#     """
#     n = len(handles)
#     nrow = int(math.ceil(n / ncol))
    
#     # Create a grid (list of rows) in row-major order.
#     grid = [handles[i * ncol : (i + 1) * ncol] for i in range(nrow)]
    
#     # Pad the last row if needed so every row has ncol elements.
#     if len(grid[-1]) < ncol:
#         grid[-1].extend([None] * (ncol - len(grid[-1])))
    
#     # Now transpose the grid.
#     new_handles = []
#     for col in range(ncol):
#         for row in range(nrow):
#             item = grid[row][col]
#             if item is not None:
#                 new_handles.append(item)
                
#     return new_handles

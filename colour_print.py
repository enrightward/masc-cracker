from colr import color
import curses, itertools, numpy as np, random as rd

WHITE = (255, 255, 255)
GREY = (100, 100, 100)
BLACK = (0, 0, 0)

def rgb_heatmap(num):
    result = []
    delta = 255.0/float(num)

    for i in range(num):
        r = 0

        if i < num/2:
            g = 2 * (i * delta)
            b = 255.0 - 2 * (i * delta)

        else:
            j = i - (num/2)
            r = 2 * j * delta
            g = 255.0 - 2 * (j * delta)

        triple = (r, g, b)
        result.append(triple)

    return result

def colour_text(text, rgb):
    background = BLACK
    return color(text, fore=rgb, back=background)

def get_entry_rgb(entry, hmap, maxval):

    if maxval != 0:
        idx = max(int(np.ceil(len(hmap) * (entry/maxval))) - 1, 0)

    else:
        idx = 0

    return hmap[idx]


def row_string_template(i, idx_to_alpha):
    template = ' %s  %s'
    letter = '%s'
    stars = ' '.join(['%s'] * len(idx_to_alpha))
    values = (letter, stars)
    template = template % values
    return template


def row_string_vals(row, hmap, maxval):
    row_vals = ['*' for x in row]
    row_colour = get_entry_rgb(np.max(row), hmap, maxval)
    row_colours = [get_entry_rgb(x, hmap, maxval) for x in row]
    return (row_vals, row_colours, row_colour)


def hmap_display_bigrams(array, hmap, idx_to_alpha):
    _, width = array.shape
    maxval = np.max(array)
    top_rgbs = [get_entry_rgb(x, hmap, maxval) for x in np.max(array, axis=0)]
    top_letters = [idx_to_alpha[i] for i, _ in enumerate(top_rgbs)]
    values = tuple([' '] + top_letters)
    template = row_string_template(-1, idx_to_alpha)
    top_string = template % values
    lines = [(top_string, top_rgbs), '']

    for i, row in enumerate(array):
        template = row_string_template(i, idx_to_alpha)
        row_vals, row_colours, row_colour = row_string_vals(row, hmap, maxval)
        letter = idx_to_alpha[i]
        values = tuple([letter] + row_vals)
        line = template % values
        data = (line, [row_colour] + row_colours)
        lines.append(data)

    return lines


def rgb_to_curses_colour_old(rgb):
    num_cols = curses.COLORS
    r, g, b = tuple(map(int, rgb))
    idx = (r + g + b) % num_cols
    idx = int(idx/4)
    return curses.color_pair(idx)


def hmap_display_bigrams_old(array, hmap, idx_to_alpha):
    _, width = array.shape
    maxval = np.max(array)
    top_rgbs = [get_entry_rgb(x, hmap, maxval) for x in np.max(array, axis=0)]
    top_letters = [colour_text(idx_to_alpha[i], rgb) for i, rgb in enumerate(top_rgbs)]
    values = tuple([' '] + top_letters)
    template = row_string_template(-1, idx_to_alpha)
    top_string = template % values
    lines = [top_string]

    for i, row in enumerate(array):
        template = row_string_template(i, idx_to_alpha)
        row_vals, row_colour = row_string_vals(row, hmap, maxval)
        letter = colour_text(idx_to_alpha[i], row_colour)
        letter = idx_to_alpha[i]
        values = tuple([letter] + row_vals)
        lines.append(template % values)

    return lines


def exit():
    curses.echo()
    curses.nocbreak()
    curses.endwin()


def print_colour_line(stdscr, chars, colours, y):
    for i, (char, col) in enumerate(zip(chars, colours)):
        stdscr.addstr(y, i, char, col)


def rgb_to_curses_colour(rgb):
    """
    Converts RGB values to the nearest equivalent xterm-256 color.
    (Taken from comment of TerrorBite on Apr 29, 2015 from repo:
    https://gist.github.com/MicahElliott/719710/8b8b962033efed8926ad8a8635b0a48630521a67)
    """
    r, g, b = rgb
    # Default color levels for the color cube
    cubelevels = [0x00, 0x5f, 0x87, 0xaf, 0xd7, 0xff]
    # Generate a list of midpoints of the above list
    snaps = [(x+y)/2 for x, y in list(zip(cubelevels, [0]+cubelevels))[1:]]
    # Using list of snap points, convert RGB value to cube indexes
    r, g, b = map(lambda x: len(tuple(s for s in snaps if s < x)), (r, g, b))
    # Simple colorcube transform
    idx = r*36 + g*6 + b + 16
    return curses.color_pair(idx)


def print_block(lines, stdscr):
    rdidx = lambda: rd.sample(range(curses.COLORS), 1)[0]

    try:
        for y, line in enumerate(lines):

            if isinstance(line, tuple):
                chars, rgbs = line
                rgbs = (rgb for rgb in rgbs)
                colours = []

                for a in chars:
                    if a == ' ':
                        colour = curses.color_pair(0)

                    else:
                        colour = rgb_to_curses_colour(next(rgbs))

                    colours.append(colour)

            else:
                chars = line
                colours = [curses.color_pair(0) for a in chars]

            print_colour_line(stdscr, chars, colours, y)

    except curses.error:
        exit()

    stdscr.refresh()

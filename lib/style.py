from rich import print as rprint
import plotly.graph_objects as go
import plotly.express as px

def format_coustom_plotly(
    fig,
    title=None,
    legend=dict(),
    fontsize=16,
    figsize=None,
    ranges=(None, None),
    matches=("x", "y"),
    tickformat=(".s", ".s"),
    log=(False, False),
    margin={"auto": True},
    add_units=False,
    debug=False,
):
    """
    Format a plotly figure

    Args:
        fig (plotly.graph_objects.Figure): plotly figure
        title (str): title of the figure (default: None)
        legend (dict): legend options (default: dict())
        fontsize (int): font size (default: 16)
        figsize (tuple): figure size (default: None)
        ranges (tuple): axis ranges (default: (None,None))
        matches (tuple): axis matches (default: ("x","y"))
        tickformat (tuple): axis tick format (default: ('.s','.s'))
        log (tuple): axis log scale (default: (False,False))
        margin (dict): figure margin (default: {"auto":True,"color":"white","margin":(0,0,0,0)})
        add_units (bool): True to add units to axis labels, False otherwise (default: False)
        debug (bool): True to print debug statements, False otherwise (default: False)

    Returns:
        fig (plotly.graph_objects.Figure): plotly figure
    """
    # Find the number of subplots
    if type(fig) == go.Figure:
        try:
            rows, cols = fig._get_subplot_rows_columns()
            rows, cols = rows[-1], cols[-1]
        except Exception:
            rows, cols = 1, 1
            rprint("[red]Error: unknown figure type[/red]")
    else:
        rows, cols = 1, 1
        rprint("[red]Error: unknown figure type[/red]")

    if debug:
        rprint("[blue]Detected number of subplots: " + str(rows * cols) + "[/blue]")

    if figsize == None:
        figsize = (800 + 400 * (cols - 1), 600 + 200 * (rows - 1))

    default_margin = {"color": "white", "margin": (0, 0, 0, 0)}
    if margin != None:
        for key in default_margin.keys():
            if key not in margin.keys():
                margin[key] = default_margin[key]

    fig.update_layout(
        title=title,
        legend=legend,
        template="presentation",
        font=dict(size=fontsize),
        paper_bgcolor=margin["color"],
    )  # font size and template

    fig.update_xaxes(
        matches=matches[0],
        showline=True,
        mirror="ticks",
        showgrid=True,
        minor_ticks="inside",
        tickformat=tickformat[0],
        # range=ranges[0],
    )  # tickformat=",.1s" for scientific notation

    if ranges[0] != None:
        fig.update_xaxes(range=ranges[0])
    if ranges[1] != None:
        fig.update_yaxes(range=ranges[1])

    fig.update_yaxes(
        matches=matches[1],
        showline=True,
        mirror="ticks",
        showgrid=True,
        minor_ticks="inside",
        tickformat=tickformat[1],
        # range=ranges[1],
    )  # tickformat=",.1s" for scientific notation

    if figsize != None:
        fig.update_layout(width=figsize[0], height=figsize[1])
    if log[0]:
        fig.update_xaxes(type="log", tickmode="linear")
    if log[1]:
        fig.update_yaxes(type="log", tickmode="linear")
    if margin["auto"] == False:
        fig.update_layout(
            margin=dict(
                l=margin["margin"][0],
                r=margin["margin"][1],
                t=margin["margin"][2],
                b=margin["margin"][3],
            )
        )
    # Update axis labels to include units
    if add_units:
        try:
            fig.update_xaxes(
                title_text=fig.layout.xaxis.title.text
                + get_units(fig.layout.xaxis.title.text, debug=debug)
            )
        except AttributeError:
            pass
        try:
            fig.update_yaxes(
                title_text=fig.layout.yaxis.title.text
                + get_units(fig.layout.yaxis.title.text, debug=debug)
            )
        except AttributeError:
            pass
    return fig


def get_units(var, debug=False):
    """
    Returns the units of a variable based on the variable name

    Args:
        var (str): variable name
    """
    units = {
        "T": " (s) ",
        "Amplitude": " (mV) ",
    }
    unit = ""
    for unit_key in list(units.keys()):
        if debug:
            print("Checking for " + unit_key + " in " + var)
        if var.endswith(unit_key):
            unit = units[unit_key]
            if debug:
                print("Unit found for " + var)
    return unit
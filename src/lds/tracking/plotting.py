
import numpy as np
import plotly.graph_objects as go

def get_fig_mfs_positions_2D(time, measurements=None,
                             filtered_means=None,
                             smoothed_means=None,
                             color_measurements="black",
                             color_filtered="red",
                             color_smoothed="green",
                             xlabel="x (pixels)", ylabel="y (pixels)",
                             hovertemplate="<b>x:</b>%{x:.3f}<br><b>y</b>:%{y:.3f}<br><b>time</b>:%{customdata} sec",
                            ):
    """Returns a figure with measured, filtered and/or smoothed (mfs) positions
    with the x and y components plotted against each other.
    """
    fig = go.Figure()
    if measurements is not None:
        trace = go.Scatter(x=measurements[0, :], y=measurements[1, :],
                          mode="lines+markers",
                          marker={"color": color_measurements},
                          customdata=time,
                          hovertemplate=hovertemplate,
                          name="measurements",
                          showlegend=True,
                          )
        fig.add_trace(trace)
    if filtered_means is not None:
        trace = go.Scatter(x=filtered_means[0, :],
                           y=filtered_means[1, :],
                           mode="lines+markers",
                           marker={"color": color_filtered},
                           customdata=time,
                           hovertemplate=hovertemplate,
                           name="filtered",
                           showlegend=True,
                           )
        fig.add_trace(trace)
    if smoothed_means is not None:
        trace = go.Scatter(x=smoothed_means[0, :],
                           y=smoothed_means[1, :],
                           mode="lines+markers",
                           marker={"color": color_smoothed},
                           customdata=time,
                           hovertemplate=hovertemplate,
                           name="smoothed",
                           showlegend=True,
                           )
        fig.add_trace(trace)
    fig.update_layout(xaxis_title=xlabel, yaxis_title=ylabel,
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)')
    return fig

def get_fig_mfdfs_kinematics_1D(time, yaxis_title,
                                measurements=None,
                                finite_differences=None,
                                filtered_means=None,
                                filtered_stds=None,
                                smoothed_means=None,
                                smoothed_stds=None,
                                color_measurements="black",
                                color_fd="blue",
                                color_pattern_filtered="rgba(255,0,0,{:f})",
                                color_pattern_smoothed="rgba(0,255,0,{:f})",
                                cb_alpha=0.3,
                                symbol_x="circle", symbol_y="circle-open",
                                xlabel1D="x (pixels)", ylabel1D="y (pixels)",
                                xlabel2D="time (sec)", ylabel2D="position (pixels)",
                               ):
    """Returns a figure with measurements, finite differences, filtered and/or
    smoothed (mfs) kinematics (e.g., positions, velocities or accelerations)
    with the x and y components plotted against time.
    """
    fig = go.Figure()
    if finite_differences is not None:
        trace_x = go.Scatter(x=time,
                             y=finite_differences[0, :],
                             mode="lines+markers",
                             marker={"color": color_fd},
                             name="finite diff x",
                             showlegend=True,
                             )
        trace_y = go.Scatter(x=time,
                             y=finite_differences[1, :],
                             mode="lines+markers",
                             marker={"color": color_fd},
                             name="finite diff y",
                             showlegend=True,
                             )
        fig.add_trace(trace_x)
        fig.add_trace(trace_y)
    if measurements is not None:
        trace_x = go.Scatter(x=time,
                             y=measurements[0, :],
                             mode="lines+markers",
                             marker={"color": color_measurements,
                                     "symbol": symbol_x},
                             name="measurements x",
                             showlegend=True,
                             )
        trace_y = go.Scatter(x=time,
                             y=measurements[1, :],
                             mode="lines+markers",
                             marker={"color": color_measurements,
                                     "symbol": symbol_y},
                             name="measurements y",
                             showlegend=True,
                             )
        fig.add_trace(trace_x)
        fig.add_trace(trace_y)
    if filtered_means is not None and filtered_stds is not None:
        filter_mean_x = filtered_means[0, :]
        filter_mean_y = filtered_means[1, :]
        filter_ci_x_upper = filter_mean_x + 1.96*filtered_stds[0, :]
        filter_ci_x_lower = filter_mean_x - 1.96*filtered_stds[0, :]
        filter_ci_y_upper = filter_mean_y + 1.96*filtered_stds[1, :]
        filter_ci_y_lower = filter_mean_y - 1.96*filtered_stds[1, :]

        trace_x = go.Scatter(
            x=time, y=filter_mean_x,
            mode="lines+markers",
            marker={"color": color_pattern_filtered.format(1.0)},
            name="filtered x",
            showlegend=True,
            legendgroup="filtered_x",
        )
        trace_x_cb = go.Scatter(
            x=np.concatenate([time, time[::-1]]),
            y=np.concatenate([filter_ci_x_upper, filter_ci_x_lower[::-1]]),
            fill="toself",
            fillcolor=color_pattern_filtered.format(cb_alpha),
            line=dict(color=color_pattern_filtered.format(0.0)),
            showlegend=False,
            legendgroup="filtered_x",
        )
        trace_y = go.Scatter(
            x=time, y=filter_mean_y,
            mode="lines+markers",
            marker={"color": color_pattern_filtered.format(1.0)},
            name="filtered y",
            showlegend=True,
            legendgroup="filtered_y",
        )
        trace_y_cb = go.Scatter(
            x=np.concatenate([time, time[::-1]]),
            y=np.concatenate([filter_ci_y_upper, filter_ci_y_lower[::-1]]),
            fill="toself",
            fillcolor=color_pattern_filtered.format(cb_alpha),
            line=dict(color=color_pattern_filtered.format(0.0)),
            showlegend=False,
            legendgroup="filtered_y",
        )
        fig.add_trace(trace_x)
        fig.add_trace(trace_x_cb)
        fig.add_trace(trace_y)
        fig.add_trace(trace_y_cb)

    if smoothed_means is not None and smoothed_stds is not None:
        smooth_mean_x = smoothed_means[0, :]
        smooth_mean_y = smoothed_means[1, :]
        smooth_ci_x_upper = smooth_mean_x + 1.96*smoothed_stds[0, :]
        smooth_ci_x_lower = smooth_mean_x - 1.96*smoothed_stds[0, :]
        smooth_ci_y_upper = smooth_mean_y + 1.96*smoothed_stds[1, :]
        smooth_ci_y_lower = smooth_mean_y - 1.96*smoothed_stds[1, :]

        trace_x = go.Scatter(
            x=time, y=smooth_mean_x,
            mode="lines+markers",
            marker={"color": color_pattern_smoothed.format(1.0)},
            name="smoothed x",
            showlegend=True,
            legendgroup="smoothed_x",
        )
        trace_x_cb = go.Scatter(
            x=np.concatenate([time, time[::-1]]),
            y=np.concatenate([smooth_ci_x_upper, smooth_ci_x_lower[::-1]]),
            fill="toself",
            fillcolor=color_pattern_smoothed.format(cb_alpha),
            line=dict(color=color_pattern_smoothed.format(0.0)),
            showlegend=False,
            legendgroup="smoothed_x",
        )
        trace_y = go.Scatter(
            x=time, y=smooth_mean_y,
            mode="lines+markers",
            marker={"color": color_pattern_smoothed.format(1.0)},
            name="smoothed y",
            showlegend=True,
            legendgroup="smoothed_y",
        )
        trace_y_cb = go.Scatter(
            x=np.concatenate([time, time[::-1]]),
            y=np.concatenate([smooth_ci_y_upper, smooth_ci_y_lower[::-1]]),
            fill="toself",
            fillcolor=color_pattern_smoothed.format(cb_alpha),
            line=dict(color=color_pattern_smoothed.format(0.0)),
            showlegend=False,
            legendgroup="smoothed_y",
        )
        fig.add_trace(trace_x)
        fig.add_trace(trace_x_cb)
        fig.add_trace(trace_y)
        fig.add_trace(trace_y_cb)

    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)',
                      xaxis_title="time (sec)",
                      yaxis_title=yaxis_title,
                     )
    return fig

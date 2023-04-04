
"""
Offline smoothing of a simulated mouse trajectory
=================================================

The code below performs online Kalman filtering of a simulated mouse
trajectory.

"""

#%%
# Import packages
# ~~~~~~~~~~~~~~~

import configparser
import numpy as np
import pandas as pd

import lds_python.simulation
import lds_python.inference


#%%
# Set initial conditions and parameters
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

pos_x0 = 0.0
pos_y0 = 0.0
vel_x0 = 0.0
vel_y0 = 0.0
ace_x0 = 0.0
ace_y0 = 0.0
dt = 1e-3
num_pos = 1000
sigma_a = 1.0
sigma_x = 1.0
sigma_y = 1.0
sqrt_diag_V0_value = 1e-03

#%%
# Set LDS parameters
# ~~~~~~~~~~~~~~~~~~

# Taken from the book
# barShalomEtAl01-estimationWithApplicationToTrackingAndNavigation.pdf
# section 6.3.3

# Eq. 6.3.3-2
B = np.array([[1, dt, .5*dt**2, 0, 0, 0],
              [0, 1, dt, 0, 0, 0],
              [0, 0, 1, 0, 0, 0],
              [0, 0, 0, 1, dt, .5*dt**2],
              [0, 0, 0, 0, 1, dt],
              [0, 0, 0, 0, 0, 1]], dtype=np.double)
Z = np.array([[1, 0, 0, 0, 0, 0],
              [0, 0, 0, 1, 0, 0]], dtype=np.double)
# Eq. 6.3.3-4
Qe = np.array([[dt**4/4, dt**3/2, dt**2/2, 0, 0, 0],
               [dt**3/2, dt**2,   dt,      0, 0, 0],
               [dt**2/2, dt,      1,       0, 0, 0],
               [0, 0, 0, dt**4/4, dt**3/2, dt**2/2],
               [0, 0, 0, dt**3/2, dt**2,   dt],
               [0, 0, 0, dt**2/2, dt,      1]],
              dtype=np.double)
Q = Qe*sigma_a**2
R = np.diag([sigma_x**2, sigma_y**2])
m0 = np.array([pos_x0, vel_x0, ace_x0, pos_y0, vel_y0, ace_y0],
              dtype=np.double)
V0 = np.diag(np.ones(len(m0))*sqrt_diag_V0_value**2)

#%%
# Sample from the LDS
# ~~~~~~~~~~~~~~~~~~~
# View source code of `lds_python.simulation.simulateLDS
# <https://joacorapela.github.io/lds_python/_modules/lds_python/simulation.html#simulateLDS>`_

x0, x, y = lds_python.simulation.simulateLDS(N=num_pos, B=B, Q=Q, Z=Z, R=R,
                                             m0=m0, V0=V0)

#%%
# Perform batch filtering
# ~~~~~~~~~~~~~~~~~~~~~~~
# View source code of `lds_python.inference.filterLDS_SS_withMissingValues_np
# <https://joacorapela.github.io/lds_python/_modules/lds_python/inference.html#filterLDS_SS_withMissingValues_np>`_

Q = sigma_a*Qe
filterRes = lds_python.inference.filterLDS_SS_withMissingValues_np(
    y=y, B=B, Q=Q, m0=m0, V0=V0, Z=Z, R=R)

#%%
# Perform batch smoothing
# ~~~~~~~~~~~~~~~~~~~~~~~
# View source code of `lds_python.inference.smoothLDS_SS
# <https://joacorapela.github.io/lds_python/_modules/lds_python/inference.html#smoothLDS_SS>`_

smoothRes = lds_python.inference.smoothLDS_SS(
    B=B, xnn=filterRes["xnn"], Vnn=filterRes["Vnn"],
    xnn1=filterRes["xnn1"], Vnn1=filterRes["Vnn1"], m0=m0, V0=V0)

#%%
# Set variables for plotting
# ~~~~~~~~~~~~~~~~~~~~~~~~~~

N = y.shape[1]
time = np.arange(0, N*dt, dt)
smoothed_means = smoothRes["xnN"]
smoothed_covs = smoothRes["VnN"]
smoothed_std_x_y = np.sqrt(np.diagonal(a=smoothed_covs, axis1=0, axis2=1))
color_true = "blue"
color_measured = "black"
color_smoothed_pattern = "rgba(255,0,0,{:f})"
cb_alpha = 0.3

#%%
# Define function for plotting
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def get_fig_kinematics_vs_time(
    time,
    true_x, true_y,
    measured_x, measured_y,
    estimated_mean_x, estimated_mean_y,
    estimated_ci_x_upper, estimated_ci_y_upper,
    estimated_ci_x_lower, estimated_ci_y_lower,
    cb_alpha,
    color_true,
    color_measured,
    color_estimated_pattern,
    xlabel, ylabel):

    fig = go.Figure()
    trace_true_x = go.Scatter(
        x=time, y=true_x,
        mode="markers",
        marker={"color": color_true},
        name="true x",
        showlegend=True,
    )
    fig.add_trace(trace_true_x)
    trace_true_y = go.Scatter(
        x=time, y=true_y,
        mode="markers",
        marker={"color": color_true},
        name="true y",
        showlegend=True,
    )
    fig.add_trace(trace_true_y)
    if measured_x is not None:
        trace_mes_x = go.Scatter(
            x=time, y=measured_x,
            mode="markers",
            marker={"color": color_measured},
            name="measured x",
            showlegend=True,
        )
        fig.add_trace(trace_mes_x)
    if measured_y is not None:
        trace_mes_y = go.Scatter(
            x=time, y=measured_y,
            mode="markers",
            marker={"color": color_measured},
            name="measured y",
            showlegend=True,
        )
        fig.add_trace(trace_mes_y)
    trace_est_x = go.Scatter(
        x=time, y=estimated_mean_x,
        mode="markers",
        marker={"color": color_estimated_pattern.format(1.0)},
        name="estimated x",
        showlegend=True,
        legendgroup="estimated_x",
    )
    fig.add_trace(trace_est_x)
    trace_est_x_cb = go.Scatter(
        x=np.concatenate([time, time[::-1]]),
        y=np.concatenate([estimated_ci_x_upper, estimated_ci_x_lower[::-1]]),
        fill="toself",
        fillcolor=color_estimated_pattern.format(cb_alpha),
        line=dict(color=color_estimated_pattern.format(0.0)),
        showlegend=False,
        legendgroup="estimated_x",
    )
    fig.add_trace(trace_est_x_cb)
    trace_est_y = go.Scatter(
        x=time, y=estimated_mean_y,
        mode="markers",
        marker={"color": color_estimated_pattern.format(1.0)},
        name="estimated y",
        showlegend=True,
        legendgroup="estimated_y",
    )
    fig.add_trace(trace_est_y)
    trace_est_y_cb = go.Scatter(
        x=np.concatenate([time, time[::-1]]),
        y=np.concatenate([estimated_ci_y_upper, estimated_ci_y_lower[::-1]]),
        fill="toself",
        fillcolor=color_estimated_pattern.format(cb_alpha),
        line=dict(color=color_estimated_pattern.format(0.0)),
        showlegend=False,
        legendgroup="estimated_y",
    )
    fig.add_trace(trace_est_y_cb)

    fig.update_layout(xaxis_title=xlabel,
                      yaxis_title=ylabel,
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)',
                      yaxis_range=[estimated_mean_x.min(),
                                   estimated_mean_x.max()],
                     )
    return fig

#%%
# Plot true, measured and smoothed positions (with 95% confidence band)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

true_x = x[0, :]
true_y = x[3, :]
measured_x = y[0, :]
measured_y = y[1, :]
smoothed_mean_x = smoothed_means[0, 0, :]
smoothed_mean_y = smoothed_means[3, 0, :]

smoothed_ci_x_upper = smoothed_mean_x + 1.96*smoothed_std_x_y[:, 0]
smoothed_ci_x_lower = smoothed_mean_x - 1.96*smoothed_std_x_y[:, 0]
smoothed_ci_y_upper = smoothed_mean_y + 1.96*smoothed_std_x_y[:, 3]
smoothed_ci_y_lower = smoothed_mean_y - 1.96*smoothed_std_x_y[:, 3]

fig = get_fig_kinematics_vs_time(
    time=time,
    true_x=true_x, true_y=true_y,
    measured_x=measured_x, measured_y=measured_y,
    estimated_mean_x=smoothed_mean_x, estimated_mean_y=smoothed_mean_y,
    estimated_ci_x_upper=smoothed_ci_x_upper,
    estimated_ci_y_upper=smoothed_ci_y_upper,
    estimated_ci_x_lower=smoothed_ci_x_lower,
    estimated_ci_y_lower=smoothed_ci_y_lower,
    cb_alpha=cb_alpha,
    color_true=color_true, color_measured=color_measured,
    color_estimated_pattern=color_smoothed_pattern,
    xlabel="Time (sec)", ylabel="Position (pixels)")
# fig_filename_pattern = "../../figures/smoothed_pos.{:s}"
# fig.write_image(fig_filename_pattern.format("png"))
# fig.write_html(fig_filename_pattern.format("html"))
fig

#%%
# Plot true and smoothed velocities (with 95% confidence band)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

true_x = x[1, :]
true_y = x[4, :]
measured_x = None
measured_y = None
smoothed_mean_x = smoothed_means[1, 0, :]
smoothed_mean_y = smoothed_means[4, 0, :]

smoothed_ci_x_upper = smoothed_mean_x + 1.96*smoothed_std_x_y[:, 1]
smoothed_ci_x_lower = smoothed_mean_x - 1.96*smoothed_std_x_y[:, 1]
smoothed_ci_y_upper = smoothed_mean_y + 1.96*smoothed_std_x_y[:, 4]
smoothed_ci_y_lower = smoothed_mean_y - 1.96*smoothed_std_x_y[:, 4]

fig = get_fig_kinematics_vs_time(
    time=time,
    true_x=true_x, true_y=true_y,
    measured_x=measured_x, measured_y=measured_y,
    estimated_mean_x=smoothed_mean_x, estimated_mean_y=smoothed_mean_y,
    estimated_ci_x_upper=smoothed_ci_x_upper,
    estimated_ci_y_upper=smoothed_ci_y_upper,
    estimated_ci_x_lower=smoothed_ci_x_lower,
    estimated_ci_y_lower=smoothed_ci_y_lower,
    cb_alpha=cb_alpha,
    color_true=color_true, color_measured=color_measured,
    color_estimated_pattern=color_smoothed_pattern,
    xlabel="Time (sec)", ylabel="Velocity (pixels/sec)")
# fig_filename_pattern = "../../figures/smoothed_vel.{:s}"
# fig.write_image(fig_filename_pattern.format("png"))
# fig.write_html(fig_filename_pattern.format("html"))
fig

#%%
# Plot true and smoothed accelerations (with 95% confidence band)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

true_x = x[2, :]
true_y = x[5, :]
measured_x = None
measured_y = None
smoothed_mean_x = smoothed_means[2, 0, :]
smoothed_mean_y = smoothed_means[5, 0, :]

smoothed_ci_x_upper = smoothed_mean_x + 1.96*smoothed_std_x_y[:, 2]
smoothed_ci_x_lower = smoothed_mean_x - 1.96*smoothed_std_x_y[:, 2]
smoothed_ci_y_upper = smoothed_mean_y + 1.96*smoothed_std_x_y[:, 5]
smoothed_ci_y_lower = smoothed_mean_y - 1.96*smoothed_std_x_y[:, 5]

fig = get_fig_kinematics_vs_time(
    time=time,
    true_x=true_x, true_y=true_y,
    measured_x=measured_x, measured_y=measured_y,
    estimated_mean_x=smoothed_mean_x, estimated_mean_y=smoothed_mean_y,
    estimated_ci_x_upper=smoothed_ci_x_upper,
    estimated_ci_y_upper=smoothed_ci_y_upper,
    estimated_ci_x_lower=smoothed_ci_x_lower,
    estimated_ci_y_lower=smoothed_ci_y_lower,
    cb_alpha=cb_alpha,
    color_true=color_true, color_measured=color_measured,
    color_estimated_pattern=color_smoothed_pattern,
    xlabel="Time (sec)", ylabel="Acceleration (pixels/sec^2)")
# fig_filename_pattern = "../../figures/smoothed_acc.{:s}"
# fig.write_image(fig_filename_pattern.format("png"))
# fig.write_html(fig_filename_pattern.format("html"))
fig


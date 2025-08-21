import matplotlib.pyplot as plt
import numpy as np
from obspy import UTCDateTime
from obspy.clients.fdsn import Client
import cartopy
import matplotlib.pyplot as plt
from ipywidgets import FloatSlider, FloatText, HBox, Label, interactive_output, Output
from IPython.display import display
import matplotlib.patches as patches  


# Download der Daten und Prozessierung
def get_data(station_data,origin_time):
    # Daten Download
    # Station 1
    st1 = client.get_waveforms(
        network=station_data[0]["network"],
        station=station_data[0]["station"],
        location="*",
        channel=station_data[0]["channel"],
        starttime=origin_time-20,
        endtime=origin_time+40, attach_response=True,
    )

    # Station 2
    st2 = client.get_waveforms(
        network=station_data[1]["network"],
        station=station_data[1]["station"],
        location="*",
        channel=station_data[1]["channel"],
        starttime=origin_time-20,
        endtime=origin_time+40, attach_response=True,
    )

    # Station 3
    st3 = client.get_waveforms(
        network=station_data[2]["network"],
        station=station_data[2]["station"],
        location="*",
        channel=station_data[2]["channel"],
        starttime=origin_time-20,
        endtime=origin_time+40, attach_response=True,
    )

    # Vorprozessierung
    st1.remove_response(output="VEL")
    st2.remove_response(output="VEL")
    st3.remove_response(output="VEL")

    # Bandpass Filter
    st1.filter("bandpass", freqmin=2, freqmax=30)
    st2.filter("bandpass", freqmin=2, freqmax=30)
    st3.filter("bandpass", freqmin=2, freqmax=30)

    return st1.trim(origin_time, origin_time+20), st2.trim(origin_time, origin_time+20), st3.trim(origin_time, origin_time+20)


# Interactive Plot Funktion
def plot_with_start_slider(timeseries, initial_start=1, time_range=[0, 10]):
    """
    Plot a timeseries with an interactive slider and numeric box 
    to set the onset (start) point. Returns a dict with updated value.
    
    Parameters
    ----------
    timeseries : obspy.Stream or obspy.Trace
        Seismic timeseries. If a Stream is given, the first Trace will be used.
    """
    # Handle Stream or Trace
    if hasattr(timeseries, "traces"):
        tr = timeseries[0]
    else:
        tr = timeseries

    t = tr.times()
    data = tr.data
    dt = 1.0 / tr.stats.sampling_rate
    onset_val = {'start': initial_start}  # mutable container for updated value

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(t, data, lw=1, color="k")
    onset_line = ax.axvline(initial_start, color='darkred', lw=2, ls="--")
    label = ax.text(initial_start, max(data)*0.9, "Start Signal", color='darkred',
                    rotation=90, va='top', ha='right')

    ax.set_xlim(time_range)
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Amplitude [m/s]")
    ax.set_title(tr.id)
    onset_slider = FloatSlider(
        value=initial_start,
        min=t[0],
        max=t[-1],
        step=dt,
        description='Start'
    )
    onset_box = FloatText(value=initial_start)
    unit_label = Label(" [s]")

    # Update functions
    def update_onset(val):
        x = val['new']
        onset_line.set_xdata([x, x])
        label.set_x(x)
        fig.canvas.draw_idle()
        onset_box.value = x
        onset_val['start'] = x  # update container

    def update_box(change):
        x = change['new']
        onset_slider.value = x
        onset_val['start'] = x  # update container

    onset_slider.observe(update_onset, names='value')
    onset_box.observe(update_box, names='value')

    display(HBox([onset_slider, onset_box, unit_label]))
    plt.show()

    return onset_val  # contains the current value

from ipywidgets import FloatSlider, FloatText, HBox, VBox, interactive_output
import matplotlib.pyplot as plt
from IPython.display import display

def plot_with_p_s(timeseries, initial_p=1, initial_s=3, time_range=[0, 10]):
    """
    Plot a timeseries with interactive sliders to select P- and S-wave onsets.
    Returns a dict with the currently selected P- and S-times.
    """
    # Handle Stream or Trace
    if hasattr(timeseries, "traces"):
        tr = timeseries[0]
    else:
        tr = timeseries

    t = tr.times()
    data = tr.data
    dt = 1.0 / tr.stats.sampling_rate
    values = {'P': initial_p, 'S': initial_s}

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(t, data, lw=1, color="k")
    p_line = ax.axvline(initial_p, color='darkred', lw=2, ls="--")
    s_line = ax.axvline(initial_s, color='darkgreen', lw=2, ls="--")
    p_label = ax.text(initial_p, max(data)*0.9, "P", color='darkred', rotation=90, va='top', ha='right')
    s_label = ax.text(initial_s, max(data)*0.9, "S", color='darkgreen', rotation=90, va='top', ha='right')

    ax.set_xlim(time_range)
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Amplitude [m/s]")
    ax.set_title(tr.id)
    plt.show()

    # Widgets
    p_slider = FloatSlider(value=initial_p, min=t[0], max=t[-1], step=dt, description='P')
    p_box = FloatText(value=initial_p, description='P')
    s_slider = FloatSlider(value=initial_s, min=t[0], max=t[-1], step=dt, description='S')
    s_box = FloatText(value=initial_s, description='S')

    # Update function
    def update(P, S):
        values['P'] = P
        values['S'] = S
        p_line.set_xdata([P, P])
        p_label.set_x(P)
        s_line.set_xdata([S, S])
        s_label.set_x(S)
        fig.canvas.draw_idle()
        return values

    out = interactive_output(update, {'P': p_slider, 'S': s_slider})

    display(VBox([
        HBox([p_slider, p_box]),
        HBox([s_slider, s_box]),
        out
    ]))

    # Synchronize slider and text box
    def sync_slider_box(slider, box):
        def on_slider_change(change):
            box.value = change['new']
        def on_box_change(change):
            slider.value = change['new']
        slider.observe(on_slider_change, names='value')
        box.observe(on_box_change, names='value')

    sync_slider_box(p_slider, p_box)
    sync_slider_box(s_slider, s_box)

    return values


def get_station_info(station_data):
    # Wir sammeln noch die Koordinaten der Stationen (Lat/Lon)
    station_info = []
    for stat in station_data:
        inventory = client.get_stations(network=stat["network"],
                                        station=stat["station"],
                                        channel=stat["channel"],
                                        level="station",
                                        starttime=origin_time,endtime=origin_time+20,)
        
        sta = inventory[0][0]  # Network -> Station
        
        station_info.append([stat["station"],sta.latitude,sta.longitude])
    return station_info

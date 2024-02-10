import streamlit as st
import matplotlib
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

st.title("Jake's Outing Visualizer")
pitch_df = pd.read_parquet('AppDataPitches.parquet')
pitch_df['velo'] = round(pitch_df['velo'], 0)

pitch_list = list(pitch_df['pitchtype'].value_counts().index)
marker_colors = dict(zip(pitch_list,
                         list(sns.color_palette('tab20', n_colors=len(pitch_list)))))

pitcher_list = list(pitch_df.groupby(['name', 'pitchtype'])['pitch_id'].count().reset_index().query('pitch_id >=20')[
                        'name'].sort_values().unique())

col1, col2 = st.columns(2)
with col1:
    # Player
    card_player = st.selectbox('Choose a pitcher:', pitcher_list)

# with col2:
    # Pitch
    # pitches = list(pitch_df.loc[pitch_df['name'] == card_player].groupby('pitchtype')[
    # 'pitch_id'].count().reset_index().sort_values('pitch_id', ascending=False).query('pitch_id>=20')[
    # 'pitchtype'])
    # pitch_type = st.selectbox('Choose a pitch:', pitches)

with col2:
    # Date
    game_dates = list(pitch_df.loc[pitch_df['name'] == card_player].groupby('game_date').count()
                      .reset_index().query('pitch_id>0')['game_date'])
    selected_date = st.selectbox('Choose a Date:', game_dates)

# Plot parameters
sz_bot = 1.5
sz_top = 3.5
x_ft = 2.5
y_bot = -0.5
y_lim = 6
plate_y = -.25

pitch_palette = {'FF': 'C3', 'FS': 'C1', 'KC': 'C2', 'FC': 'C0',
                 'ST': 'C4', 'SL': 'C5', 'CH': 'C6', 'SI': 'C7',
                 'CU': 'C8', 'PO': 'C9'}
def pitch_scatters(card_player, selected_date):
    sns.set_theme(style='darkgrid')
    pitches_scatter = pitch_df.loc[(pitch_df['name'] == card_player) & (pitch_df['game_date'] == selected_date)]

    # Plot Movements
    grid = plt.GridSpec(2, 2, width_ratios=[1, 1], height_ratios=[1, 1])
    # scatter_grid = gridspec.GridSpecFromSubplotSpec(2, 4, subplot_spec=grid[0])
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(grid[0])
    sns.scatterplot(data=pitches_scatter, x='horizontal_movement', y='vertical_movement',
                    hue='pitchtype', s=25, color=marker_colors, legend=False, palette=pitch_palette)

    ax.axhline(0, color='k', linestyle='--', linewidth=1, alpha=0.5)
    ax.axvline(0, color='k', linestyle='--', linewidth=1, alpha=0.5)
    ax.set_xlim(25, -25)
    ax.set_ylim(-22, 22)
    ax.set(aspect=1)

    # Plot Locations
    ax1 = fig.add_subplot(grid[1])
    sns.scatterplot(data=pitches_scatter, x='horizontal_location', y='vertical_location',
                    hue='pitchtype', legend=False, palette=pitch_palette)

    # Strike zone outline
    ax1.plot([-10 / 12, 10 / 12], [sz_bot, sz_bot], color='k', linewidth=2)
    ax1.plot([-10 / 12, 10 / 12], [sz_top, sz_top], color='k', linewidth=2)
    ax1.plot([-10 / 12, -10 / 12], [sz_bot, sz_top], color='k', linewidth=2)
    ax1.plot([10 / 12, 10 / 12], [sz_bot, sz_top], color='k', linewidth=2)

    # Inner Strike Zone
    ax1.plot([-10 / 12, 10 / 12], [1.5 + 2 / 3, 1.5 + 2 / 3], color='k', linewidth=1)
    ax1.plot([-10 / 12, 10 / 12], [1.5 + 4 / 3, 1.5 + 4 / 3], color='k', linewidth=1)
    ax1.axvline(10 / 36, ymin=(sz_bot - y_bot) / (y_lim - y_bot), ymax=(sz_top - y_bot) / (y_lim - y_bot), color='k',
                linewidth=1)
    ax1.axvline(-10 / 36, ymin=(sz_bot - y_bot) / (y_lim - y_bot), ymax=(sz_top - y_bot) / (y_lim - y_bot), color='k',
                linewidth=1)
    # Plate
    ax1.plot([-8.5 / 12, 8.5 / 12], [plate_y, plate_y], color='k', linewidth=2)
    ax1.axvline(8.5 / 12, ymin=(plate_y - y_bot) / (y_lim - y_bot), ymax=(plate_y + 0.15 - y_bot) / (y_lim - y_bot),
                color='k', linewidth=2)
    ax1.axvline(-8.5 / 12, ymin=(plate_y - y_bot) / (y_lim - y_bot), ymax=(plate_y + 0.15 - y_bot) / (y_lim - y_bot),
                color='k', linewidth=2)
    ax1.plot([8.28 / 12, 0], [plate_y + 0.15, plate_y + 0.25], color='k', linewidth=2)
    ax1.plot([-8.28 / 12, 0], [plate_y + 0.15, plate_y + 0.25], color='k', linewidth=2)

    ax1.set(xlim=(-x_ft, x_ft),
            ylim=(y_bot, y_lim),
            aspect=1)

    amovement = pitch_df.loc[pitch_df['name'] == card_player]
    amovement = (amovement.loc[:, ['vertical_movement', 'horizontal_movement', 'name', 'pitchtype']].
                 groupby(['name', 'pitchtype']).mean())

    sns.scatterplot(data=amovement, ax=ax, x='horizontal_movement', y='vertical_movement',
                    hue='pitchtype', legend=True, s=150, palette=pitch_palette, marker='*')
  
    ax.set_title('Pitch Movements')
    ax1.set_title('Locations - '+selected_date)
    ax.legend(title='Season AVG Pitch Movement')
    sns.move_legend(ax, "lower center", bbox_to_anchor=(0.5, -.5), ncol=len(amovement), fontsize=10)
    sns.despine(fig)
    st.pyplot(fig)


pitch_scatters(card_player, selected_date)

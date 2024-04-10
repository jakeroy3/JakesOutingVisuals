import streamlit as st
import matplotlib
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

st.title("Jake's Outing Visualizer")

col1, col2 = st.columns(2)

with col2:
    years = list(('2024', '2023', '2022'))
    selected_year = st.selectbox('Choose a Year:', years)

with col2:
    comparisons = list(('2024', '2023', '2022'))
    compare = st.selectbox('Compare to:', comparisons)

pitch_df = pd.read_parquet('AppDataPitches'+selected_year+'.parquet')
pitch_df['game_date'] = pd.to_datetime(pitch_df['game_date'], format='mixed')
pitch_df['game_date'] = pitch_df['game_date'].dt.date

compare_df = pd.read_parquet('AppDataPitches'+compare+'.parquet')
compare_df['game_date'] = pd.to_datetime(compare_df['game_date'])
compare_df['game_date'] = compare_df['game_date'].dt.date

pitch_list = list(pitch_df['pitch_type'].value_counts().index)
marker_colors = dict(zip(pitch_list,
                         list(sns.color_palette('tab20', n_colors=len(pitch_list)))))

pitcher_list = list(pitch_df.groupby(['player_name', 'pitch_type'])['pitch_id'].count().reset_index().query('pitch_id>=5')[
                        'player_name'].sort_values().unique())


# col1, col2, col3 = st.columns(3)
with col1:
    # Player
    card_player = st.selectbox('Choose a pitcher:', pitcher_list)

# with col2:
    # Pitch
    # pitches = list(pitch_df.loc[pitch_df['name'] == card_player].groupby('pitchtype')[
    # 'pitch_id'].count().reset_index().sort_values('pitch_id', ascending=False).query('pitch_id>=20')[
    # 'pitchtype'])
    # pitch_type = st.selectbox('Choose a pitch:', pitches)

with col1:
    # Date
    game_dates = list(pitch_df.loc[pitch_df['player_name'] == card_player].groupby('game_date').count()
                      .reset_index().query('pitch_id>0')['game_date'])
    selected_date = st.selectbox('Game Date:', game_dates)

# Plot parameters
sz_bot = 1.5
sz_top = 3.5
x_ft = 2.5
y_bot = -0.5
y_lim = 6
plate_y = -.25

pitch_palette = {'FF': 'C3', 'FS': 'C5', 'KC': 'C2', 'FC': 'C0',
                 'ST': 'C4', 'SL': 'C1', 'CH': 'C6', 'SI': 'C8',
                 'CU': 'C9', 'PO': 'C9', 'KN': 'C7', 'FA': 'C10',
                 'EP': 'C8'}

def pitch_scatters(card_player, selected_date):
    sns.set_theme(style='darkgrid')
    pitches_scatter = pitch_df.loc[(pitch_df['player_name'] == card_player) & (pitch_df['game_date'] == selected_date)].query('pitch_id>0')

    # Plot Movements
    grid = plt.GridSpec(2, 2, width_ratios=[1, 1], height_ratios=[1, 1])
    # scatter_grid = gridspec.GridSpecFromSubplotSpec(2, 4, subplot_spec=grid[0])
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(grid[0])
    sns.scatterplot(data=pitches_scatter, x='pfx_x', y='pfx_z',
                    hue='pitch_type', s=25, color=marker_colors, legend=False, palette=pitch_palette)

    ax.axhline(0, color='k', linestyle='--', linewidth=1, alpha=0.5)
    ax.axvline(0, color='k', linestyle='--', linewidth=1, alpha=0.5)
    ax.set_xlim(25, -25)
    ax.set_ylim(-22, 22)
    ax.set(aspect=1)

    # Plot Locations
    ax1 = fig.add_subplot(grid[1])
    sns.scatterplot(data=pitches_scatter, x='plate_x', y='plate_z',
                    hue='pitch_type', legend=False, palette=pitch_palette)

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
    ax1.set_xlabel('Horizontal Location')
    ax1.set_ylabel('Vertical Location')

    ax1.set(xlim=(x_ft, -x_ft),
            ylim=(y_bot, y_lim),
            aspect=1)
    ax1.set_title('Locations ' + str(selected_date) + '\n (Pitcher Perspective)')

    # Create Table for Average Movements
    amovement = compare_df.loc[compare_df['player_name'] == card_player]
    amovementcount = amovement.loc[:, ['player_name', 'pitch_id', 'pitch_type']].groupby(['player_name', 'pitch_type'], as_index=False).count()
    amovementcount = amovementcount.rename(columns={'pitch_id':'count'})
    amovement = amovement.merge(amovementcount, on=['player_name', 'pitch_type'])
    amovement = (amovement.loc[amovement['count'] >= 5, ['pfx_z', 'pfx_x', 'player_name', 'pitch_type']].
                 groupby(['player_name', 'pitch_type']).mean())

    # Plot Season Average Movements
    try:
        sns.scatterplot(data=amovement, ax=ax, x='pfx_x', y='pfx_z',
                        hue='pitch_type', legend=True, s=150, palette=pitch_palette, marker='*')
        ax.set_title('Pitch Movements compared to '+str(compare))
        ax.legend(title='Season AVG Pitch Movement')
        ax.set_xlabel('Horizontal Movement')
        ax.set_ylabel('Vertical Movement')
        sns.move_legend(ax, "lower center", bbox_to_anchor=(0.5, -.55), ncol=(len(amovement)/2)+1, fontsize=10)
        sns.despine(fig)

    except:
        errormessage = ('Not enough pitches in '+compare+' for comparison. Please choose another year to see average movements.')
        st.error(errormessage, icon='🚨')

    st.pyplot(fig)

    # Returns Total Pitches
    start_total = pitches_scatter.loc[:, ['pitch_id', 'player_name']].groupby('player_name', as_index=False).count()
    start_total = start_total.rename(columns={'pitch_id': 'Total'})

    # Returns Pitch Type Pitches
    start_counts = (pitches_scatter.loc[:, ['pitch_id', 'pitch_type', 'player_name']]
                    .groupby(['pitch_type', 'player_name'], as_index=False).count())

    # Set Up Streamlit Table
    # Returns Stats by Pitch
    start_sums = (pitches_scatter.loc[:, ['pitch_type', 'player_name', 'whiff', 'called_strike', 'in_zone',
                                          'contact', 'chase_swing']]
                    .groupby(['pitch_type', 'player_name'], as_index=False).sum())

    # Merges DataFrames
    start_counts = start_total.merge(start_counts)
    start_counts = start_counts.merge(start_sums)
    start_counts = start_counts.drop(columns=['player_name'])

    start_counts['Usage%'] = round((start_counts['pitch_id'] / start_counts['Total'] * 100), 2)
    start_counts['CSW%'] = round(((start_counts['whiff'] + start_counts['called_strike']) / start_counts['pitch_id']) * 100, 2)
    start_counts['Zone%'] = round((start_counts['in_zone'] / start_counts['pitch_id']) * 100, 2)

    # Returns Average Pitch Specs
    start_avgs = (pitches_scatter.loc[:, ['release_speed', 'pitch_type', 'pfx_z', 'pfx_x']]
                  .groupby('pitch_type', as_index=False).mean())
    start_avgs['release_speed'] = round(start_avgs['release_speed'], 2)
    start_avgs['pfx_x'] = round(start_avgs['pfx_x'], 2)
    start_avgs['pfx_z'] = round(start_avgs['pfx_z'], 2)

    start_stats = start_counts.merge(start_avgs, on='pitch_type')
    start_stats = start_stats.rename(columns={'pitch_type': 'Pitch Type', 'pitch_id': '#', 'whiff': 'Whiffs',
                                              'called_strike': 'CS', 'release_speed': 'MPH', 'pfx_z': 'VMov',
                                              'pfx_x': 'HMov', 'contact': 'In Play', 'chase_swing': 'Chases'})
    start_stats = start_stats.drop(columns=['in_zone', 'Total'])
    st.dataframe(data=start_stats, width=1200, column_order=('Pitch Type', '#', 'Usage%', 'MPH', 'CS', 'Whiffs', 'CSW%', 'Chases',
                 'In Play', 'Zone%', 'VMov', 'HMov'), hide_index=True)


pitch_scatters(card_player, selected_date)
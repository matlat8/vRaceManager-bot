import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import discord
import os
import uuid
import datetime

class DriverCharts():
    
    def create_laptime_chart(self, df: pd.DataFrame):
        
        sns.set_theme()
        
        fig, ax = plt.subplots(figsize=(25,8))
        sns.lineplot(x='lap_number', y='lap_time', data=df)
        ax.set_title('Lap Times')
        ax.set_xlabel('Lap Number')
        ax.set_ylabel('Lap Time')
        ax.legend(['Lap Time', 'Fastest Lap', 'Slowest Lap', 'Average Lap'], loc='upper left')
        
        self.min_max_datapoints(df, ax)
        
        ax2 = ax.twinx()
        sns.lineplot(x='lap_number', y='lap_position', data=df, ax=ax2, color='red')
        ax2.set_ylabel('Lap Position')
        ax2.set_ylim(bottom=1, top=max(df['lap_position']) + 1)
        ax2.invert_yaxis()  # Invert the y-axis
        ax2.legend(['Lap Position'], loc='upper right')
        
        # Set the x-axis ticks to increment by 1
        ax.set_xticks(range(min(df['lap_number']), max(df['lap_number'])+1, 1))
        
        
        # Set the y-axis limits to be the average lap time plus and minus 10
        avg_lap_time = df['lap_time'].mean()
        ax.set_ylim(bottom=avg_lap_time - 5, top=avg_lap_time * 1.20)
        
        # Set the y-axis limits to remove whitespace
        ax.set_xlim(left=min(df['lap_number']) - .5, right=max(df['lap_number']))
        
        # Create a table with lap times
        #table_data = df[['lap_number', 'lap_time']].copy()
        #table_data['lap_time'] = table_data['lap_time'].apply(lambda x: f"{int(x//60)}:{int(x%60):02d}.{int((x%1)*1000):03d}")
        #table_data = table_data.values.tolist()  # Use the formatted 'lap_time' values
        #table_data.insert(0, ['Lap Number', 'Lap Time'])  # Add column headers
        #table = plt.table(cellText=table_data, cellLoc='left', loc='right', colWidths=[0.05, 0.1], fontsize=24, bbox=[0.85, 0, 0.15, 1])
        
        # Adjust layout to make room for the table
        #plt.subplots_adjust(right=0.8)
        
        # Save the plot as an image file
        random_uuid = uuid.uuid4()
        filename = f'{random_uuid}.png'
        plt.savefig(filename)
        return filename

    
    def min_max_datapoints(self, df: pd.DataFrame, ax):
        # Find the min and max lap times
        min_lap_time = df['lap_time'].min()
        max_lap_time = df['lap_time'].max()
        avg_lap_time = df['lap_time'].mean()

        # Add data points for the min and max lap times
        ax.scatter(df['lap_number'][df['lap_time'] == min_lap_time], min_lap_time, color='green')
        ax.scatter(df['lap_number'][df['lap_time'] == max_lap_time], max_lap_time, color='red')
        ax.scatter(df['lap_number'], [avg_lap_time]*len(df), color='blue')
        
        # Format the times to be minutes, seconds, and milliseconds
        min_lap_time_str = datetime.timedelta(seconds=int(min_lap_time), milliseconds=int((min_lap_time % 1) * 1000))
        max_lap_time_str = datetime.timedelta(seconds=int(max_lap_time), milliseconds=int((max_lap_time % 1) * 1000))
        avg_lap_time_str = datetime.timedelta(seconds=int(avg_lap_time), milliseconds=int((avg_lap_time % 1) * 1000))

        # Add text labels for the min and max lap times
        ax.text(df['lap_number'][df['lap_time'] == min_lap_time], min_lap_time, f'Fastest: {min_lap_time_str}', horizontalalignment='left')
        ax.text(df['lap_number'][df['lap_time'] == max_lap_time], max_lap_time, f'Slowest: {max_lap_time_str}', horizontalalignment='left')
        ax.text(df['lap_number'].iloc[-1], avg_lap_time, f'Average: {avg_lap_time_str}', horizontalalignment='right')
        
        # Add legend
        ax.scatter(df['lap_number'][df['lap_time'] == min_lap_time], min_lap_time, color='green', label='Fastest Lap')
        ax.scatter(df['lap_number'][df['lap_time'] == max_lap_time], max_lap_time, color='red', label='Slowest Lap')
        ax.scatter(df['lap_number'], [avg_lap_time]*len(df), color='blue', label='Average Lap')
        
        return ax
    
    def create_positionranking_chart(self, df: pd.DataFrame):
        sns.set_theme()
        fig, ax = plt.subplots(figsize=(25,8))
        sns.lineplot(x='lap_number', y='lap_position', data=df)
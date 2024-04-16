import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import discord
import os
import uuid


class DriverCharts():
    
    def create_laptime_chart(self, df: pd.DataFrame, ctx):
        
        sns.set_theme()
        
        fig, ax = plt.subplots(figsize=(25,8))
        sns.lineplot(x='lap_number', y='lap_time', data=df)
        ax.set_title('Lap Times')
        ax.set_xlabel('Lap Number')
        ax.set_ylabel('Lap Time')
        
        # Set the x-axis ticks to increment by 1
        ax.set_xticks(range(min(df['lap_number']), max(df['lap_number'])+1, 1))
        
        # Set the y-axis limits to be the average lap time plus and minus 10
        avg_lap_time = df['lap_time'].mean()
        ax.set_ylim(bottom=avg_lap_time - 5, top=avg_lap_time + 20)
        
        # Set the y-axis limits to remove whitespace
        ax.set_xlim(left=min(df['lap_number']) - .5, right=max(df['lap_number']))
        
        # Create a table with lap times
        table_data = df[['lap_number', 'lap_time']].copy()
        table_data['lap_time'] = table_data['lap_time'].apply(lambda x: f"{int(x//60)}:{int(x%60):02d}.{int((x%1)*1000):03d}")
        table_data = table_data.values.tolist()  # Use the formatted 'lap_time' values
        table_data.insert(0, ['Lap Number', 'Lap Time'])  # Add column headers
        table = plt.table(cellText=table_data, cellLoc='left', loc='right', colWidths=[0.05, 0.1], fontsize=24)
        
        # Adjust layout to make room for the table
        plt.subplots_adjust(right=0.8)
        
        # Save the plot as an image file
        random_uuid = uuid.uuid4()
        filename = f'{random_uuid}.png'
        plt.savefig(filename)
        return filename
        
        
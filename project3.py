import pandas as pd
import numpy as np
import os
import seaborn as sns
import matplotlib as plt

os.chdir(r'C:\Users\laure\summer2025\aae718\project3') 

#data
all_data = []
city_folders = ['chicago', 'manitowoc', 'milwaukee', 'ludington']
for city_folder in city_folders:
    if not os.path.exists(city_folder):
        print(f"not found")
        continue
    
    for filename in os.listdir(city_folder):
        if filename.endswith('.csv'):
            file_path = os.path.join(city_folder, filename)
            
            try:
                df = pd.read_csv(file_path)
                year = filename[-8:-4]
                df = df[['DATE', 'HourlyWindSpeed']].copy()
                df['Station'] = city_folder.capitalize()
                df['Year'] = year
                all_data.append(df)
            except Exception as e:
                print(f"error")

if all_data:
    speed_df = pd.concat(all_data, ignore_index=True)
    speed_df.columns = ['Date', 'HourlyWindSpeed','Station', 'Year']
    speed_df['Date'] = pd.to_datetime(speed_df['Date'], format='ISO8601')
    speed_df['Year'] = speed_df['Date'].dt.year 
    speed_df['Month'] = speed_df['Date'].dt.month
    speed_df['Day'] = speed_df['Date'].dt.day
    speed_df['Hour'] = speed_df['Date'].dt.hour

    speed_df = speed_df.sort_values(['Station', 'Date']).reset_index(drop=True)

    print(speed_df)
    
    speed_df.to_csv('combined_wind_data_cleaned.csv', index=False)
else:
    print("error")


#graph for avg hourly wind across the data period 
speed_df['HourlyWindSpeed'] = pd.to_numeric(speed_df['HourlyWindSpeed'], errors='coerce')
daily_avg = speed_df.groupby(['Station', pd.Grouper(key='Date', freq='D')])['HourlyWindSpeed'].mean().reset_index()


plt.figure(figsize=(14, 7))
sns.set_style("whitegrid")
sns.lineplot(
    data=daily_avg,x='Date', y='HourlyWindSpeed',
    hue='Station',palette='viridis',linewidth=1.5,estimator=None )

plt.title('Daily Average Wind Speeds (2014-2024)', fontsize=14, pad=20)
plt.xlabel('Date', fontsize=12)
plt.ylabel('Wind Speed (mph)', fontsize=12)
plt.xticks(rotation=45)

plt.legend(
    title='Station',bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('station_wind_comparison.png', dpi=300, bbox_inches='tight')
plt.show()

#cities by windiest days 
threshold = speed_df['HourlyWindSpeed'].quantile(0.9)  # 90th percentile 
top_wind_days = speed_df[speed_df['HourlyWindSpeed'] >= threshold]

city_counts = top_wind_days['Station'].value_counts().reset_index()
city_counts.columns = ['Station', 'TopWindDays']

city_counts['Percentage'] = (city_counts['TopWindDays'] / len(top_wind_days)) * 100

plt.figure(figsize=(10, 6))
barplot = sns.barplot(
    data=city_counts,
    x='Station',
    y='TopWindDays',
    order=city_counts.sort_values('TopWindDays', ascending=False)['Station'],
    palette='Purples')
for p in barplot.patches:
    barplot.annotate(
        f"{p.get_height():.0f}\n({p.get_height()/len(top_wind_days)*100:.1f}%)",
        (p.get_x() + p.get_width() / 2., p.get_height()),
        ha='center', va='center', xytext=(0, 10), textcoords='offset points')

plt.title(f"Cities in Top 10% Windiest Days\n(Threshold: {threshold:.1f} mph+)", pad=20)
plt.xlabel('Station')
plt.ylabel('Number of High-Wind Days')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('top_wind_cities_ranked.png', dpi=300)
plt.show()

#wind gust data 
gust_df = []

for city_folder in city_folders:
    if not os.path.exists(city_folder):
        print(f"error")
        continue
    
    for filename in os.listdir(city_folder):
        if filename.endswith('.csv'):
            file_path = os.path.join(city_folder, filename)
            
            try:
                df = pd.read_csv(file_path, low_memory=False)

                df = df[['DATE', 'HourlyWindGustSpeed']].copy()
                df = df[df['HourlyWindGustSpeed'].notna()]
                
                df['HourlyWindGustSpeed'] = pd.to_numeric(
                    df['HourlyWindGustSpeed'],errors='coerce').dropna()
                
                if not df.empty:
                    df['Station'] = city_folder.capitalize()
                    df['Year'] = filename[-8:-4]
                    gust_df.append(df)
                    
            except Exception as e:
                print(f"Error")

gust_df = pd.concat(gust_df, ignore_index=True)    
gust_df.columns = ['Date', 'WindGustSpeed', 'Station', 'Year']
gust_df['Date'] = pd.to_datetime(gust_df['Date'], errors='coerce')
gust_df = gust_df.dropna(subset=['Date'])

gust_df = gust_df.sort_values(['Station', 'Date']).reset_index(drop=True)
print(gust_df)
gust_df.to_csv('raw_wind_gusts.csv', index=False)




#Wind gust frequnecy
plt.figure(figsize=(10, 6))
gust_counts = gust_df['Station'].value_counts().sort_values(ascending=False)
ax = sns.barplot(
    x=gust_counts.index,
    y=gust_counts.values,
    palette="Purples",
    order=gust_counts.index)

total_gusts = len(gust_df)
for p in ax.patches:
    percentage = 100 * p.get_height()/total_gusts
    ax.annotate(
        f'{p.get_height():,.0f}\n({percentage:.1f}%)', 
        (p.get_x() + p.get_width() / 2., p.get_height()),
        ha='center', va='center', xytext=(0, 10), textcoords='offset points')

plt.title('Gust Frequency by Station\n(Total Gusts Observed: {:,})'.format(total_gusts))
plt.xlabel('Station')
plt.ylabel('Number of Gust Observations')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('gust_frequency.png', dpi=300)
plt.show()




##extreme gusts 
#  1% gusts
extreme_threshold = gust_df['WindGustSpeed'].quantile(0.99)
extreme_gusts = gust_df[gust_df['WindGustSpeed'] >= extreme_threshold]

# Plot counts by station
plt.figure(figsize=(8, 6))
sns.countplot(
    data=extreme_gusts,
    y='Station',
    order=extreme_gusts['Station'].value_counts().index,
    palette='Purples')
plt.title(f'Stations with Most Extreme Gusts\n(≥ {extreme_threshold:.1f} mph, Top 1%)')
plt.xlabel('Number of Extreme Gust Events')
plt.tight_layout()
plt.savefig('extreme_gusts.png', dpi=300)
plt.show()

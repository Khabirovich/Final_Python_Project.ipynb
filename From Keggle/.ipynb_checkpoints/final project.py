import pandas as pd
import numpy as np
import sqlite3
import sqlalchemy
import matplotlib as mp
import seaborn as sns
db_file='/Users/khabirovich/Downloads/hw.db'
def get_from_sql(sql):
    rs = None
    with sqlite3.connect(db_file) as cn: #работает через with и сам закрывает
        crs = cn.cursor()
        crs.execute(sql)
        rs = [{v[0]:r[i] for i, v in enumerate(crs.description)} for r in crs.fetchall()] #дклвкм красивыйлист для пандаса
    return rs

sql ='''
SELECT *
FROM 't'
'''
get_from_sql(sql)
with sqlite3.connect(db_file) as cn:
    df = pd.read_sql(sql, cn)
df
g = sns.relplot(x='date', y='total', kind='line', data=df.groupby('date', as_index=False).sum()); g.fig.autofmt_xdate()


df['date'] = pd.to_datetime(df['date'])
df['year'] = df['date'].dt.year
df['isoYear'] = df['date'].dt.isocalendar().year
df['week'] = df['date'].dt.isocalendar().week
df['startOfWeek'] = df['date'] -df['date'].dt.weekday*pd.Timedelta(days=1)
df['doy'] = df['date'].dt.dayofyear
#%%
df
#%%
df_t = df.groupby(['year', 'doy'],as_index=False).sum()
g = sns.relplot(x='doy', y='total', hue='year', kind='line', data=df_t)

df_t = df.groupby(['startOfWeek'],as_index=False).sum()
g = sns.relplot(x='startOfWeek', y='total', kind='line', data=df_t)
g.fig.autofmt_xdate()#%%

#%%
df_t = df.groupby(['isoYear','week'],as_index=False).sum()
g = sns.relplot(x='week', y='total', hue='isoYear', kind='line', data=df_t)
#%%
df.groupby('city').sum()
#%%
df.groupby('city').sum().assign(avg = lambda x: x.total/x.qty)['avg']
df.groupby('item').sum().sort_values(by='total', ascending=False)[['total']].head(10)

sns.distplot(df.groupby('item').sum().assign(avg = lambda x: x.total/x.qty)['avg'])

#%%
df[df['date'].dt.month==6].groupby('item').sum().sort_values(by='total', ascending=False)[['total']].head(10)
df_t = df[df['date'].dt.year==2018].copy()
df_t.loc[:,'qrt'] = 0
df_t.loc[df_t['date'].dt.month >= 4,'qrt'] = 1
df_t.loc[df_t['date'].dt.month >= 7,'qrt'] = 2
df_t.loc[df_t['date'].dt.month >= 10,'qrt'] = 3
df_t = df_t[['item','qrt','total']].groupby(['item','qrt']).sum().unstack()
df_t.columns = [0, 1, 2, 3]
df_t['s'] = df_t[0] + df_t[1] + df_t[2] + df_t[3]
df_t[0] = df_t[0]/df_t['s']
df_t[1] = df_t[1]/df_t['s']
df_t[2] = df_t[2]/df_t['s']
df_t[2] = df_t[3]/df_t['s']
sns.relplot(data=df_t, x=0, y=1)
sns.relplot(data=df_t, x=2, y=3)
sns.relplot(data=df_t, x=0, y=2)#%%

#%%
df_t.loc[:, 'tp'] = 'I'
df_t.loc[df_t[2] > 0.29, 'tp'] = 'II'
df_t.loc[df_t[2] > 0.37, 'tp'] == 'III'
df_m = pd.DataFrame(df_t['tp'], index=df_t.index).reset_index()
#%%
df_tt = df.merge(df_m, on='item').groupby(['tp', 'startOfWeek'], as_index=False).sum()
g = sns.relplot(data=df_tt, x='startOfWeek', y='total', hue='tp', kind='line')
g.fig.autofmt_xdate()#%%

#%%
df_tt = df.merge(df_m, on='item').groupby(['tp', 'city']).sum()[['total']].unstack()
df_tt.columns = [0,1,2,3]
ss = df_tt.sum(axis=1)
for c in df_tt.columns:
    df_tt[c] = df_tt[c]/ss
df_tt = df_tt.stack().reset_index()
df_tt.columns = ['tp', 'city', 'total']
sns.catplot(data=df_tt, x='city', y='total', hue='tp', kind='bar')
#%%

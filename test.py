import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
 
df = sns.load_dataset('iris')
print('Original Dataset')
df.head()
 
scaler = MinMaxScaler()
 
df_scaled = scaler.fit_transform(df[gameStats])
df_scaled = pd.DataFrame(df_scaled, columns=[
  'sepal_length', 'sepal_width', 'petal_length', 'petal_width'])
 
print("Scaled Dataset Using MinMaxScaler")
df_scaled.head()
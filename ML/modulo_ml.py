import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

current_directory = os.path.dirname(os.path.abspath(__file__))
base_directory = os.path.dirname(current_directory)
ml_directory = os.path.join(base_directory, "ML")
data_directory = os.path.join(ml_directory, "sintetico.csv")
df = pd.read_csv(data_directory)

X = df[['Days', 'Average_DMI', 'Energy_density_of_feed', 'Average_number_of_heads']]
y = df['Global_emission_Ton_CO2e']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

linear_model = LinearRegression()
linear_model.fit(X_train, y_train)

y_pred = linear_model.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print('Regressão Linear:')
print(f'Mean Squared Error: {mse:.2f}')
print(f'R2 Score: {r2:.2f}')

model_filename = 'linear_regression_model.pkl'
model_filepath = os.path.join(ml_directory, model_filename)
joblib.dump(linear_model, model_filepath)

print(f'Modelo treinado salvo em: {model_filepath}')

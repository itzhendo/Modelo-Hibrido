# -*- coding: utf-8 -*-
"""14-07-2023.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1UEP1lUqDFzBpQ_3-GTmjQ5gw5_cm5wEF
"""

!pip install tensorflow

!pip install yfinance

import math
import yfinance as yf
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.optimizers import Adam as AdamLegacy
from keras.models import Sequential
from keras.layers import Dense, LSTM
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
from keras.optimizers import Adam
import random
pd.options.mode.chained_assignment = None

#Ativos da bolsa de Valores---------

ativo = "PETR4.SA"
#ativo = "MGLU3.SA"
#ativo =  "BBDC4.SA"
#ativo = "VALE3.SA"
#ativo = "ITUB4.SA"


dados = yf.download(ativo)

dados

cotacao = dados['Close'].to_numpy().reshape(-1,1)
cotacao

# Criar um gráfico de linha
plt.figure(figsize=(10, 6))  # Defina o tamanho da figura conforme necessário
plt.plot(cotacao)
plt.title('Gráfico de Cotação')
plt.xlabel('Período')
plt.ylabel('Cotação')
plt.grid(True)
plt.show()

tamanho_dados_treinamento = int(len(cotacao)*0.8)
tamanho_dados_treinamento

#Transformou os dados em uma escala entre 0 e 1 melhor normalizar os dados para a rede neural-------

escalador = MinMaxScaler(feature_range=(0, 1))

treinamento = escalador.fit_transform(cotacao[0: tamanho_dados_treinamento, :])

teste = escalador.transform(cotacao[tamanho_dados_treinamento: , :])

dadosMinMax = list(treinamento.reshape(len(treinamento))) + list(teste.reshape(len(teste)))

dadosMinMax = np.array(dadosMinMax).reshape(len(dadosMinMax), 1)

dadosMinMax

# Criar um gráfico de linha
plt.figure(figsize=(10, 6))  # Defina o tamanho da figura conforme necessário
plt.plot(dadosMinMax)
plt.title('Gráfico de Cotação')
plt.xlabel('Período')
plt.ylabel('Cotação')
plt.grid(True)
plt.show()

dados_para_treinamento = dadosMinMax[0: tamanho_dados_treinamento, :]

#dados que serão usados para gerar o resultado

treinamento_x = []

#cotação que aconteceu de fato

treinamento_y = []

dias_previsao = 60

for i in range(dias_previsao, len(dados_para_treinamento)):
    #60 ultimos dias
    treinamento_x.append(dados_para_treinamento[i - dias_previsao: i, 0])
    #cotacao
    treinamento_y.append(dados_para_treinamento[i, 0])

    if i <= dias_previsao+1:
        print(treinamento_x)
        print(treinamento_y)

treinamento_x, treinamento_y = np.array(treinamento_x), np.array(treinamento_y)

print(treinamento_x)

treinamento_x = treinamento_x.reshape(treinamento_x.shape[0],treinamento_x.shape[1], 1)

print(treinamento_x)

# Dados para Definir os parâmetros da rede com base no cromossomo
# Ja setados caso nao queira executar o AG

hidden_units = 50
dense = 25
learning_rate = 0.001
num_epochs = 100

def evaluate_fitness(chromosome):
    # Definir os parâmetros da rede com base no cromossomo
    hidden_units = int(chromosome[0])
    dense = chromosome[1]
    learning_rate = chromosome[2]
    num_epochs = int(chromosome[3])
    # Criar o modelo da rede
    model = Sequential()
    model.add(LSTM(hidden_units, return_sequences=True, input_shape=(treinamento_x.shape[1], 1)))
    model.add(LSTM(hidden_units, return_sequences=True))
    model.add(LSTM(hidden_units))
    model.add(Dense(dense))
    model.add(Dense(1))

    # Treinar o modelo
    model.compile(loss='mean_squared_error', optimizer=Adam(learning_rate=learning_rate))
    model.fit(treinamento_x, treinamento_y, batch_size=32, epochs=1)

    dados_teste = dadosMinMax[tamanho_dados_treinamento - dias_previsao: , :]

    teste_x = []
    teste_y = cotacao[tamanho_dados_treinamento:, :]

    for i in range(dias_previsao, len(dados_teste)):
        teste_x.append(dados_teste[i-dias_previsao: i, 0])

    teste_x = np.array(teste_x)
    teste_x = teste_x.reshape(teste_x.shape[0], teste_x.shape[1])

    predicoes = model.predict(teste_x)
    predicoes = escalador.inverse_transform(predicoes)

    rmse = np.sqrt(np.mean(predicoes - teste_y)**2)
    return rmse



def select_parents(fitness_values):
    # Seleciona dois pais aleatórios com base na probabilidade proporcional ao valor de fitness
    total_fitness = np.sum(fitness_values)
    probabilities = fitness_values / total_fitness
    parents_indices = np.random.choice(len(fitness_values), size=2, replace=False, p=probabilities)
    return parents_indices

def reproduce(parents, population_size, mutation_rate):
    # Cruzamento dos pais
    offspring = []
    for _ in range(population_size):
        child = []
        for j in range(len(parents[0])):
            gene = np.random.choice(parents.shape[0])
            child.append(parents[gene][j])
        offspring.append(child)

        # Mutação
    for i in range(population_size):
        if np.random.rand() < mutation_rate:
            gene = np.random.randint(len(offspring[0]))
            offspring[i][gene] += np.random.normal(0, 0.1)

    return offspring

# Definir os parâmetros do algoritmo genético
num_genes = 4  # O número de genes é igual ao número total de pesos na rede neural
population_size = 4              # Tamanho da população
mutation_rate = 0.05              # Taxa de mutação
num_generations = 4             # Número de gerações

#-------------------------------------------------
def individual():
    hidden_units = random.randint(45, 60)
    dense = random.randint(25, 50)
    learning_rate = random.uniform(0.001, 0.01)
    num_epochs = random.randint(10, 100)
    return [hidden_units, dense, learning_rate, num_epochs]

def generate_population(n_de_individuos):
    return [individual() for _ in range(n_de_individuos)]
#-------------------------------------------------
population = generate_population(population_size)  # Populacao inicial 10


# Executar o algoritmo genético para avaliar a aptidão de cada indivíduo na população
for generation in range(num_generations):
    print(f'Generation {generation + 1}:')
    fitness_values = np.array([evaluate_fitness(chromosome) for chromosome in population])
    best_fitness = np.min(fitness_values)
    print(f'Generation {generation + 1}: best fitness = {best_fitness:.4f}')

    # Selecionar os pais para cruzamento
    parents_indices = select_parents(fitness_values)
    parents = np.array([population[i] for i in parents_indices])

    # Gerar nova população por cruzamento e mutação
    offspring = reproduce(parents, population_size, mutation_rate)

    # Avaliar a aptidão dos filhos gerados
    offspring_fitness_values = np.array([evaluate_fitness(child) for child in offspring])

    # Substituir a população atual pelos filhos gerados
    combined_population = np.vstack((population, offspring))
    combined_fitness_values = np.hstack((fitness_values, offspring_fitness_values))
    sorted_indices = np.argsort(combined_fitness_values)
    sorted_indices = np.argsort(fitness_values)
    population = [combined_population[i] for i in sorted_indices[:population_size]]

# Treinar o modelo final usando a melhor solução encontrada pelo algoritmo genético
best_solution = population[0]


# Definir os parâmetros da rede com base na melhor solução encontrada
hidden_units = int(best_solution[0])
dense = best_solution[1]
learning_rate = best_solution[2]
num_epochs = int(best_solution[3])

print(hidden_units, dense, learning_rate, num_epochs)

from tensorflow.keras.optimizers import Adam
model = Sequential()
model.add(LSTM(hidden_units, return_sequences=True, input_shape=(treinamento_x.shape[1], 1)))
model.add(LSTM(hidden_units, return_sequences=True))
model.add(LSTM(hidden_units))
model.add(Dense(dense))
model.add(Dense(1))

treinamento_x.shape[1]

#model.compile(optimizer = "adam", loss = "mean_squared_error")
model.compile(loss='mean_squared_error', optimizer=Adam(learning_rate=learning_rate))
model.fit(treinamento_x, treinamento_y, batch_size=64, epochs=100)

dados_teste = dadosMinMax[tamanho_dados_treinamento - dias_previsao: , :]

teste_x = []
teste_y = cotacao[tamanho_dados_treinamento:, :]

for i in range(dias_previsao, len(dados_teste)):
    teste_x.append(dados_teste[i-dias_previsao: i, 0])

teste_x = np.array(teste_x)
teste_x = teste_x.reshape(teste_x.shape[0], teste_x.shape[1])

predicoes = model.predict(teste_x)

predicoes = escalador.inverse_transform(predicoes)

predicoes

# Cálculo do RMSE
rmse = np.sqrt(np.mean((predicoes - teste_y) ** 2))


# Cálculo do MSE
mse = np.mean((predicoes - teste_y) ** 2)

# Cálculo do R²
media_y = np.mean(teste_y)
ss_total = np.sum((teste_y - media_y) ** 2)
ss_residual = np.sum((predicoes - teste_y) ** 2)
r2 = 1 - (ss_residual / ss_total)

# Cálculo do MAPE
mae = np.mean(np.abs(predicoes - cotacao[tamanho_dados_treinamento:, :]))

print("RMSE:", rmse)
print("MSE:", mse)
print("R²:", r2)
print("MAE:", mae)

treinamento = dados.iloc[:tamanho_dados_treinamento, :]

df_teste = pd.DataFrame({"Close": dados['Close'].iloc[tamanho_dados_treinamento:],
                        "predicoes": predicoes.reshape(len(predicoes))})

plt.figure(figsize =(16, 8))

plt.title("Modelo")

plt.xlabel('Data', fontsize = 18)

plt.ylabel("Preço de fechamento", fontsize = 18)
plt.plot(treinamento['Close'])

plt.plot(df_teste[['Close', 'predicoes']])
plt.legend(['Treinamento', 'Real', 'Predições'], loc=2, prop={"size":16})

plt.show()

import matplotlib.pyplot as plt

# Dados de treinamento
treinamento = dados.iloc[:tamanho_dados_treinamento, :]

# Dados de teste (real e previsões)
df_teste = pd.DataFrame({"Close": dados['Close'].iloc[tamanho_dados_treinamento:],
                        "predicoes": predicoes.reshape(len(predicoes))})

plt.figure(figsize=(16, 8))
plt.title("Modelo")
plt.xlabel('Data', fontsize=18)
plt.ylabel("Preço de fechamento", fontsize=18)

# Plota apenas os dados reais em laranja e as previsões em verde
plt.plot(df_teste['Close'], color='orange', label='Real')
plt.plot(df_teste['predicoes'], color='green', label='Predições')

plt.legend(loc=2, prop={"size": 16})
plt.show()

df_teste.sort_index()

df_teste

#Previsao do dia seguinte
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np

data_hoje = datetime.now()

if data_hoje.hour > 18:
    final = data_hoje
    inicial = datetime.now() - timedelta(days=252)
else:
    final = data_hoje - timedelta(days=1)
    inicial = datetime.now() - timedelta(days=252)

cotacoes = yf.download(ativo, start=inicial, end=final)

ultimos_60_dias = cotacoes['Close'].iloc[-60:].values.reshape(-1, 1)

ultimos_60_dias_escalado = escalador.transform(ultimos_60_dias)

teste_x = []
teste_x.append(ultimos_60_dias_escalado)
teste_x = np.array(teste_x)
teste_x = teste_x.reshape(teste_x.shape[0],teste_x.shape[1])

previsao_de_preco = model.predict(teste_x)
previsao_de_preco = escalador.inverse_transform(previsao_de_preco)

print(previsao_de_preco)
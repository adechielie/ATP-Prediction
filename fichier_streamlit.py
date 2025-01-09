import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import  confusion_matrix
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Lire les données .csv
df2009=pd.read_csv("atp_matches_2009.csv")
df2010=pd.read_csv("atp_matches_2010.csv")
df2011=pd.read_csv("atp_matches_2011.csv")
df2012=pd.read_csv("atp_matches_2012.csv")
df2013=pd.read_csv("atp_matches_2013.csv")
df2014=pd.read_csv("atp_matches_2014.csv")
df2015=pd.read_csv("atp_matches_2015.csv")
df2016=pd.read_csv("atp_matches_2016.csv")
df2017=pd.read_csv("atp_matches_2017.csv")
df2018=pd.read_csv("atp_matches_2018.csv")
df2019=pd.read_csv("atp_matches_2019.csv")
df2020=pd.read_csv("atp_matches_2020.csv")
df=pd.read_csv("atp_matches_2016.csv")
df1=pd.read_csv("atpdata_github.csv")
df2=pd.read_csv("temp_newyork.csv")
df3=pd.read_csv("temp_paris.csv")
dfinal = pd.read_csv("merged_atpdatafinal_filtered.csv")
new_data = pd.read_csv("New_data.csv")


# Créer trois pages
st.title("Projet de prédiction de résultat sur un match de tennis ATP")
st.sidebar.title("Sommaire")
pages=["Introduction","Collecte des données","DataVizualization","Préparation des données","Modélisation","Conclusion"]
page=st.sidebar.radio("Aller vers", pages)

if page == pages[0] : 
  st.write("### Introduction")
  st.markdown("<p style='font-size: 14px;'> L'objetcif de ce projet est de créer un algorithme permettant de prédire l'issue d'un match de tennis du circuit ATP. Pour cela nous disposons d'une compilation sur plusieurs années de données de résultats de matchs faites par Jeff SACKMAN et disponible sur le site github.com.</p>", unsafe_allow_html=True)
  st.write("### Afficher les données de matchs de Jeff SACKMAN obtenues sur github")
  st.dataframe(df1.head(10))
  st.write(df1.shape)

  st.write("### Afficher les différentes variables des données et leur type")
  st.dataframe(df1.dtypes)

  st.write("### Afficher une description des variables numériques")
  colonnes_float = df1.select_dtypes(include=['float'])
  st.dataframe(colonnes_float.describe())

  if st.checkbox("Afficher les NA") :
     st.dataframe(df1.isna().sum())

if page == pages[1] : 
  st.write("### Collecte des données des matchs")
  st.write("### Choisir l'année et afficher le dataframe correspondant sur github avec les résultats de matchs")

  
  choix = ['2009', '2010', '2011', '2012','2013','2014','2015','2016','2017','2018','2019','2020']
  option = st.selectbox("Choix de l'année", choix)
  st.write("L'année choisie est :", option)

  def choix(an):
   if an == '2009':
     st.dataframe(df2009.head(10))
     st.write(df2009.shape)
   elif an == '2010':
     st.dataframe(df2010.head(10))
     st.write(df2010.shape)
   elif an == '2011':
     st.dataframe(df2011.head(10))
     st.write(df2011.shape)
   elif an == '2012':
     st.dataframe(df2012.head(10))
     st.write(df2012.shape)
   elif an == '2013':
     st.dataframe(df2013.head(10))
     st.write(df2013.shape)
   elif an == '2014':
     st.dataframe(df2014.head(10))
     st.write(df2014.shape)
   elif an == '2015':
     st.dataframe(df2015.head(10))
     st.write(df2015.shape)
   elif an == '2016':
     st.dataframe(df2016.head(10))
     st.write(df2016.shape)
   elif an == '2017':
     st.dataframe(df2017.head(10))
     st.write(df2017.shape)
   elif an == '2018':
     st.dataframe(df2018.head(10))
     st.write(df2018.shape)
   elif an == '2019':
     st.dataframe(df2019.head(10))
     st.write(df2019.shape)
   elif an == '2020':
     st.dataframe(df2020.head(10))
     st.write(df2020.shape)
   return an
  
  an = choix(option)
 
  
  st.write("### Afficher le dataframe de 'climate.org' contenant des données climatiques des 4 villes des grands chelem ") 
  choix2 = ['New-york', 'Paris', 'Melbourne', 'Londres']
  option2 = st.selectbox("Choix de la ville", choix2)
  st.write("La ville choisie est :", option2)

  def choix2(ville):
   if ville == 'New-york':
     st.dataframe(df2.head(10))
     st.write(df2.shape)
   elif ville == 'Paris':
     st.dataframe(df3.head(10))
     st.write(df3.shape)
   return ville
  
  ville = choix2(option2)


if page == pages[2] : 
  st.write("### DataVizualization")

  st.write("### Afiicher les 100 premiers tournois les plus représentés")
  tourney_counts = df1['tourney_name'].value_counts()

  # Sélectionnez les 100 premiers joueurs
  top_100_tourneys = tourney_counts.head(100)

  fig = plt.figure(figsize=(20, 12))  # Ajustez la taille si nécessaire
  top_100_tourneys.plot(kind='bar', color='skyblue')

  # Ajoutez des labels et un titre
  plt.xlabel('Nom du tournoi')
  plt.ylabel('Nombre')
  plt.title('Répartition des 100 premiers tournois les plus représentés')

  st.pyplot(fig)

  st.write("### Afiicher la répartition des victoires par nationalité")
  winner_ioc_counts = df1['winner_ioc'].value_counts()

  # Sélectionnez les 20 premières nationalités (ajustez si nécessaire)
  top_20_winner_ioc = winner_ioc_counts.head(20)

  # Créez un diagramme en barres
  fig = plt.figure(figsize=(20, 10))  # Ajustez la taille si nécessaire
  top_20_winner_ioc.plot(kind='bar', color='skyblue')

  # Ajoutez des labels et un titre
  plt.xlabel('Code IOC du gagnant')
  plt.ylabel('Nombre de victoires')
  plt.title('Répartition des victoires par nationalité (IOC)') 
  st.pyplot(fig)


  st.write("### Afficher le nombre victoire par surface en fonction du joueur")
  choix3 = ['Roger Federer', 'Rafael Nadal', 'Gael Monfils', 'Gilles Simon', 'Daniil Medvedev', 'Marco Cecchinato']
  option3 = st.selectbox("Choix du joueur", choix3)
  st.write("Le joueur choisi est :", option3)

  # Filtrer les matchs par joueur via une fonction
  def choix4(player_name):
    return df1[df1['winner_name'] == player_name]
  
  player_wins = choix4(option3)

  # Tracer la répartition des victoires par tournoi

  # Comptez le nombre d'occurrences de victoires par surface
  player_wins_by_tourney = player_wins['tourney_name'].value_counts()

  # Créez un diagramme en barres
  fig = plt.figure(figsize=(10, 6))
  player_wins_by_tourney.plot(kind='bar', color='skyblue')


  # Ajouter des labels et un titre
  plt.xlabel('Nom du tournoi')
  plt.ylabel('Nombre de victoires')
  plt.title('Répartition des victoires du joueur par tournoi')
  st.pyplot(fig) 

  st.write("### Afficher la relation entre les défaites et le nombre d'ace dans le match")
  choix9 = ['Roger Federer', 'Rafael Nadal', 'Gael Monfils', 'Gilles Simon', 'Daniil Medvedev', 'Marco Cecchinato']
  option9 = st.selectbox("Choisir le joueur", choix9)
  st.write("Le joueur choisi est :", option9)

  # Filtrer les matchs par joueur via une fonction
  def choix9(player_name):
    return df1[df1['loser_name'] == player_name]
    
  player_loss = choix9(option9)

  # Créer un scatter plot avec une ligne de tendance
  fig = plt.figure(figsize=(10, 6))
  sns.regplot(x='l_ace', y=player_loss.index, data=player_loss, scatter_kws={'color': 'skyblue'}, line_kws={'color': 'orange'})

  # Ajouter des labels et un titre
  plt.xlabel('Nombre d\'aces')
  plt.ylabel('Index du match')
  plt.title('Relation entre les défaites et le nombre d\'aces par match')
  st.pyplot(fig) 


if page == pages[3] : 
  
  st.write("### Préparation des données")

  st.write("### *Sélection des tournois et suppression des valeurs manquantes")

  st.markdown("<p style='font-size: 14px;'> -Liste des tournois retenus.</p>", unsafe_allow_html=True)
  st.markdown("<p style='font-size: 14px;'>  tournois_autorises = ['Roland Garros','Wimbledon','US Open','Australian Open','Halle', 'Queen\'s Club', 'Washington', 'Barcelona', 'Monte Carlo Masters', 'Indian Wells Masters', 'Cincinnati Masters', 'Canada Masters', 'Miami Masters', 'Paris Masters', 'Rome Masters', 'Madrid Masters'].</p>", unsafe_allow_html=True)

  st.markdown("<p style='font-size: 14px;'> - Filtrer le DataFrame pour inclure uniquement les tournois retenus : atpdatanew3 = atpdatanew3[atpdatanew3['tourney_name'].isin(tournois_autorises)].</p>", unsafe_allow_html=True)

  st.markdown("<p style='font-size: 14px;'> - Enlever les valeurs manquantes : atpdatafinal = atpdatanew3.dropna().</p>", unsafe_allow_html=True)

  st.write("### *Définition de la variable cible")

  st.markdown("<p style='font-size: 14px;'> merged_atpdatafinal['result'] = np.where(merged_atpdatafinal['result'] == merged_atpdatafinal['P1'], 1, merged_atpdatafinal['result']) .</p>", unsafe_allow_html=True)
  
  st.markdown("<p style='font-size: 14px;'> merged_atpdatafinal['result'] = np.where(merged_atpdatafinal['result'] == merged_atpdatafinal['P2'], -1, merged_atpdatafinal['result']) .</p>", unsafe_allow_html=True)

  st.write("### *Sélection des joueurs ayant au moins 10 matchs joués dans le jeu de données")

  st.markdown("<p style='font-size: 14px;'> - selected_players = counts[counts >= 10].index.</p>", unsafe_allow_html=True)

  st.write("### *Création d'une copie du dataframe pour répartir les valeur entre P1 et P2")

  st.markdown("<p style='font-size: 14px;'> - copie_atpdatafinal = atpdatafinal.copy().</p>", unsafe_allow_html=True)

  st.write("### *Calcul des moyennes des statistiques du joueur sur ses 5 précédents matchs")

  st.markdown("<p style='font-size: 14px;'> - for col in colonnes_moyenne: merged_atpdatafinal_filtered[f'{col}_moy'] = merged_atpdatafinal_filtered.groupby('P1')[col].rolling(window=5, min_periods=1).mean().reset_index(level=0, drop=True).</p>", unsafe_allow_html=True)

 


if page == pages[4] : 
  st.write("### Modélisation")
  
  st.write("### Afficher le nom du joueur choisi pour la modélisation")
  choix5 = ['Roger Federer', 'Rafael Nadal', 'Gael Monfils', 'Gilles Simon', 'Daniil Medvedev', 'Marco Cecchinato']
  option5 = st.selectbox("Choix du joueur", choix5)
  st.write("Le joueur choisi est :", option5)

  def filter_by_player(df, player_name):
   return df[(df['P1'] == player_name) | (df['P2'] == player_name)]
  
  filtered_atpdf = filter_by_player(dfinal, option5)
  st.dataframe(dfinal.head(20))

  
  # Colonnes catégorielles
  cat = ['tourney_name', 'surface', 'tourney_level', 'P1', 'P1_hand', 'P1_ioc',
       'P2', 'P2_hand', 'P2_ioc', 'round']

  # Utiliser get_dummies pour encoder ces colonnes
  filtered_atpdf_encoded = pd.get_dummies(filtered_atpdf, columns=cat)

  #Séparation des données explicatives de la variable cible
  feats = filtered_atpdf_encoded.drop('result', axis=1)
  target = filtered_atpdf_encoded['result']

  scaler = StandardScaler()
  feats = scaler.fit_transform(feats)


  st.write("### Afficher le nom du modèle choisi pour la prédiction")
  choix6 = ['KNC', 'Logistic Regression']
  option6 = st.selectbox('Choix du modèle', choix6)
  st.write('Le modèle choisi est :', option6)

  if option6 == 'Logistic Regression':
    nom_de_famille = option5.split()[-1]
    model_name = nom_de_famille+'_lrg'

    lrg = joblib.load(model_name)
    # Effectuer des prédictions
    predictions = lrg.predict(feats)

    if st.checkbox("Afficher le diagramme d'importance des variables") :
      # Récupérer les coefficients
      coefficients = lrg.coef_[0]

      # Obtenir les indices des coefficients positifs
      positive_indices = np.where(coefficients > 0)[0]

      # Limiter le nombre de variables à afficher
      top_indices = positive_indices[:50]

      # Extraire les noms des variables correspondantes
      top_variables = feats.columns[top_indices]

      # Extraire les coefficients correspondants
      top_coefficients = coefficients[top_indices]

      # Créer le graphique à barres
      fig = plt.figure(figsize=(12, 8))
      plt.bar(top_variables, top_coefficients, color='skyblue')
      plt.xlabel('Coefficient Value')
      plt.title('Top Positive Coefficients - Logistic Regression')
      plt.xticks(rotation=45)  # Pour faire pivoter les étiquettes sur l'axe x si nécessaire
      st.pyplot(fig)

    def scores(choice):
     if  choice == 'Accuracy':
      return accuracy_score(target, predictions)
     elif choice == 'Confusion matrix':
      return confusion_matrix(target, predictions)
   
    choix7 = ['Accuracy', 'Confusion matrix']
    option7 = st.selectbox('Quel indicateur souhaitez vous voir?', choix7)
    st.write("L'indicateur choisi est :", option7)

    result = scores(option7)
    st.write("Résultat :", result)

    
  elif option6 == 'KNC':
    nom_de_famille = option5.split()[-1]
    model_name = nom_de_famille+'_knc'
    knc = joblib.load(model_name)

    # Effectuer des prédictions
    feats_contiguous = np.ascontiguousarray(feats)
    predictions2 = knc.predict(feats_contiguous)


    def scores(choice):
     if  choice == 'Accuracy':
      return accuracy_score(target, predictions2)
     elif choice == 'Confusion matrix':
      return confusion_matrix(target, predictions2)
   
    choix8 = ['Accuracy', 'Confusion matrix']
    option8 = st.selectbox('Quel indicateur souhaitez vous voir?', choix8)
    st.write("L'indicateur choisi est :", option8)

    result = scores(option8)
    st.write("Résultat :", result)


if page == pages[5] : 
  st.write("### Conclusion")

  st.markdown("<p style='font-size: 14px;'>Au terme de ce projet, nous avons grâce à nos deux modèles, KNC et LogisticRegression, réussi à prédire la victoire ou défaite d'un joueur à l'issue d'un match de tennis. Nous devons considéré un modèle spécifique pour chaque joueur et entrainé le modèle avec les données spécifiques au joueur car chaque joueur a des statistiques et un profil particulier. Il est donc difficile d'avoir des résultats fiables en entrainant un modèle avec des données générales de tous les joueurs puis en l'appliquant sur des joueurs particuliers.  .</p>", unsafe_allow_html=True)
  st.markdown("<p style='font-size: 14px;'>Nous obtenons de meilleurs résultats avec le modèle KNC et nous pouvons également conclure que la précision de notre modèle et son score augmente significativement avec les joueurs les plus performants. Il sera donc plus précis en prédisant les résultats des meilleurs joueurs et beaucoup moins précis pour les joueurs les moins performants. .</p>", unsafe_allow_html=True)
  st.markdown("<p style='font-size: 14px;'> Nous restons toutefois perplexe quant à l'impact négligeable des données climatiques sur nos résultats. il serait intéressant de creuser cette approche en écartant certaines varibales afin de mettre en lumière l'impact de ce facteur notamment sur les grands tournois qui se jouent généralement extérieurs.</p>", unsafe_allow_html=True)
  
  
  

  
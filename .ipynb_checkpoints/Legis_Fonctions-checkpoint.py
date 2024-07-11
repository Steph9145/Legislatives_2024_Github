import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display, HTML
import matplotlib.pyplot as plt
import folium
from folium.features import GeoJson, GeoJsonTooltip
import geopandas as gpd
from branca.element import Element

# Fonction pour afficher des messages plus esthétiques
def Tmess(message, Color='firebrick', Align='center', Size='14', Police='arial', Weight='normal', Style='italic'):
    max_line_length = 150  # Longueur maximale d'une ligne avant de sauter à la ligne suivante
    lines = []
    current_line = ""
    # Séparation du message en lignes en fonction de la longueur maximale
    for mot in message.split():
        if len(current_line + mot) <= max_line_length:
            current_line += mot + " "
        else:
            lines.append(current_line.strip())
            current_line = mot + " "
    # Ajoute la dernière ligne restante
    lines.append(current_line.strip())
    # Formatage du message avec les balises HTML appropriées
    formatted_lines = "<br>".join(lines)
    styled_message = '<div style="text-align: {};"><span style="font-weight: {}; font-style: {}; color: {}; font-size: {}pt; font-family: {};">{}</span></div>'.format(Align, Weight, Style, Color, Size, Police, formatted_lines)
    # Affichage du message formaté
    display(HTML(styled_message))
    
# _______________________________________________________ Lecture des informations du fichier _________________________________________ 
def infos_DF(DF):
    print("______________________________________________________________________________________________________________________")
    message = "Information du Fichier"
    Tmessage(message)
    display(DF.head(3))
    message = "le fichier contient {:.0f} lignes et {} colonnes".format(DF.shape[0],DF.shape[1])
    Text_message(message)
    print('')
    
    Tmessage("Statistiques descriptives du dataframe")
    # Calcul des statistiques descriptives
    unique= DF.nunique()
    Count = DF.count()
    moy = round((DF.mean()),3)
    med = DF.median() 
    std = round((DF.std()),3)
    mini = DF.min()
    maxi = DF.max()
    valeurs_manquantes = DF.isnull().sum()
    dtype = DF.dtypes
    
    # Création du DataFrame de résumé statistique
    summary = pd.DataFrame({'Dtype' : dtype, 'Non-Null Count' : Count, 'Valeurs unique' : unique, 'moyennes': moy,
                            'medianes': med, 'ecart_types': std, 'min': mini, 'max': maxi,
                            'Valeurs manquantes': valeurs_manquantes,
                            'Valeurs manquantes%' : round((valeurs_manquantes/DF.shape[0])*100,2)})
    display(summary)
    
    # Détection des doublons
    Tmessage('Vérification des doublons')
    # Vérification des doublons dans le DataFrame
    doublons = DF[DF.duplicated(keep=False)]
    # Affichage des lignes qui sont des doublons
    display(doublons)
    if doublons.shape[0] == 0:
        Text_message("Absence de doublons dans le Dataframe")
    else:
        Text_message("Le Dataframe contient {} doublon(s)".format(doublons.shape[0]))
        

# _______________________________________________________ Classement des listes par le score Législatives _________________________________________ 
def top_Nb_listes(data, Nb_Lists= 19):
    # Création des listes des colonnes de voix et des listes correspondantes
    voix_columns = [col for col in data.columns if col.startswith("Candidat") and col.endswith("_RapportExprimes")]
    VIns_columns = [col for col in data.columns if col.startswith("Candidat") and col.endswith("_RapportInscrits")]
    NbVoix_columns = [col for col in data.columns if col.startswith("Candidat") and col.endswith("_NbVoix")]
    Parti_columns = [col for col in data.columns if col.startswith("Candidat") and col.endswith("_LibNuaCand")]
    Listes_columns = [col for col in data.columns if col.startswith("Candidat") and col.endswith("_CodNuaCand")]
    Civ_Candidat = [col for col in data.columns if col.startswith("Candidat") and col.endswith("_CivilitePsn")]
    Nom_Candidat = [col for col in data.columns if col.startswith("Candidat") and col.endswith("_NomPsn")]
    Prenom_Candidat = [col for col in data.columns if col.startswith("Candidat") and col.endswith("_PrenomPsn")]

    # Vérification que les colonnes existent
    assert all(col in data.columns for col in voix_columns), "Certaines colonnes de voix sont manquantes dans le DataFrame."
    assert all(col in data.columns for col in VIns_columns), "Certaines colonnes de voix/inscrits sont manquantes dans le DataFrame."
    assert all(col in data.columns for col in Listes_columns), "Certaines colonnes de listes sont manquantes dans le DataFrame."
    assert all(col in data.columns for col in Civ_Candidat), "Certaines colonnes de civilité sont manquantes dans le DataFrame."
    assert all(col in data.columns for col in Nom_Candidat), "Certaines colonnes de noms sont manquantes dans le DataFrame."
    assert all(col in data.columns for col in Prenom_Candidat), "Certaines colonnes de prénoms sont manquantes dans le DataFrame."

    # Fonction pour classer les "Nb_Lists" listes ayant obtenues le plus de voix (Par circonscription)
    def Top_Listes(row):
        # Combiner les listes et les voix en paires
        votes_result = [(row[Listes], row[Voix], row[VIns], row[Nbvoix], row[Parti], row[Civil], row[Nom], row[Prenom]) 
                        for Listes, Voix, VIns, Nbvoix, Parti, Civil, Nom, Prenom 
                        in zip(Listes_columns, voix_columns, VIns_columns, NbVoix_columns, Parti_columns, Civ_Candidat, Nom_Candidat, Prenom_Candidat)]
        # Trier les %votes par ordre décroissant et prendre les 'Nb_Lists' premiers
        top_Nb = sorted(votes_result, key=lambda x: x[1], reverse=True)[:Nb_Lists]
        # Réorganiser pour l'alternance Liste, %Voix, Nom et Prénom
        alternated = []
        for Listes, Voix, VIns, Nbvoix, Parti, Civil, Nom, Prenom in top_Nb:
            alternated.extend([Listes, Parti, Civil, Nom, Prenom, Nbvoix, Voix, VIns])
        return pd.Series(alternated)
 
    # Appliquer la fonction sur le DataFrame
    top_Nb_results = data.apply(Top_Listes, axis=1)

    # Générer les noms des colonnes alternées (Liste, Civilité, Nom, Prénom, Voix Exp, % Voix Exp, % Voix Ins)
    column_names = []
    for i in range(Nb_Lists):
        column_names.append(f'Liste{i+1}')
        column_names.append(f'Parti{i+1}')
        column_names.append(f'Civilité{i+1}')
        column_names.append(f'Nom{i+1}')
        column_names.append(f'Prénom{i+1}')
        column_names.append(f'Voix Exp {i+1}')
        column_names.append(f'% Voix Exp {i+1}')
        column_names.append(f'% Voix Ins {i+1}')
    top_Nb_results.columns = column_names

    # Conserver les 18 premières colonnes du DataFrame original
    columns_conserve = data.iloc[:, :18]

    # Concaténer les résultats
    Resultat = pd.concat([columns_conserve, top_Nb_results], axis=1)

    return Resultat

# ________________________________________ Fonction pour assigner des couleurs en fonction des valeurs de 'Elu' _______________________________ 
def style_function(feature):
    en_tete = feature['properties']['Elu']
    colors = {
        'RN': '#1C097F', # Bleu très foncé
        'UG': '#E00000', # Rouge 
        'ENS': '#FF9A1F', # Brun
        'LR': '#6870A7', # Bleu
        'DVD': '#6870A7', # Bleu
        'UXD': '#230B9A', # Bleu foncé
        'EXD': '#0B0044', # Noir
        'REG': '#E8E37B', # Jaune
        'DVG': '#D73B3B', # Rose
        'SOC': '#CD426C', # Rose
        'HOR': '#CEA345', # Orange
        'UDI': '#A35F0B', # Orange
        'DVD': '#545B89', # Bleu
        'ECO': '#1FFF3D', # Vert
        'DVC': '#AA783B', # Vert
    }
    return {
        'fillColor': colors.get(en_tete, '#ffffff'),  # Couleur par défaut blanche si non trouvée
        'fillOpacity': 1, 
        'color': 'black',
        'weight': 0.5,
        'dashArray': None
    }
# _______________________________________ Fonction pour assigner des couleurs en fonction des valeurs de 'Elu' 1er Tour _______________________________      
def style_function1erT(feature):
    Elu = feature['properties']['Elu']
    colors = {
        'RN': '#1D02A7', # Bleu très foncé
        'Union des Gauche': '#E00000', # Rouge 
        'Renaissance-Ensemble': '#FF9A1F', # Violet
        'Union Ext Droite': '#6243FF', # Bleu foncé
        'Extrême Droite': '#0B0044', # Noir
        'Régionaliste': '#E8E37B', # Jaune
        'Divers Gauche': '#D73B3B', # Rose
        'Parti Socialiste': '#CD426C', # Rose
        'Horizons': '#CEA345', # Violet
        'Divers Centre': '#3C1CDB', # Bleu
    }
    return {
        'fillColor': colors.get(Elu, '#ffffff'),  # Couleur par défaut blanche si non trouvée
        'fillOpacity': 1, 
        'color': 'black',
        'weight': 0.5,
        'dashArray': None
    }


# ___________________________________________ Fonction pour centrer la carte sur une région spécifique ___________________________________
def Carte_Result(geo_df,Zoom=6):

    # Calculer le centroid de la région pour centrer la carte
    centroid = geo_df.geometry.centroid.unary_union.centroid
    center_lat, center_lon = centroid.y, centroid.x

    # Créer la carte centrée sur la région
    m = folium.Map(location=[center_lat, center_lon], zoom_start=Zoom, tiles='Stamen Terrain')
    #m = folium.Map(location=[46.60, 1.89], zoom_start=Zoom, tiles='Stamen Terrain', width=800, height=800)
    
    # Ajouter les données géographiques à la carte
    geojson = GeoJson(
        geo_df,
        style_function=style_function,
        tooltip=GeoJsonTooltip(
            fields=['nomDepartement', 'codeCirconscription', 'Elu', '% Votes','Civ','Nom','Prenom','Second'],
            #aliases=['Département: ', 'Circonscription: ', 'Liste1: ', 'Votes (%): ', 'Liste2: ', 'Votes (%): ', 'Liste3: ', 'Votes (%): '],
            aliases=['Département: ', 'Circonscription: ', 'Elu: ', 'Votes (%): ', 'Civ: ', 'Nom: ', 'Prénom: ', 'Second'],
            localize=True
        )
    ).add_to(m)

    return m

# ___________________________________________ Fonction pour centrer la carte sur une région spécifique ___________________________________
def Carte_Resultats(geo_df, Resultats_Visuel, Zoom=6, sauv='off'):

    # Liste des partis
    Partis = ['RN', 'UXD', 'EXD', 'LR', 'DVD', 'ENS', 'HOR', 'UDI', 'DVC', 'DIV', 'UG', 'DVG', 'SOC', 'ECO', 'REG']
    
    # Dictionnaire pour stocker les compteurs de sièges
    counts = {}

    # Calculer les sièges pour chaque parti
    for parti in Partis:
        counts[parti] = (Resultats_Visuel["Elu"] == parti).sum()

    # Calculer le centroid de la région pour centrer la carte
    centroid = geo_df.geometry.centroid.unary_union.centroid
    center_lat, center_lon = centroid.y, centroid.x

    # Créer la carte centrée sur la région
    m = folium.Map(location=[center_lat, center_lon], zoom_start=Zoom, tiles='Stamen Terrain')
    
    # Ajouter les données géographiques à la carte
    geojson = GeoJson(
        geo_df,
        style_function=style_function,
        tooltip=GeoJsonTooltip(
            fields=['nomDepartement', 'codeCirconscription', 'Elu', '% Votes','Civ','Nom','Prenom','Second'],
            #aliases=['Département: ', 'Circonscription: ', 'Liste1: ', 'Votes (%): ', 'Liste2: ', 'Votes (%): ', 'Liste3: ', 'Votes (%): '],
            aliases=['Département: ', 'Circonscription: ', 'Elu: ', 'Votes (%): ', 'Civ: ', 'Nom: ', 'Prénom: ', 'Second'],
            localize=True
        )
    ).add_to(m)

    # Création de la légende
    legend_html = '''
    <div style="
        position: fixed; 
        bottom: 50px; 
        left: 30px; 
        width: 150px; 
        height: auto; 
        border:2px solid grey; 
        z-index:9999; 
        font-size:12px;
        background-color:white; 
        opacity: 0.8;
        padding: 10px;
    ">
    <b>Légende</b><br>
    <b></b><br>
    <i style="background: #1C097F; width: 18px; height: 18px; display: inline-block;"></i> RN<br>
    <i style="background: #230B9A; width: 18px; height: 18px; display: inline-block;"></i> Union Ext Droite<br>
    <i style="background: #0B0044; width: 18px; height: 18px; display: inline-block;"></i> Extrême Droite<br>

    <i style="background: #6870A7; width: 18px; height: 18px; display: inline-block;"></i> LR<br>
    <i style="background: #6870A7; width: 18px; height: 18px; display: inline-block;"></i> DVD<br>
    <i style="background: #FF9A1F; width: 18px; height: 18px; display: inline-block;"></i> Ensemble<br>
    <i style="background: #C76F03; width: 18px; height: 18px; display: inline-block;"></i> HOR<br>
    <i style="background: #A35F0B; width: 18px; height: 18px; display: inline-block;"></i> UDI<br>
    <i style="background: #AA783B; width: 18px; height: 18px; display: inline-block;"></i> DVC<br>
    <i style="background: #E00000; width: 18px; height: 18px; display: inline-block;"></i> Union des Gauche<br>
    <i style="background: #D73B3B; width: 18px; height: 18px; display: inline-block;"></i> DVG<br>
    <i style="background: #CD426C; width: 18px; height: 18px; display: inline-block;"></i> SOC<br>
    <i style="background: #1FFF3D; width: 18px; height: 18px; display: inline-block;"></i> ECO<br>
    <i style="background: #E8E37B; width: 18px; height: 18px; display: inline-block;"></i> Régionaliste<br>
    </div>
    '''
    # Ajout de la légende à la carte en tant qu'élément HTML
    legend_element = Element(legend_html)
    m.get_root().html.add_child(legend_element)

    # Créer le HTML pour le titre
    title_html = '''
    <h3 style="position: fixed; 
        top: 10px; 
        left: 50%; 
        transform: translateX(-50%);
        z-index:9999; 
        font-size:20px;
        background-color:white; 
        padding: 10px;
        border: 2px solid grey;
        opacity: 0.8;">
    Prévisions Résultats Législatives 2024
    </h3>
    '''
    # Ajouter le titre à la carte en tant qu'élément HTML
    title_element = Element(title_html)
    m.get_root().html.add_child(title_element)

    # Création de la note 'Résultats Nationaux par Listes' avec les compteurs
    note_html = '''
    <div style="
        position: fixed;
        bottom: 50px;
        right: 50px;
        width: 150px;
        height: auto;
        border:2px solid grey;
        z-index:9999; 
        font-size:14px;
        background-color:white; 
        opacity: 0.8;
        padding: 10px;">
    <b>Nb Sièges</b><br>
    <b></b><br>
    {}
    </div>
    '''.format('<br>'.join([f'{parti} : {count}' for parti, count in counts.items()]))

    # Ajout de la Note en tant qu'élément HTML
    note_element = Element(note_html)
    m.get_root().html.add_child(note_element)
    if sauv == 'on':
        m.save('Projections2tr_2024_Legis_circonscriptions.html')

    
    return m

# ___________________________________________ Fonction pour centrer la carte sur une région spécifique 1er TOUR  ___________________________________
def Carte_Results_1erT(geo_df, Resultats_Visuel, Zoom=6, sauv='off'):
    # Initialiser la carte centrée sur la France
    m = folium.Map(location=[46.60, 1.89], zoom_start=6, tiles='Stamen Terrain')

    # Ajouter les données géographiques à la carte
    geojson = GeoJson(
        geo_df,
        style_function=style_function1erT,
        tooltip=GeoJsonTooltip(
        fields=['Libellé département', 'codeCirconscription', 'Elu', '% Votes','Second','% Votes2','Troisième','% Votes3'],
        aliases=['Département: ', 'Circonscription: ', 'Elu: ', 'Votes (%): ', 'Liste2: ', 'Votes (%): ', 'Liste3: ', 'Votes (%): '],
        localize=True
        )
    ).add_to(m)
    # Création de la légende
    legend_html = '''
    <div style="
        position: fixed; 
        bottom: 50px; 
        left: 50px; 
        width: 200px; 
        height: auto; 
        border:2px solid grey; 
        z-index:9999; 
        font-size:14px;
        background-color:white; 
        opacity: 0.8;
        padding: 10px;
    ">
    <b>Légende</b><br>
    <b></b><br>
    <i style="background: #1D02A7; width: 18px; height: 18px; display: inline-block;"></i> RN<br>
    <i style="background: #E00000; width: 18px; height: 18px; display: inline-block;"></i> Union des Gauche<br>
    <i style="background: #FF9A1F; width: 18px; height: 18px; display: inline-block;"></i> Renaissance-Ensemble<br>
    <i style="background: #6243FF; width: 18px; height: 18px; display: inline-block;"></i> Union Ext Droite<br>
    <i style="background: #0B0044; width: 18px; height: 18px; display: inline-block;"></i> Extrême Droite<br>
    <i style="background: #E8E37B; width: 18px; height: 18px; display: inline-block;"></i> Régionaliste<br>
    </div>
    '''
    # Ajout de la légende à la carte en tant qu'élément HTML
    legend_element = Element(legend_html)
    m.get_root().html.add_child(legend_element)

    # Création de la note 'Résultats Nationaux par Listes'
    note_html = '''
    <div style="
        position: fixed;
        bottom: 50px;
        right: 100px;
        width: 250px;
        height: auto;
        border:2px solid grey;
        z-index:9999; 
        font-size:14px;
        background-color:white; 
        opacity: 0.8;
        padding: 10px;">
    RN & Unions:  33.14 %<br>
    Union des Gauches:  27.64 %<br>
    Ensemble / Renaissance:  21.88 %
    </div>
    '''
    # Ajout de la Note en tant qu'élément HTML
    note_element = Element(note_html)
    m.get_root().html.add_child(note_element)

    # Créer le HTML pour le titre
    title_html = '''
    <h3 style="position: fixed; 
        top: 10px; 
        left: 50%; 
        transform: translateX(-50%);
        z-index:9999; 
        font-size:20px;
        background-color:white; 
        padding: 10px;
        border: 2px solid grey;
        opacity: 0.8;">
    Prévisions Résultats 1er Tour
    </h3>
    '''

    # Ajouter le titre à la carte en tant qu'élément HTML
    title_element = Element(title_html)
    m.get_root().html.add_child(title_element)
    # Afficher la carte
    m.save('Projections_Results_Legis1Tour.html')
    
    return m

# _______________________________________________________ Classement des listes par le score Européennes _________________________________________ 
def TopList_Europ(data, Nb_Lists = 5):
    # Création des listes des colonnes de voix et des listes correspondantes
    voix_columns = [col for col in data.columns if col.startswith("% Voix/exprimés")]
    Listes_columns = ['Libellé abrégé de liste ' + col.split()[2] for col in voix_columns]

    # Vérification que les colonnes existent
    assert all(col in data.columns for col in voix_columns), "Certaines colonnes de voix sont manquantes dans le DataFrame."
    assert all(col in data.columns for col in Listes_columns), "Certaines colonnes de listes sont manquantes dans le DataFrame."

    # Fonction pour obtenir les 4 listes ayant obtenues le plus de voix
    def Top_Listes(row):
        # Combiner les listes et les voix en paires
        votes_result = [(row[Listes], row[Voix]) for Listes, Voix in zip(Listes_columns, voix_columns)]
        # Trier les %votes par ordre décroissant et prendre les 4 premiers
        top_4 = sorted(votes_result, key=lambda x: x[1], reverse=True)[:Nb_Lists]
        # Réorganiser pour l'alternance Liste, %Voix
        alternated = []
        for Listes, Voix in top_4:
            alternated.extend([Listes, Voix])
        return pd.Series(alternated)

    # Appliquer la fonction sur le DataFrame
    top_4_results = data.apply(Top_Listes, axis=1)

    # Générer les noms des colonnes alternées Parti, Voix
    column_names = []
    for i in range(len(top_4_results.columns) // 2):
        column_names.append(f'Liste{i+1}')
        column_names.append(f'% Voix Liste{i+1}')
    top_4_results.columns = column_names

    # Conserver les 18 premières colonnes du DataFrame original
    columns_conserve = data.iloc[:, :18]

    # Concaténer les résultats
    Resultat = pd.concat([columns_conserve, top_4_results], axis=1)

    # Sélection des colonnes numériques utilisant une expression régulière
    colonnes_numeriques = [col for col in Resultat.columns if col.startswith('% Voix Liste')]
    # Création de la colonne 'somme' en additionnant les valeurs des colonnes numériques
    Resultat['somme'] = Resultat[colonnes_numeriques].sum(axis=1)
    Resultat = Resultat.sort_values(by="somme", ascending=True)

    return Resultat


# ___________________________________________________ Classement des listes par le score Législatives 2022 _________________________________________ 
def top_Legis2022(data, Nb_Lists = 3,AN = 0):
    # Création des listes des colonnes de voix et des listes correspondantes
    voix_columns = [col for col in data.columns if col.startswith("%VOIX")]

    if AN != 22:
        voix_columns = [col for col in data.columns if col.endswith("% Voix/Exp") or col.startswith("%VOIX25% ")]
        
    # Fonction pour obtenir les Nb_Lists listes ayant obtenues le plus de voix
    def Top_Listes(row):
        # Création d'une liste de tuples (nom de colonne, valeur)
        votes_result = [(col, row[col]) for col in voix_columns if not pd.isna(row[col])]
        # Tri par valeur décroissante et sélection des 3 premiers
        top_n = sorted(votes_result, key=lambda x: x[1], reverse=True)[:Nb_Lists]
        # Extraire les noms de colonnes des 3 meilleurs
        top_n_colnames = [col for col, val in top_n]
        # Extraire les valeurs des 3 meilleurs
        top_n_values = [val for col, val in top_n]
        # Combiner les noms de colonnes et les valeurs dans un dictionnaire
        result = {}
        for i in range(Nb_Lists):
            result[f"Top_{i+1}_List"] = top_n_colnames[i]
            result[f"Top_{i+1}_%"] = top_n_values[i]
        return pd.Series(result)
       
    # Appliquer la fonction sur le DataFrame
    top_n_results = data.apply(Top_Listes, axis=1)

    # Conserver les 15 premières colonnes du DataFrame original
    columns_conserve = data.iloc[:, :18]

    # Concaténer les résultats
    Resultat = pd.concat([columns_conserve, top_n_results], axis=1)

    return Resultat
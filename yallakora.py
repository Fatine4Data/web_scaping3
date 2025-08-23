import requests
from bs4 import BeautifulSoup
import csv
date = input("entrer une date sous la forme de MM/DD/YYYY ")   
url=f"https://www.yallakora.com/match-center?date={date}"

def main():
        with requests.Session() as session:
            response = session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            resultats=[]

            try:
                 
                 championships = soup.find_all("div", class_="matchesList")

                 for champ in championships:
                      #recupere les nom des chanpions related a chaque date 
                      #Gérer les balises manquantes
                      titre_tag = champ.find("div", class_="title")
                      if titre_tag and titre_tag.find("a") and titre_tag.find("h2"):
                            titre = titre_tag.find("a").find("h2").text.strip()
                      else:
                            titre = "Titre introuvable"

                      

                      #recuper tous les matches de chaque championship
                      liste_matches=champ.find("div",class_="ul").find_all("div",class_="liItem")

                      #recuperer la data de chaque match 
                      if liste_matches:
                        for match in liste_matches :
                            match_data=match.find("a").find("div",class_="allData").find("div",class_="teamCntnr").find("div",class_="teamsData")

                                #les noms des teams
                            try:
                                    
                                    team_A = match_data.find("div", class_="teamA").find("p").text.strip()
                                    team_B = match_data.find("div", class_="teamB").find("p").text.strip()
                            except AttributeError:
                                    print("⚠️ Impossible de lire les données d’un match")
                                    continue
                            
                            #le temps du match 
                            match_time=match_data.find("div",class_="MResult").find("span",class_="time").text.strip()

                            #le score de chaque match 
                            score_tag = match_data.find("div", class_="MResult").find_all("span", class_="score")
                            if score_tag:
                                score_teama = score_tag[0].text.strip()
                                score_teamb=score_tag[1].text.strip()
                                match_score=f"{score_teama} - {score_teamb}"
                            else:
                                match_score = "Non joué"



                            resultats.append({
                                    "championship":titre,
                                    "team_A":team_A,
                                    "team_B":team_B,
                                    "time":match_time,
                                    "score":match_score                        
                                    
                            })

                      else:
                             print("Aucun match trouvé pour ce championnat :", titre)

                 with open("matches.csv","w",newline="",encoding="utf-8") as f:
                    colonnes=["championship","team_A","team_B","time","score"]
                    ecrivain=csv.DictWriter(f,fieldnames=colonnes)
                    ecrivain.writeheader()
                    ecrivain.writerows(resultats)
                      
                 print("✅ Données sauvegardées dans matches.csv")

            except requests.exceptions.RequestException as e:
                print("Erreur :", e)

if __name__ == '__main__':
    main()
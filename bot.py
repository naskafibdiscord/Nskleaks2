import os
import discord
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup

# Configuration des intents Discord
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Récupération des secrets depuis les variables d'environnement (Railway)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# URL de FiveVault (à adapter selon la page exacte des leaks ou de recherche)
FIVEVAULT_URL = "https://fivevault.net/" 

# Variable pour stocker la dernière ressource vue et éviter les doublons
dernier_lien_connu = None

@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user.name}")
    # Lancement de la tâche de vérification automatique (toutes les 30 minutes ici)
    verifier_nouvelles_ressources.start()

@tasks.loop(minutes=30)
async def verifier_nouvelles_ressources():
    global dernier_lien_connu
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("Salon introuvable !")
        return

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(FIVEVAULT_URL, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # --- EXEMPLE DE SCRAPING (À adapter selon le HTML exact de FiveVault) ---
        # On cherche la première ressource de la liste
        item = soup.select_one('.resource-card') # Remplace par la bonne classe CSS
        if not item:
            return

        titre = item.select_one('.title').text.strip()
        lien_ressource = item.select_one('a')['href']
        description = item.get_text() # Ou une description spécifique

        # Si c'est une nouvelle ressource qu'on n'a pas encore postée
        if lien_ressource != dernier_lien_connu:
            dernier_lien_connu = lien_ressource

            # Étape A : Télécharger le fichier et l'uploader sur GoFile (Simulation / API)
            # (Ici tu mets ta fonction de téléchargement du fichier source puis upload GoFile)
            lien_gofile = "https://gofile.io/d/exemple" # Remplacer par le retour de l'API GoFile

            # Étape B : Trouver une preview sur YouTube
            lien_youtube = chercher_youtube(titre)

            # Étape C : Construction du message Discord (identique à ton image)
            message_content = (
                f"📜 **Nouvel ajout — Script**\n"
                f"Une ressource a été ajoutée dans les leaks.\n\n"
                f"📄 **Contenu**\n"
                f"# Script\n\n"
                f"• 🎬 **Preview** : {lien_youtube}\n"
                f"• 💻 **Download** : {lien_gofile}\n\n"
                f"**Description**\n"
                f"{description[:300]}...\n\n"
                f"📁 **Type**\n"
                f"📜 **Script**\n"
                f"📅 **Date**\n"
                f"17/10/2026\n"
                f"📍 **Source**\n"
                f"# FiveVault"
            )

            await channel.send(message_content)

    except Exception as e:
        print(f"Erreur lors de la vérification : {e}")

def chercher_youtube(titre_ressource):
    """Recherche une vidéo YouTube correspondante via l'API Google"""
    if not YOUTUBE_API_KEY:
        return "https://youtube.com"
    
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={titre_ressource}&type=video&key={YOUTUBE_API_KEY}"
    try:
        res = requests.get(url).json()
        if "items" in res and len(res["items"]) > 0:
            video_id = res["items"][0]["id"]["videoId"]
            return f"https://youtu.be/{video_id}"
    except:
        pass
    return "Aucune preview trouvée"

# Lancement du bot
bot.run(DISCORD_TOKEN)

# PootBot

<p align="center">
  <img width="300" height="300" src="https://raw.githubusercontent.com/AhmetMuratAcar/PootBot/main/Images/PootBot%20Logo.webp">
</p>

## What is it
Quick lil discord bot for managing roles for the current flavor of the month game. Instead of @ing multiple people, allows user to @ a centralized role.

## How to Contribute
If for any reason you want to contribute. Feel free to make a pull request. Keep in mind that the bot is private on discord and currently hosted on the free tier of Oracle (OCI).

Clone the repository from GitHub and install the dependencies as so:
```
pip install -r requirements.txt
```

## Commands
Currently there are 2 commands:

```
/current-flavor
```
The bot tells you what the current flavor of the month game is.

```
/change-flavor name: <game title>
```
**First**: mentions the users that currently have the "Current Flavor" role to let them know the game is changing.  
**Second**: removes everyone from the role and sends a message containing a ✅ reaction.  
**Third**: if they are interested in the new game, users can add themselves to the "Current Flavor" role by clicking the ✅ reaction. Users can remove themselves from the role by removing their reaction.

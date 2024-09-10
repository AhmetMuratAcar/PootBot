# PootBot

<p align="center">
  <img width="300" height="300" src="https://raw.githubusercontent.com/AhmetMuratAcar/PootBot/main/Images/PootBot-Logo.png">
</p>

## What is it
Quick lil discord bot for managing roles for your server. Allows users to create and add roles to themselves.

## How to Contribute
If for any reason you want to contribute. Feel free to make a pull request. Keep in mind that the bot is private on discord and currently hosted on the free tier of Oracle (OCI). Since this is such a small scale project don't worry about managing any databases. All data is stored within 2 JSON files in the `/data` directory that is created.

Clone the repository from GitHub and install the dependencies as so:
```
pip install -r requirements.txt
```

## Commands
Currently there are 3 commands:

```
/setup_master_message [channel_name]
```
This command sets up the message that users will interact with to add/remove roles from themselves in your desired channel. I personally recommend setting up a text chat where users can do nothing but interact with the master message.

\* Note that admin privilages are required to use this command.
```
/add_role [role_name] [emoji]
```
This command adds the given desired role and emoji into the master message and adds a reaction to the master message with the given emoji. Interacting with this emoji adds/removes its respective role to the user.

```
/remove_role [role_name]
```
This command removes the given role and its respective emoji from the master message. The role is completely deleted from the server. It only works on roles in the master message.

\* Note that admin privilages are required to use this command.

## Example
<p align="center">
  <img width="641" height="355" src="https://raw.githubusercontent.com/AhmetMuratAcar/PootBot/main/Images/Example.webp">
</p>

This is how a master message with a few roles added looks. Note that it supports custom emojis that the bot has access to in your server.
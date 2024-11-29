# Voicebot

## What is it?
This is a Discord bot designed specifically for [Voicebox's Kingdom](https://discord.gg/pkbMEsJVwx), but I've released it to the public so anyone can use it.

## Features

### User Level
- [x] **AFK**
- [x] **Snipe** (s) and **Editsnipe** (es)
- [x] **Summoning**
- [x] **Summon List Management** 
- [ ] **Currency System**  
    - [x] Check balance
    - [x] Daily currency claim  
    - [x] Beg  
    - [x] Gambling  
    - [x] Wager (coin flip, dice)  
    - [ ] Robbing  
    - [ ] Heist  
    - [ ] Cash events  
    - [ ] Work  
    - [ ] Shop  
    - [ ] Trade  
    - [ ] Inventory
    - [ ] Bank
    - [ ] Fish

### Admin Level
- [x] **User Management**
- [x] **Clearsnipes** (cs)
- [x] **Currency Management**
- [x] **Pause**

### Owner Level
- [x] **Admin Management**
- [x] **Stop**

## Folder Structure
```
my_discord_bot/ 
├── bot.py
├── cogs/
│ ├── user/
│ │ ├── currency.py
│ │ ├── utility.py
│ ├── admin/
│ │ ├── init.py
│ │ ├── administration.py 
│ │ ├── currency.py
│ │ ├── utility.py
│ ├── owner/
│ │ ├── init.py
│ │ ├── owner.py 
├── data/
│ ├── summons.json
│ ├── user_ids.json
│ ├── currency.json
│ ├── inventory.json
│ ├── shop.json
│ ├── loottables.json
├── utils/
│ ├── helpers.py
├── requirements.txt
├── config.py
├── .gitignore
├── requirements.txt
├── LICENSE
└── README.md
```
## How to Use

1. **Clone the Repository**  
   Use the following command to clone the repository to your local machine:
   > `git clone https://github.com/JasonZhaoExp/VoiceBot`
2. **Install dependencies**
   Make sure you have python installed, then install the required packages using:
   > `pip install -r requirements.txt`
3. **Set up configuration**
   Create a `config.py` file in the root directory and add the following configuration variables:
   ```py
   TOKEN = "your_discord_bot_token"
   PREFIX = "your prefix"
   ```
4. **Run the bot**
   Run the bot using:
   `python bot.py`

## Contribution guidelines
- Ensure code is clean and well documented
- Use consistent naming conventions and folder structure
- Open a PR for new features or bug fixes.

## License
This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.

# Voicebot

## What is it?
This is a Discord bot designed specifically for [Voicebox's Kingdom](https://discord.gg/pkbMEsJVwx).

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
    - [x] Shop  
    - [ ] Trade  
    - [x] Inventory
    - [ ] Bank

### Admin Level
- [x] **User Management**
- [x] **Clearsnipes** (cs)
- [x] **Currency Management**
- [x] **Pause**

### Owner Level
- [x] **Admin Management**
- [x] **Stop**

## Folder Structure

my_discord_bot/ ├── bot.py
├── cogs/
│ ├── init.py
│ ├── user/
│ │ ├── init.py
│ │ ├── currency.py
│ │ ├── fun.py
│ │ ├── summoning.py
│ │ ├── utility.py
│ ├── admin/
│ │ ├── init.py
│ │ ├── administration.py │ │ ├── currency.py
│ ├── owner/
│ │ ├── init.py
│ │ ├── administration.py ├── data/
│ ├── summons.json
│ ├── user_ids.json
├── utils/
│ ├── init.py
│ ├── helpers.py
| ├── messagecache.py 
├── requirements.txt
├── config.py
└── README.md

## How to Use

1. **Clone the Repository**  
   Use the following command to clone the repository to your local machine:
   `bash git clone <repository_url>`
2. **Install dependencies**
   Make sure you have python installed, then install the required packages using:
   `pip install -r requirements.txt`
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
This project is licensed under the MIT License. See [LICENSE](LICENSE) for detail.
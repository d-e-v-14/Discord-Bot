# Discord Music & AI Bot

## Overview
This Discord bot provides music playback functionality and integrates the Gemini API for AI-powered responses. Users can control music playback in a voice channel and interact with the AI using simple commands. This bot utilizes the discord's library inorder to use the functions for creating the bot.

## Commands

### Music Commands
| Command | Description |
|---------|-------------|
| `/help` | Displays all available commands |
| `/p <keyword>` | Plays the song in your voice channel |
| `/q` | Displays the current music queue |
| `/skip` | Skips the currently playing song |
| `/clear` | Stops the music and clears the queue |
| `/leave` | Disconnects the bot from the voice channel |
| `/pause` | Pauses or resumes the song |
| `/resume` | Resumes playing the song |

### AI Commands
| Command | Description |
|---------|-------------|
| `$ <prompt>` | Sends a request to the Gemini API and returns a response |

## Gemini API Integration
This bot integrates the Gemini API to provide AI-powered responses in Discord channels. When a user types `$ <prompt>`, the bot sends the prompt to the Gemini API and returns the generated response.

### API Setup
1. Obtain an API key from [Gemini API](https://ai.google.dev/).
2. Store the API key securely in your bot's environment variables.
3. Use an HTTP request to send user prompts and receive responses.

```

## Installation & Usage
1. Install dependencies: `pip install discord requests`
2. Set up your environment variables (`DISCORD_BOT_TOKEN`, `GEMINI_API_KEY`).
3. Run the bot using `python bot.py`.
4. To Access the music, /<keyword><link>

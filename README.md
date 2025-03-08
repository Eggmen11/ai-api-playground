# AI-API-Playground

Welcome to `ai-api-playground`, my DIY lab for screwing around with OpenAI’s APIs. I’ve cooked up a real-time agent that chats via text or audio (because typing’s overrated), and a basic tool-calling agent that’s like my personal errand boy. It’s a work in progress, and I’m just here to see how far I can push this API nonsense.

## The Setup

Here’s the rundown, minus the boring junk:

```
.
├── LICENSE (legal vibes, whatever)
└── openai_agents
    ├── common
    │   ├── __init__.py (keeps things tidy)
    │   └── tools.py (weather tricks and such)
    ├── example_usage.py (the “test drive” script)
    ├── realtime_agent
    │   ├── realtime_agent.py (the live-action boss)
    │   └── tool_schemas.py (tool blueprints, very profesh)
    ├── requirements.txt (your shopping list)
    └── tool_calling_agent
        ├── simple_agent.py (the laid-back helper)
        └── tool_schemas.py (more tool specs)
```
- **`example_usage.py`**: Launchpad. Pick an agent and go wild.
- **`realtime_agent.py`**: The real deal—talks back in real-time with text or audio. Mic or keyboard, your call.
- **`simple_agent.py`**: Does the basics and grabs tools when I need it to stop slacking.
- **`tools.py`**: Weather tools live here, courtesy of OpenWeatherMap. Ask it about rain; it’s got you.

## How to Kick It Off

1. **Grab It**:
   - Clone this beast: `git clone https://github.com/yourusername/ai-api-playground.git`
   - Step in: `cd ai-api-playground`

2. **Prep the Goods**:
   - Python’s your friend (I’m on 3.12, but it’s chill).
   - Install the stash: `pip install -r requirements.txt`
   - Drop a `.env` file in the root with:
     ```
     OPENAI_API_KEY=your-openai-key
     OPENWEATHER_API_KEY=your-openweather-key
     ```
     **Pro Tip**: That OpenWeather key’s a must for weather tools (see `tools.py`). Snag one from [openweathermap.org](https://openweathermap.org), or the agents will just stare at you like “bro, really?”

3. **Run the Show**:
   - Hit it: `python openai_agents/example_usage.py`
   - Pick 1 for simple, 2 for real-time. Real-time mode lets you flex with text or audio input—smooth, right?

## What It’s Packing

- **Simple Agent**: Handles chit-chat and tools. Ask “What’s the weather?” and it’ll flex—if you’ve got the key.
- **Real-Time Agent**: The MVP. Text and audio replies, live. Throw it a mic rant or type; it’s unbothered either way.

## What’s Coming?

I’m still knee-deep in API land, so expect more chaos. New agents, slicker tools, maybe something that doesn’t crash for once. This is my sandbox, and I’m just getting warmed up.

## Props

- OpenAI for the brainpower behind this.
- OpenWeatherMap for the weather hookup (key required, don’t sleep on it).
- You, for peeking at this—drop a line if you’ve got thoughts.

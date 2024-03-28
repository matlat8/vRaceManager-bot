# vRaceManager
iRacing Discord bot geared towards analytics. 

## Road Map
**Team Statistics:** Track how your iRacing team is doing in offical series. Track series points, pos. gain/loss, iRating gain/loss and more.

**Weekly Time Trial League Manager**: Setup a hosted session in iRacing and have vRaceManager track all teammates lap times. At the end of the hosted session, team members get points depending on how fast they were that week compared to others.

## Planned Majors
> All items are subject to change

1.?.0 -> Weekly Time Trial League Manager

?.0.0 -> Migrate off supabase, using Neon.tech instead.

## Dev

.env file example

```
# discord information
DISCORD_TOKEN=
DISCORD_COMMAND_PREFIX=?

# backend db to store all data
SUPABASE_URL=https://{your url}.supabase.co
SUPABASE_KEY=

# used for iRacing API authentication
IRACING_USERNAME={this is your iracing email address}
IRACING_PASSWORD={iracing password}
```

-----
Join the racing team helping me develop and build out this bot and its capabilities. [PUR iRacing Community](https://discord.gg/BcK7hUuNcj)
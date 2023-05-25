const { Client, Intents, GatewayIntentBits, ActivityType, Guild } = require('discord.js');
const fs = require('fs');
const { REST } = require('@discordjs/rest');
const { Routes } = require('discord-api-types/v9');

//@xkawaimugi Load configuration from config.json
const config = require('./config/config.json');
const { clientId, guildIds, token, userId } = config;

const client = new Client({
  intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages],
});

async function setBotStatus(client, guildIds) {
  try {
    for (const guildId of guildIds) {
      const guild = await client.guilds.fetch(guildId);
      const user = guild.members.resolve(client.user.id);

      await client.user.setPresence({
        activities: [
          {
            name: 'mugi.me | /awoo',
            type: ActivityType.Playing
          }
        ],
        status: 'online'
      });

      console.log(`Bot status set successfully for guild: ${guildId}`);
    }
  } catch (error) {
    console.error('Failed to set bot status:', error);
  }
}

client.once('ready', () => {
  console.log(`Logged in as ${client.user.tag}!`);

  // Set the initial bot status
  setBotStatus(client, guildIds);
});

const rest = new REST({ version: '9' }).setToken(token);

(async () => {
  try {
    console.log('Started refreshing application (/) commands.');

    const commands = [];
    const commandFiles = fs.readdirSync('./commands').filter((file) => file.endsWith('.js'));

    for (const file of commandFiles) {
      const command = require(`./commands/${file}`);
      commands.push(command.data.toJSON());
    }

    for (const guildId of guildIds) {
      await rest.put(Routes.applicationGuildCommands(clientId, guildId), { body: commands });
      console.log(`Registered slash commands for guild: ${guildId}`);
    }

    console.log('Successfully registered application (/) commands.');
  } catch (error) {
    console.error('Failed to register application (/) commands:', error);
  }
})();

client.commands = new Map();
const commandFiles = fs.readdirSync('./commands').filter((file) => file.endsWith('.js'));
for (const file of commandFiles) {
  //commands @xkawaimugi
  const command = require(`./commands/${file}`);
  client.commands.set(command.data.name, command);
}

client.on('interactionCreate', async (interaction) => {
  if (!interaction.isCommand()) return;

  const { commandName } = interaction;
  const command = client.commands.get(commandName);

  if (!command) return;

  try {
    await command.execute(interaction);
  } catch (error) {
    console.error(`Error executing command ${commandName}:`, error);
    await interaction.reply({ content: 'An error occurred while executing this command.', ephemeral: true });
  }
});

client.login(token);

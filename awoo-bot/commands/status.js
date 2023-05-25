const { SlashCommandBuilder, ChannelTypes, ActivityType } = require('discord.js');
const { userId } = require('../config/config.json');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('status')
    .setDescription('Set bot status')
    .addStringOption(option =>
      option
        .setName('status')
        .setDescription('The new bot status')
        .setRequired(true)
    ),
  async execute(interaction) {
    if (interaction.user.id !== userId) {
      await interaction.reply('You do not have permission to use this command.');
      return;
    }

    const statusMessage = interaction.options.getString('status');
    const statusMessages = 'mugi.pages.dev';

    try {
      await interaction.client.user.setPresence({
        activities: [{ name: `${statusMessages} ${statusMessage}`, type: ActivityType.PLAYING }],
        status: 'online',
      });
      await interaction.reply(`Bot status set to: ${statusMessage}`);
    } catch (error) {
      console.error('Failed to set bot status:', error);
      await interaction.reply('An error occurred while setting the bot status.');
    }
  },
};

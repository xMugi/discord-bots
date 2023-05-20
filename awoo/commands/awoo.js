const { SlashCommandBuilder } = require('discord.js');
const fs = require('fs');
const path = require('path');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('awoo')
    .setDescription('awooooooooooooo.'),
  async execute(interaction) {
    const awooDirectory = './awoo'; // Directory path where the awoo images are located

    try {
      const files = fs.readdirSync(awooDirectory);
      const randomIndex = Math.floor(Math.random() * files.length);
      const randomFile = files[randomIndex];
      const attachmentUrl = path.join(awooDirectory, randomFile);
      await interaction.reply({ content: 'Awoo!', files: [attachmentUrl] });
    } catch (error) {
      console.error(error);
      await interaction.reply({ content: 'Failed to execute the command.', ephemeral: true });
    }
  },
};
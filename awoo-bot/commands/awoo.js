const { SlashCommandBuilder } = require('discord.js');
const fs = require('fs');
const path = require('path');

const awooUrlsFile = path.join(__dirname, '..', 'config', 'awooUrls.json');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('awoo')
    .setDescription('awooooooooooooo.'),
  async execute(interaction) {
    try {
      // Read existing fileUrls from awooUrls.json
      const fileUrlsData = fs.readFileSync(awooUrlsFile, 'utf-8');
      const fileUrls = JSON.parse(fileUrlsData);

      // Select a random URL from the fileUrls
      const randomIndex = Math.floor(Math.random() * fileUrls.length);
      const randomUrl = fileUrls[randomIndex];

      // Post the response with the embedded image
      await interaction.reply({ content: 'Awoo!', embeds: [{ image: { url: randomUrl } }] });
    } catch (error) {
      console.error(error);
      await interaction.reply({ content: 'Failed to execute the command.', ephemeral: true });
    }
  },
};

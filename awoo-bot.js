const Discord = require('discord.js');
const client = new Discord.Client();

client.on('ready', () => {
  console.log(`Logged in as ${client.user.tag}`);
});

client.on('message', (message) => {
  if (message.content === '/awoo') {
    const attachment = new Discord.MessageAttachment('https://mugi.me/discord/bots/img/awoo.png');
    message.channel.send(attachment);
  }
});

client.login('your_bot_token');

const { defineConfig } = require('@vue/cli-service')

const path = require('path');
const dotenv = require('dotenv');

// Load .env from project root
dotenv.config({
  path: path.resolve(__dirname, '../.env')
});

module.exports = defineConfig({
  transpileDependencies: true
})

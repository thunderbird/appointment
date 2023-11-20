const { defineConfig } = require('@vue/cli-service');
const { sentryWebpackPlugin } = require('@sentry/webpack-plugin');

module.exports = defineConfig({
  transpileDependencies: true,
  productionSourceMap: true,
  publicPath: '/',
  pages: {
    index: {
      entry: 'src/main.js',
      title: 'Thunderbird Appointment',
    },
  },
  configureWebpack: {
    devtool: 'source-map', // Source map generation must be turned on
    plugins: [
      sentryWebpackPlugin({
        org: 'thunderbird',
        project: 'appointment-frontend',

        // Auth tokens can be obtained from https://sentry.io/settings/account/api/auth-tokens/
        // and need `project:releases` and `org:read` scopes
        authToken: process.env.SENTRY_AUTH_TOKEN,
      }),
    ],
  }
});

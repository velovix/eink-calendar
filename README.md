# eInk Calendar

Displays Google Calendar events on an Inky Impression display connected to a
Raspberry Pi.

![Example showing how the UI looks](https://i.imgur.com/cKqnSmU.png)

## Installation

This project is available on PyPI and can be installed with `pipx`.

```bash
pipx install eink-calendar
```

Then, you will need to create a desktop OAuth2 client ID using the Google Cloud
console. For details on how to do this, see
[Google's Documentation][oauth2_client_docs].

Once you have created the client ID, download the client secret JSON file to
`~/.local/share/eink-calendar/credentials.json`.

Then, start the application:

```bash
eink-calendar
```

A browser window will automatically open prompting you to give eInk Calendar
read access to your calendars. Once this process completes, the application
will start. You only need to complete this process once.

## Development

If you want to develop without the eInk display connected, start the
application with the following flag:

```bash
eink-calendar --no-display
```

The generated images will be opened using your image viewer instead.

[oauth2_client_docs]: https://developers.google.com/identity/protocols/oauth2/native-app

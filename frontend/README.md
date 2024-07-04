# Thunderbird Appointment Frontend

This is the frontend component of Thunderbird Appointment. It's written in VueJS with Vite.

## Project setup

Copy the [.env.example](.env.example) as `.env`.

Then simply run:

```bash
yarn install
```

### Compiles and hot-reloads for development

```bash
yarn run serve
```

### Compiles and minifies for production

```bash
yarn run build
```

### Post-CSS

We use post-css to enhance our css. Any post-css that isn't in a SFC must be in a `.pcss` file and imported into the scoped style like so:

```css
@import '@/assets/styles/custom-media.pcss';

@media (--md) {
  .container {
    ...
  }
}
```

### Lints and fixes files

Frontend is formatted using ESlint with airbnb rules.

```bash
yarn run lint
yarn run lint --fix
```

### Run tests

```bash
yarn run test
```

### Customize configuration

See [Configuration Reference](https://cli.vuejs.org/config/).

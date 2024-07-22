# Thunderbird Appointment Frontend

This is the frontend component of Thunderbird Appointment. It's written in VueJS with Vite.

## Project setup

Copy the [.env.example](.env.example) as `.env`.

Then simply run:

```bash
npm install
```

### Compiles and hot-reloads for development

```bash
npm run serve
```

### Compiles and minifies for production

```bash
npm run build
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

### Rate limits

We use slowapi for rate limiting. In order for rate limiting to function an api route needs to be have the @limiter decorator below the request decorator, and they need to have `request: Request` as a parameter.

### Lints and fixes files

Frontend is formatted using ESlint with airbnb rules.

```bash
npm run lint
npm run lint -- --fix
```

### Run tests

```bash
npm run test
```


### Customize configuration

See [Configuration Reference](https://cli.vuejs.org/config/).

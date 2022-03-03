import {
  faPlay,
  faSync,
  faTimes,
  faVideo,
} from '@fortawesome/free-solid-svg-icons'

export default {
  // https://nuxtjs.org/docs/get-started/commands/#static-deployment-pre-rendered
  target: 'static',

  // Global page headers: https://go.nuxtjs.dev/config-head
  head: {
    htmlAttrs: {
      lang: 'en'
    },
    titleTemplate(titleChunk) {
      const baseTitle = 'YTDVR'
      return titleChunk ? `${titleChunk} | ${baseTitle}` : baseTitle
    },
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { hid: 'description', name: 'description', content: '' },
      { name: 'format-detection', content: 'telephone=no' }
    ],
    link: [
      { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
    ]
  },

  // Global CSS: https://go.nuxtjs.dev/config-css
  css: [
  ],

  // Plugins to run before rendering page: https://go.nuxtjs.dev/config-plugins
  plugins: [
    { src: '~/plugins/vue-socketio.js', ssr: false }
  ],

  // Auto import components: https://go.nuxtjs.dev/config-components
  components: true,

  // Modules for dev and build (recommended): https://go.nuxtjs.dev/config-modules
  buildModules: [
  ],

  // Modules: https://go.nuxtjs.dev/config-modules
  modules: [
    // https://go.nuxtjs.dev/chakra
    '@chakra-ui/nuxt',
    // https://go.nuxtjs.dev/emotion
    '@nuxtjs/emotion',
    // https://go.nuxtjs.dev/axios
    '@nuxtjs/axios',
    // https://www.npmjs.com/package/@nuxtjs/dayjs
    '@nuxtjs/dayjs',
  ],

  // Axios module configuration: https://go.nuxtjs.dev/config-axios
  // axios: {
  //   baseURL: 'http://localhost:8000'
  // },
  publicRuntimeConfig: {
    socket: {
      endpoint: 'http://localhost:8000',
      path: '/ws/socket.io'
    },
    axios: {
      baseURL: 'http://localhost:8000/api'
    }
  },

  // Chakra UI: https://vue.chakra-ui.com/with-nuxt
  chakra: {
    // https://vue.chakra-ui.com/auto-import-components
    autoImport: true,
    // https://vue.chakra-ui.com/icon/#using-an-icon-library
    icons: {
      // https://www.npmjs.com/package/@fortawesome/free-solid-svg-icons
      // https://fontawesome.com/v5/search?m=free
      iconPack: 'fa',
      iconSet: {
        faPlay,
        faSync,
        faTimes, // cross
        // faTrash,
        faVideo,
      }
    }
  },

  // DayJS: https://www.npmjs.com/package/@nuxtjs/dayjs
  dayjs: {
    defaultTimeZone: 'Europe/Oslo',
    plugins: [
      // 'utc', // import 'dayjs/plugin/utc'
      'timezone' // import 'dayjs/plugin/timezone'
    ]
  },

  // Build Configuration: https://go.nuxtjs.dev/config-build
  build: {
  }
}

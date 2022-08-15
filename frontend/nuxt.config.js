import {
  faList,
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
    '@/assets/css/toasts.css',
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
    // https://www.npmjs.com/package/@nuxtjs/toast
    '@nuxtjs/toast',
  ],

  // Axios module configuration: https://go.nuxtjs.dev/config-axios
  publicRuntimeConfig: {
    socket: {
      endpoint: process.env.API_BASE_URL || '',
      path: '/ws/socket.io'
    },
    axios: {
      baseURL: (process.env.API_BASE_URL || '') + '/api'
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
        faList,
        faPlay,
        faSync,
        faTimes, // cross
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

  // Toast: https://www.npmjs.com/package/@nuxtjs/toast
  toast: {
    position: 'bottom-center',
    action : {
      text : 'OK',
      onClick : (e, toastObject) => {
          toastObject.goAway(0);
      }
  },
    // duration: 5000,
  },

  // Build Configuration: https://go.nuxtjs.dev/config-build
  build: {
  }
}

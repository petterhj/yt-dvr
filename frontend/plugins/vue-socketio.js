import Vue from 'vue'
import VueSocketIOExt from 'vue-socket.io-extended';
import { io } from 'socket.io-client';

export default ({ $config, store }) => {
  const socket = io($config.socket.endpoint, {
    path: $config.socket.path,
    reconnection: true,
  });

  Vue.use(VueSocketIOExt, socket, { store });
}

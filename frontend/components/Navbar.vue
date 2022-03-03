<template>
  <c-box
    as="nav"
    h="60px"
    bg="gray.700"
    px="8"
    d="flex"
    align-items="center"
  >
    <c-text
      font-weight="bold"
      font-size="xl"
      color="red.300"
    >
      YTDVR
    </c-text>
    <c-badge
      mt="1"
      mx="5"
      :variant-color="isConnected ? 'green' : 'red'"
    >
      <template v-if="isConnected">CONNECTED</template>
      <template v-else>DISCONNECTED</template>
    </c-badge>

    <c-box
      as="ul"
      d="flex"
      align-items="center"
      list-style-type="none"
      ml="12"
    > 
      <!-- <c-box as="li" mr="8">
        <c-link as="nuxt-link" to="/films">
          <c-icon class="icon" name="film" />Films
        </c-link>
      </c-box>
      <c-box as="li" mr="8">
        <c-link as="nuxt-link" to="/podcasts">
          <c-icon class="icon" name="podcast" />Podcasts
        </c-link>
      </c-box> -->
    </c-box>

    <c-box
      as="ul"
      d="flex"
      align-items="center"
      list-style-type="none"
      ml="auto"
    >
      <c-box as="li">
        <c-icon-button
          mr="3"
          variant-color="blue"
          aria-label="Refresh videos"
          icon="sync"
          @click="this.getPlaylistVideos"
        />
      </c-box>
      <c-box as="li">
        <c-icon-button
          variant-color="red"
          aria-label="Process videos"
          icon="play"
          @click="this.processVideos"
        />
      </c-box>
    </c-box>
  </c-box>
</template>

<script lang="js">
import { mapActions, mapGetters } from "vuex"

export default {
  computed: {
    ...mapGetters(['isConnected'])
  },
  methods: {
     ...mapActions(['getPlaylistVideos', 'processVideos']),
  }
}
</script>
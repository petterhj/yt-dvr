<template>
  <div class="container">
    <c-flex direction="column">
      <video-item
        v-for="(video, video_id) in videos"
        :key="video_id"
        :item="video"
      />
    </c-flex>
  </div>
</template>

<script lang="js">
import { mapGetters, mapActions } from "vuex"

export default {
  computed: {
    ...mapGetters(['isConnected', 'videos'])
  },
  watch: {
    isConnected(connected) {
      if (connected) {
        this.getState()
        this.getPlaylistVideos()
      }
    }
  },
  methods: {
     ...mapActions(['getState', 'getPlaylistVideos']),
  }
}
</script>

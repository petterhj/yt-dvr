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
    ...mapGetters({
      videos: 'videos'
    })
  },
  methods: {
     ...mapActions(['getPlaylistVideos']),
  },
  created() {
    this.getPlaylistVideos()
  }
}
</script>

<style lang="scss" scoped>

</style>
<template>
  <c-box>
    <c-flex align="center">
      <c-progress
        :color="progressColor"
        :value="progressPercent"
        height="24px"
        style="border-radius: 0.25rem;"
        :has-stripe="isOngoing"
        :is-animated="isOngoing"
        mr="2"
        flex-grow="1"
      />
      <c-icon-button
        v-if="item.job"
        size="xs"
        variant="ghost"
        variant-color="gray.500"
        aria-label="Clear job"
        title="Clear job"
        icon="times"
        opacity="0.5"
        :_hover="{ opacity: 1 }"
        @click="clearJob(item.video_id)"
      />
    </c-flex>
    <c-text color="gray.500" font-size="sm" mt="1">
      {{ progressText }}
    </c-text>
  </c-box>
</template>

<script lang="js">
import { mapActions } from "vuex"

export default {
  props: {
    item: {
      type: Object,
      required: true
    },
  },
  computed: {
    isOngoing() {
      return ((
        this.item.job && this.item.job.started_at && !this.isDone
      ) ? true : false)
    },
    isDone() {
      return (this.item.job && (
        this.item.job.downloaded_at || this.item.job.failed_at
      ) ? true : false)
    },
    progressText() {
      if (!this.isDone && this.item.job.started_at) {
        const progress = this.item.progress
        if (progress) {
          if (progress.processor === "downloader") {
            if (progress.status === "downloading")
              if (progress.percent)
                return `Downloading: ${progress.percent} %`
              else
                return "Downloading..."
            else
              return `Downloading: ${progress.status}`
          }
          else {
            return `${progress.processor}: ${progress.status}`
          }
        }
        return 'Started - awaiting progress updates...'
      }
      else {
        if (this.item.job.downloaded_at)
          return 'Completed at ' + this.$dayjs(this.item.job.downloaded_at).format('DD.MM.YY - HH:MM:ss')
        if (this.item.job.failed_at)
          return 'Failed at ' + this.$dayjs(this.item.job.downloaded_at).format('DD.MM.YY - HH:MM:ss')
      }
    },
    progressPercent() {
      if (this.isDone)
        return 100
      if (this.isOngoing)
        if (this.item.progress && this.item.progress.percent)
          return this.item.progress.percent
        else
          return 100
      return 0
    },
    progressColor() {
      if (this.isDone) {
        if (this.item.job.downloaded_at)
          return 'green'
        if (this.item.job.failed_at)
          return 'red'
      }
      return 'orange'
    }
  },
  methods: {
     ...mapActions(['clearJob']),
  },
}
</script>

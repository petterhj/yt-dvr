<template>
  <c-flex
    v-if="item"
    flex-wrap="wrap"
    p="6"
    py="8"
    class="item"
  >
    <c-box width="60%" pr="10">
      <c-text color="gray.300" is-truncated>
        <c-icon
          name="video"
          color="white"
          style="margin: -2px 16px 0 0;"
        />
        <c-link :href="item.video_url" is-external>
          {{ item.title }}
        </c-link><br>
        <c-text color="gray.500" font-size="sm" style="margin-left: 36px;" mt="1">
          <c-link :href="item.channel_url" is-external>
            <b>{{ item.channel_title }}</b>
          </c-link> - {{ $dayjs(item.added_at).format('DD.MM.YY - HH:MM:ss') }}
        </c-text>
      </c-text>
    </c-box>
    <c-box width="40%">
      <job v-if="item.job" :item="item" />
    </c-box>
  </c-flex>
</template>

<script lang="js">
export default {
  props: {
    item: {
      type: Object,
      required: true
    },
  }
}
</script>

<style lang="scss" scoped>
// .item:nth-child(even) {
//   background: rgba(255, 255, 255, 0.025);
// }
.item {
  border-bottom: 2px solid #2D3748;
}
</style>
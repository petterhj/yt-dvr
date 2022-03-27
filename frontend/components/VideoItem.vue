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
          <template v-if="item.channel_title">
            <c-link :href="item.channel_url" is-external>
              <b>{{ item.channel_title }}</b>
            </c-link> -
          </template>{{ $dayjs(item.added_at).format('DD.MM.YY - HH:MM:ss') }}
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

<style lang="css" scoped>
.item {
  border-bottom: 2px solid #242b37;
}
</style>

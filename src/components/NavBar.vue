<template>
  <v-toolbar class="dark">
    <v-toolbar-title v-text="title"></v-toolbar-title>
    <v-spacer></v-spacer>
    <v-btn flat to='/auth'>
      Login
    </v-btn>
  </v-toolbar>
</template>

<script>

export default {
  data () {
      return {
          title: 'label.ml'
      }
  }
}
</script>

<style scoped>
</style>

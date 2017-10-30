<template>
 <v-toolbar class="dark">
    <v-toolbar-title v-text="title"></v-toolbar-title>
    <v-spacer></v-spacer>
    <v-btn flat v-if="!isAuthenticated()" v-on:click="login()">
      Login
    </v-btn>
    <v-btn flat v-if="isAuthenticated()" v-on:click="logout()">
      Login
    </v-btn>
  </v-toolbar>
</template>

<script>


export default {
  props: ['auth', 'authenticated'],
  data () {
    return {
      title: 'label.ml',
    }
  },
  methods: {
    isAuthenticated () {
      return this.authenticated
    },
    login () {
      this.auth.login()
    },
    logout () {
      this.auth.logout()
    }
  }
}
</script>

<style scoped>
</style>

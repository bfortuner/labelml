<template>
  <div id="app">
  <head>
      <link href='https://fonts.googleapis.com/css?family=Roboto:300,400,500,700|Material+Icons' rel="stylesheet">
  </head>
    <router-view
      :auth="auth"
      :authenticated="authenticated">
    </router-view>
  </div>
</template>

<script>

import AuthService from './Auth/AuthService'

const auth = new AuthService()

const { authenticated, authNotifier } = auth

export default {
  name: 'app',
  data () {
      authNotifier.on('authChange', authState => {
      this.authenticated = authState.authenticated
    })
    return {
      auth,
      authenticated
    }
  }
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  /* text-align: center; */
  color: #2c3e50;
  /* margin-top: 60px; */
}
</style>

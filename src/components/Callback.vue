// src/components/Callback.vue

<template>
  <div class="spinner">
    <img src="../assets/loading.svg" alt="loading"/>
  </div>
</template>

<script>
  export default {
    name: 'callback',
    props: ['auth'],
    data () {
      this.auth.handleAuthentication()
      return {}
    }
  }
</script>

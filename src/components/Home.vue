<template>
  <div>
    <router-link to="project/example_data" tag="button">Try Demo</router-link>
    <router-link to="project/example_data" tag="button">Watch Video</router-link>
  </div>
</template>

<script>
import keys from '../constants/keyboard.js';
console.log(keys);
console.log(keys.KEY_MAP);
console.log(keys.KEYS);

export default {
  name: 'home',
  components: {},
  props: [],
}
</script>


<style scoped>

</style>
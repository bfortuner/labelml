// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
import ApolloClient, {createNetworkInterface} from 'apollo-client';
import VueApollo from 'vue-apollo';

Vue.config.productionTip = false

var HOST = '10.0.0.21' //localhost
var uri = `http://${HOST}:5000/graphql`
console.log(uri);

const apolloClient = new ApolloClient({
  networkInterface: createNetworkInterface({
    uri: `http://${HOST}:5000/graphql`,
    transportBatching: true,
  }),
});

Vue.use(VueApollo, {
  apolloClient,
});

const apolloProvider = new VueApollo({
  defaultClient: apolloClient,
  defaultOptions: {
    $loadingKey: 'loading'
  }
})

/* eslint-disable no-new */
new Vue({
  el: '#app',
  apolloProvider,
  router,
  template: '<App/>',
  components: { App }
})

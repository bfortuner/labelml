import Vue from 'vue'
import Router from 'vue-router'
import Editor from '@/components/Editor'
import Home from '@/components/Home'

Vue.use(Router)

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/project/:project',
      name: 'editor',
      component: Editor,
      props: true
    },
    {
      path: '/home',
      name: 'home',
      component: Home,
    },
    {
      path: '*',
      redirect: '/home'
    }
  ]
})

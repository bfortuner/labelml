import Vue from 'vue'
import Router from 'vue-router'
import Editor from '@/components/Editor'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/project/:project',
      name: 'Editor',
      component: Editor,
      props: true
    },
    { path: '/', 
      component: Editor, 
      props: { project: 'example_data' } 
    }
  ]
})

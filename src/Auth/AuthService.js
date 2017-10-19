// src/Auth/AuthService.js

import auth0 from 'auth0-js'

export default class AuthService {

  constructor () {
    this.login = this.login.bind(this)
  }

  auth0 = new auth0.WebAuth({
    domain: 'labelml.auth0.com',
    clientID: 'b3hP7JbR3TGOXjWG6S5bN6UY9dO42n9J',
    redirectUri: 'http://localhost:8080/callback',
    audience: 'https://labelml.auth0.com/userinfo',
    responseType: 'token id_token',
    scope: 'openid'
  })

  login () {
    this.auth0.authorize()
  }
}

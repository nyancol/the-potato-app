import { createApp, provide, h } from "vue";
import App from "./App.vue";

import { ApolloClient, InMemoryCache } from '@apollo/client/core'
import { createApolloProvider } from '@vue/apollo-option'
import VueApolloComponents from '@vue/apollo-components'

import { DefaultApolloClient } from '@vue/apollo-composable'

import { createRouter, createWebHistory } from "vue-router";

import vuetify from "./plugins/vuetify";

import HomePage from "./views/HomePage.vue";
import AnnuaireGallery from "./components/AnnuaireGallery.vue";
import PokedexGallery from "./components/PokedexGallery.vue";


const cache = new InMemoryCache()

const apolloClient = new ApolloClient({
  cache,
  uri: 'http://localhost:5000/graphql',
})

const apolloProvider = createApolloProvider({
  defaultClient: apolloClient,
})


const app = createApp({
  setup () {
    provide(DefaultApolloClient, apolloClient)
  },

  render: () => h(App),
})

app.use(apolloProvider)

// Use Vue Router
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: HomePage },
    { path: "/annuaire", component: AnnuaireGallery },
    { path: "/pokedex", component: PokedexGallery },
    // Add routes for other components
  ],
});

app.use(router);
app.use(VueApolloComponents)
app.use(vuetify);
app.mount("#app");

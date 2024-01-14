import { createApp } from "vue";
import App from "./App.vue";
import { createRouter, createWebHistory } from "vue-router";
import vuetify from "./plugins/vuetify";
import HomePage from "./views/HomePage.vue";
import AnnuaireGallery from "./components/AnnuaireGallery.vue";
import PokedexGallery from "./components/PokedexGallery.vue";

const app = createApp(App);

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

// Use Vuetify
app.use(vuetify);

app.mount("#app");

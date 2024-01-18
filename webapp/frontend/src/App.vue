<template>
  <v-app>
    <v-app-bar app>
      <v-toolbar-title>Republique des Patates</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn to="/">Home</v-btn>
      <v-btn to="/annuaire">Annuaire</v-btn>
      <v-btn to="/pokedex">Pokedex</v-btn>
      <v-btn to="/naturalisation">Demander la naturalisation</v-btn>
      <v-btn to="/horoscope">Horoscope</v-btn>
      <v-btn to="/coup">Demander un coup d'état</v-btn>
    </v-app-bar>

    <v-main>
      <v-container>
        <router-view></router-view>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
export default {
  name: "App",
};
</script>

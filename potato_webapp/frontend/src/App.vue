<!--
<template>
  <v-app>
    <v-main>
      <ImageGallery/>
    </v-main>
  </v-app>
</template>

<script>
// import HelloWorld from './components/HelloWorld.vue'
import ImageGallery from './components/ImageGallery.vue';

export default {
  name: 'App',

  components: {
    // HelloWorld,
    ImageGallery
},

  data: () => ({
    //
  }),
}
</script>
-->
<template>
  <div id="app">
    <LandingPage />
  </div>
</template>

<script>
import LandingPage from '@/components/LandingPage.vue';

export default {
  name: 'App',
  components: {
    LandingPage,
  },
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>

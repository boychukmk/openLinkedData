<template>
  <div>
    <nav class="navbar">
      <router-link to="/">Home</router-link>
      <router-link to="/chat">Chat</router-link>
      <router-link to="/hospitals">Hospitals</router-link>
      <router-link to="/drug-disease-graph">Drug Graph</router-link>

    </nav>
    <div class="content">
      <router-view />
    </div>
  </div>
</template>
<style scoped>
.navbar {
  position: fixed;
  top: 0;
  width: 100%;
  height: 60px;
  background-color: #333;
  display: flex;
  justify-content: center; /* Центрируем */
  align-items: center;
  z-index: 1000;
}

.navbar a {
  color: white;
  text-decoration: none;
  margin: 0 20px;
  font-size: 18px;
}
</style>

<script setup lang="ts">
import Hospitals from "./pages/Hospitals.vue";
</script>
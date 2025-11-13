import { createApp } from "vue";
import { createRouter, createWebHistory } from "vue-router";
import App from "./App.vue";
import Home from "./pages/Home.vue";
import Chat from "./pages/Chat.vue";
import Hospitals from "./pages/Hospitals.vue";
import DrugDiseaseGraph from "./pages/DrugDiseaseGraph.vue";
import "./style.css";

const routes = [
  { path: "/", component: Home },
  { path: "/chat", component: Chat },
  { path: "/hospitals", component: Hospitals },
  { path: "/drug-disease-graph", component: DrugDiseaseGraph },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

createApp(App).use(router).mount("#app");

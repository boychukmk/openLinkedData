<template>
  <div>
    <nav class="navbar">
      <router-link to="/">Diseases</router-link>
      <router-link to="/chat">Chat</router-link>
      <router-link to="/hospitals">Hospitals</router-link>
      <router-link to="/drug-disease-graph">Drug Graph</router-link>

      <div
        class="theme-switcher"
        @click="toggleTheme"
        role="switch"
        :aria-checked="isDark.toString()"
        tabindex="0"
        @keydown.space.prevent="toggleTheme"
        @keydown.enter.prevent="toggleTheme"
      >
        <div class="switch-track">
          <div class="switch-thumb" :class="{ dark: isDark }"></div>
        </div>
        <div class="labels">
          <span :class="{ active: !isDark }">Light</span>
          <span :class="{ active: isDark }">Dark</span>
        </div>
      </div>
    </nav>
    <router-view />
  </div>
</template>

<script>
export default {
  data() {
    return {
      isDark: false,
    };
  },
  mounted() {
    const saved = localStorage.getItem("theme");
    this.isDark = saved === "dark";
    this.applyTheme();
  },
  methods: {
    toggleTheme() {
      this.isDark = !this.isDark;
      this.applyTheme();
      localStorage.setItem("theme", this.isDark ? "dark" : "light");
    },
    applyTheme() {
      document.documentElement.setAttribute("data-theme", this.isDark ? "dark" : "light");
      // Міняємо фон body (або іншого контейнера)
      document.body.style.backgroundColor = this.isDark ? "#121212" : "#ffffff";
    },
  },
};
</script>

<style>
.navbar {
  position: fixed;
  top: 0;
  width: 100%;
  height: 100px;
  background-color: #00796b; /* залишаємо */
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 30px;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0, 121, 107, 0.6);
  border-bottom: 2px solid #a7ffeb;
  padding: 0 20px;
}

/* Посилання */
.navbar a {
  color: #ffffff;
  font-weight: 600;
  font-size: 25px;
  text-decoration: none;
  transition: all 0.3s ease;
}

.navbar a:hover {
  color: #b2fef7;
  text-shadow: 0 0 6px #64ffda;
}

/* Перемикач */
.theme-switcher {
  display: flex;
  align-items: center;
  cursor: pointer;
  user-select: none;
  outline: none;
  /* прибираємо outline та box-shadow */
}

.theme-switcher:focus {
  /* При бажанні можна залишити тонку підсвітку фокусування, або прибрати */
  outline: none;
}

.switch-track {
  position: relative;
  width: 60px;
  height: 30px;
  background: linear-gradient(
    to right,
    #b2dfdb 50%,
    #004d40 50%
  );
  border-radius: 15px;
  margin-right: 12px;
  transition: background 0.3s ease;
  /* прибираємо box-shadow */
  box-shadow: none;
}

.switch-thumb {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 24px;
  height: 24px;
  background-color: #ffffff; /* Білий для світлої теми */
  border-radius: 50%;
  /* прибираємо тіні */
  box-shadow: none;
  transition: left 0.3s ease, background-color 0.3s ease;
}

.switch-thumb.dark {
  left: 33px;
  background-color: #000000; /* Чорний для темної теми */
}

/* Лейбли (стікери) */
.labels {
  display: flex;
  gap: 10px;
  font-weight: 600;
  font-size: 14px;
  color: #a7ffebaa;
  user-select: none;
}

.labels span {
  padding: 2px 8px;
  border-radius: 8px;
  background-color: #00796b44;
  transition: background-color 0.3s ease, color 0.3s ease;
}

.labels span.active {
  background-color: #a7ffeb;
  color: #004d40;
  font-weight: 700;
  box-shadow: 0 0 5px #64ffda;
}
</style>

<template>
  <div class="flex min-h-screen bg-gray-100">
    <!-- Sidebar: show only if logged in -->
    <SideBar v-if="showSidebar" />

    <!-- Main content -->
    <main class="flex-1 p-6 overflow-auto h-screen">
      <router-view />
    </main>
  </div>
</template>

<script>
import { computed } from "vue";
import { useRoute } from "vue-router";
import SideBar from "./SideBar.vue";

export default {
  components: { SideBar },
  setup() {
    const route = useRoute();

    const isLoggedIn = computed(() => !!localStorage.getItem("token"));
    const showSidebar = computed(() => !["/login", "/register"].includes(route.path));

    return { isLoggedIn, showSidebar };
  },
};
</script>

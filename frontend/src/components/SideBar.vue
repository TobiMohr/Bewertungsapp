<template>
  <aside class="w-64 bg-white shadow-md p-6 flex flex-col min-h-screen">
    <h2 class="text-2xl font-bold mb-6">Dashboard</h2>

    <nav class="flex-1">
      <ul class="space-y-2">
        <!-- Users Menüpunkt -->
        <li>
          <button
            @click="toggleUsers"
            class="w-full flex justify-between items-center px-4 py-2 rounded hover:bg-gray-200"
          >
            <span>Users</span>
            <svg
              :class="{'rotate-90': usersOpen}"
              class="w-4 h-4 transition-transform"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M9 5l7 7-7 7">
              </path>
            </svg>
          </button>

          <!-- Unterpunkte -->
          <ul v-show="usersOpen" class="mt-2 ml-4 space-y-1">
            <li>
              <router-link
                to="/users"
                class="block px-4 py-2 rounded hover:bg-gray-200"
                active-class="bg-gray-300 font-semibold"
              >
                List
              </router-link>
            </li>
            <li>
              <router-link
                to="/users/create"
                class="block px-4 py-2 rounded hover:bg-gray-200"
                active-class="bg-gray-300 font-semibold"
              >
                Create
              </router-link>
            </li>
          </ul>
        </li>
      </ul>
    </nav>

    <!-- Logout Button -->
    <button
      @click="logout"
      class="mt-auto px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
    >
      Logout
    </button>
  </aside>
</template>

<script>
import { ref } from "vue";
import { useRouter } from "vue-router";

export default {
  setup() {
    const router = useRouter();

    const usersOpen = ref(false);

    const toggleUsers = () => {
      usersOpen.value = !usersOpen.value;
    };

    const logout = () => {
      localStorage.removeItem("token");
      router.push("/login");
    };

    return { usersOpen, toggleUsers, logout };
  },
};
</script>

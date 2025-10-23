<template>
  <aside
    @mouseenter="openSidebar"
    @mouseleave="closeSidebar"
    :class="[
      'bg-white shadow-md p-6 flex flex-col min-h-screen transition-all duration-300',
      sidebarOpen ? 'w-64' : 'w-20'
    ]"
  >
    <!-- Title -->
    <h2 v-if="sidebarOpen" class="text-2xl font-bold mb-6">Dashboard</h2>

    <nav class="flex-1">
      <ul class="space-y-2">
        <!-- Users Menu -->
        <li>
          <button
            @click="toggleUsers"
            class="w-full flex items-center px-4 py-2 rounded hover:bg-gray-200"
          >
            <UserIcon class="w-5 h-5 flex-shrink-0" />
            <span
              :class="[
                'ml-2 whitespace-nowrap transition-opacity duration-200',
                sidebarOpen ? 'opacity-100' : 'opacity-0 hidden'
              ]"
            >
              Users
            </span>
            <ChevronRightIcon
              v-if="!usersOpen && sidebarOpen"
              class="ml-auto w-4 h-4 transition-transform"
            />
            <ChevronDownIcon
              v-if="usersOpen && sidebarOpen"
              class="ml-auto w-4 h-4 transition-transform"
            />
          </button>

          <!-- Submenu -->
          <ul v-show="usersOpen && sidebarOpen" class="mt-2 ml-8 space-y-1">
            <li>
              <router-link
                to="/users"
                class="flex items-center px-4 py-2 rounded hover:bg-gray-200"
                active-class="bg-gray-300 font-semibold"
              >
                <ListBulletIcon class="w-5 h-5 flex-shrink-0" />
                <span class="ml-2">List</span>
              </router-link>
            </li>
            <li>
              <router-link
                to="/users/create"
                class="flex items-center px-4 py-2 rounded hover:bg-gray-200"
                active-class="bg-gray-300 font-semibold"
              >
                <PlusIcon class="w-5 h-5 flex-shrink-0" />
                <span class="ml-2">Create</span>
              </router-link>
            </li>
          </ul>
        </li>

        <!-- Roles Menu (NEW) -->
        <li>
          <button
            @click="toggleRoles"
            class="w-full flex items-center px-4 py-2 rounded hover:bg-gray-200"
          >
            <ShieldCheckIcon class="w-5 h-5 flex-shrink-0" />
            <span
              :class="[
                'ml-2 whitespace-nowrap transition-opacity duration-200',
                sidebarOpen ? 'opacity-100' : 'opacity-0 hidden'
              ]"
            >
              Roles
            </span>
            <ChevronRightIcon
              v-if="!rolesOpen && sidebarOpen"
              class="ml-auto w-4 h-4 transition-transform"
            />
            <ChevronDownIcon
              v-if="rolesOpen && sidebarOpen"
              class="ml-auto w-4 h-4 transition-transform"
            />
          </button>

          <!-- Submenu -->
          <ul v-show="rolesOpen && sidebarOpen" class="mt-2 ml-8 space-y-1">
            <li>
              <router-link
                to="/roles"
                class="flex items-center px-4 py-2 rounded hover:bg-gray-200"
                active-class="bg-gray-300 font-semibold"
              >
                <ListBulletIcon class="w-5 h-5 flex-shrink-0" />
                <span class="ml-2">List</span>
              </router-link>
            </li>
            <li>
              <router-link
                to="/roles/create"
                class="flex items-center px-4 py-2 rounded hover:bg-gray-200"
                active-class="bg-gray-300 font-semibold"
              >
                <PlusIcon class="w-5 h-5 flex-shrink-0" />
                <span class="ml-2">Create</span>
              </router-link>
            </li>
          </ul>
        </li>

        <!-- Criterias Menu -->
        <li>
          <button
            @click="toggleCriterias"
            class="w-full flex items-center px-4 py-2 rounded hover:bg-gray-200"
          >
            <ClipboardDocumentListIcon class="w-5 h-5 flex-shrink-0" />
            <span
              :class="[
                'ml-2 whitespace-nowrap transition-opacity duration-200',
                sidebarOpen ? 'opacity-100' : 'opacity-0 hidden'
              ]"
            >
              Criterias
            </span>
            <ChevronRightIcon
              v-if="!criteriasOpen && sidebarOpen"
              class="ml-auto w-4 h-4 transition-transform"
            />
            <ChevronDownIcon
              v-if="criteriasOpen && sidebarOpen"
              class="ml-auto w-4 h-4 transition-transform"
            />
          </button>

          <!-- Submenu -->
          <ul v-show="criteriasOpen && sidebarOpen" class="mt-2 ml-8 space-y-1">
            <li>
              <router-link
                to="/criterias"
                class="flex items-center px-4 py-2 rounded hover:bg-gray-200"
                active-class="bg-gray-300 font-semibold"
              >
                <ListBulletIcon class="w-5 h-5 flex-shrink-0" />
                <span class="ml-2">List</span>
              </router-link>
            </li>
            <li>
              <router-link
                to="/criterias/create"
                class="flex items-center px-4 py-2 rounded hover:bg-gray-200"
                active-class="bg-gray-300 font-semibold"
              >
                <PlusIcon class="w-5 h-5 flex-shrink-0" />
                <span class="ml-2">Create</span>
              </router-link>
            </li>
          </ul>
        </li>

        <!-- Sessions Menu -->
        <li>
          <button
            @click="toggleSessions"
            class="w-full flex items-center px-4 py-2 rounded hover:bg-gray-200"
          >
            <CalendarDaysIcon class="w-5 h-5 flex-shrink-0" />
            <span
              :class="[
                'ml-2 whitespace-nowrap transition-opacity duration-200',
                sidebarOpen ? 'opacity-100' : 'opacity-0 hidden'
              ]"
            >
              Sessions
            </span>
            <ChevronRightIcon
              v-if="!sessionsOpen && sidebarOpen"
              class="ml-auto w-4 h-4 transition-transform"
            />
            <ChevronDownIcon
              v-if="sessionsOpen && sidebarOpen"
              class="ml-auto w-4 h-4 transition-transform"
            />
          </button>

          <!-- Submenu -->
          <ul v-show="sessionsOpen && sidebarOpen" class="mt-2 ml-8 space-y-1">
            <li>
              <router-link
                to="/sessions"
                class="flex items-center px-4 py-2 rounded hover:bg-gray-200"
                active-class="bg-gray-300 font-semibold"
              >
                <ListBulletIcon class="w-5 h-5 flex-shrink-0" />
                <span class="ml-2">List</span>
              </router-link>
            </li>
            <li>
              <router-link
                to="/sessions/create"
                class="flex items-center px-4 py-2 rounded hover:bg-gray-200"
                active-class="bg-gray-300 font-semibold"
              >
                <PlusIcon class="w-5 h-5 flex-shrink-0" />
                <span class="ml-2">Create</span>
              </router-link>
            </li>
          </ul>
        </li>

        <!-- Files menu -->
        <li>
          <router-link
            to="/files"
            class="flex items-center px-4 py-2 rounded hover:bg-gray-200"
            active-class="bg-gray-300 font-semibold"
          >
            <ArrowUpTrayIcon class="w-5 h-5 flex-shrink-0" />
            <span
              :class="[
                'ml-2 whitespace-nowrap transition-opacity duration-200',
                sidebarOpen ? 'opacity-100' : 'opacity-0 hidden'
              ]"
            >
              Files
            </span>
          </router-link>
        </li>
      </ul>
    </nav>

    <!-- Logout Button -->
    <button
      @click="logout"
      class="mt-auto flex items-center px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
    >
      <ArrowRightOnRectangleIcon class="w-5 h-5 flex-shrink-0" />
      <span v-if="sidebarOpen" class="ml-2">Logout</span>
    </button>
  </aside>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

// Heroicons
import {
  ChevronRightIcon,
  ChevronDownIcon,
  UserIcon,
  ClipboardDocumentListIcon,
  CalendarDaysIcon,
  ListBulletIcon,
  PlusIcon,
  ArrowRightOnRectangleIcon,
  ArrowUpTrayIcon,
  ShieldCheckIcon,
} from "@heroicons/vue/24/outline";

const router = useRouter();

const sidebarOpen = ref(false);
const usersOpen = ref(false);
const criteriasOpen = ref(false);
const sessionsOpen = ref(false);
const rolesOpen = ref(false);

const openSidebar = () => (sidebarOpen.value = true);
const closeSidebar = () => (sidebarOpen.value = false);

const toggleUsers = () => (usersOpen.value = !usersOpen.value);
const toggleRoles = () => (rolesOpen.value = !rolesOpen.value);
const toggleCriterias = () => (criteriasOpen.value = !criteriasOpen.value);
const toggleSessions = () => (sessionsOpen.value = !sessionsOpen.value);

const logout = () => {
  localStorage.removeItem("token");
  router.push("/login");
};
</script>

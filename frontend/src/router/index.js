import { createRouter, createWebHistory } from "vue-router";

// Auth
import RegisterForm from "../components/AuthComponents/RegisterForm.vue";
import LoginForm from "../components/AuthComponents/LoginForm.vue";

// Users
import UserList from "../components/UserComponents/UserList.vue";
import UserForm from "../components/UserComponents/UserForm.vue";
import UserDetail from "../components/UserComponents/UserDetail.vue";

// Criterias
import CriteriaList from "@/components/CriteriaComponents/CriteriaList.vue";
import CriteriaForm from "@/components/CriteriaComponents/CriteriaForm.vue";

// Sessions
import SessionList from "@/components/SessionComponents/SessionList.vue";
import SessionForm from "@/components/SessionComponents/SessionForm.vue";
import SessionEdit from "@/components/SessionComponents/SessionEdit.vue";

// Phases
import PhaseDetail from "@/components/PhaseComponents/PhaseDetail.vue";

const routes = [
  { path: "/", redirect: "/login" },
  { path: "/login", component: LoginForm },
  { path: "/register", component: RegisterForm },

  // Users
  {
    path: "/users",
    component: UserList,
    meta: { requiresAuth: true },
  },
  {
    path: "/users/create",
    component: UserForm,
    meta: { requiresAuth: true },
  },
  {
    path: "/users/edit/:id",
    component: UserForm,
    props: true,
    meta: { requiresAuth: true },
  },
  {
    path: "/users/:id",
    component: UserDetail,
    meta: { requiresAuth: true },
  },

  // Criterias
  {
    path: "/criterias",
    component: CriteriaList,
    meta: { requiresAuth: true },
  },
  {
    path: "/criterias/create",
    component: CriteriaForm,
    meta: { requiresAuth: true },
  },

  // Sessions
  {
    path: "/sessions",
    component: SessionList,
    meta: { requiresAuth: true },
  },
  {
    path: "/sessions/create",
    component: SessionForm,
    meta: { requiresAuth: true },
  },
  {
    path: "/sessions/edit/:id",
    component: SessionEdit,
    props: true,
    meta: { requiresAuth: true },
  },
  // Phases
  {
    path: "/phases/:id",
    component: PhaseDetail,
    props: true,
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// simple navigation guard
router.beforeEach((to, from, next) => {
  const loggedIn = !!localStorage.getItem("token");
  if (to.meta.requiresAuth && !loggedIn) {
    next("/login");
  } else {
    next();
  }
});

export default router;

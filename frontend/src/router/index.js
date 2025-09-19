import { createRouter, createWebHistory } from "vue-router";
import RegisterForm from "../components/AuthComponents/RegisterForm.vue";
import LoginForm from "../components/AuthComponents/LoginForm.vue";
import UserList from "../components/UserComponents/UserList.vue";
import UserForm from "../components/UserComponents/UserForm.vue";
import UserDetail from "../components/UserComponents/UserDetail.vue";
import CriteriaList from "@/components/CriteriaComponents/CriteriaList.vue";
import CriteriaForm from "@/components/CriteriaComponents/CriteriaForm.vue";

const routes = [
  { path: "/", redirect: "/login" },
  { path: "/login", component: LoginForm },
  { path: "/register", component: RegisterForm },
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
    meta: { requiresAuth: true, }
  },
  {
    path: "/users/:id",
    component: UserDetail,
    meta: { requiresAuth: true, }
  },
  {
    path: "/criterias",
    component: CriteriaList,
    meta: { requiresAuth: true, }
  },
  {
    path: "/criterias/create",
    component: CriteriaForm,
    meta: { requiresAuth: true, }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// simple navigation guard
router.beforeEach((to, from, next) => {
  const loggedIn = !!localStorage.getItem("token"); // store token on login
  if (to.meta.requiresAuth && !loggedIn) {
    next("/login");
  } else {
    next();
  }
});

export default router;

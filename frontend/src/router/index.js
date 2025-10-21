import { createRouter, createWebHistory } from "vue-router";

// Auth
import RegisterForm from "@/live-sessions/components/AuthComponents/RegisterForm.vue";
import LoginForm from "@/live-sessions/components/AuthComponents/LoginForm.vue";

// Users
import UserList from "@/live-sessions/components/UserComponents/UserList.vue";
import UserForm from "@/live-sessions/components/UserComponents/UserForm.vue";
import UserDetail from "@/live-sessions/components/UserComponents/UserDetail.vue";
import UserEvaluation from "@/live-sessions/components/UserComponents/UserEvaluation.vue";

// Criterias
import CriteriaList from "@/live-sessions/components/CriteriaComponents/CriteriaList.vue";
import CriteriaForm from "@/live-sessions/components/CriteriaComponents/CriteriaForm.vue";
import CriterionUserView from "@/live-sessions/components/CriteriaComponents/CriterionUserView.vue";

// Sessions
import SessionList from "@/live-sessions/components/SessionComponents/SessionList.vue";
import SessionForm from "@/live-sessions/components/SessionComponents/SessionForm.vue";
import SessionEdit from "@/live-sessions/components/SessionComponents/SessionEdit.vue";

//Files
import FileExports from "@/live-sessions/components/FileComponents/FileExports.vue";



const routes = [
  { path: "/", redirect: "/users" },
  { path: "/login", component: LoginForm },
  { path: "/register", component: RegisterForm },

  // Users
  {
    path: "/users",
    component: UserList,
  },
  {
    path: "/users/create",
    component: UserForm,
  },
  {
    path: "/users/edit/:id",
    component: UserForm,
    props: true,
  },
  {
    path: "/users/:id",
    component: UserDetail,
  },
  {
    path: "/users/:id/evaluation",
    component: UserEvaluation,
    props: true,
  },

  // Criterias
  {
    path: "/criterias",
    component: CriteriaList,
  },
  {
    path: "/criterias/create",
    component: CriteriaForm,
  },
  {
    path: "/criterias/:id/users",
    component: CriterionUserView,
    props: true,
  },

  // Sessions
  {
    path: "/sessions",
    component: SessionList,
  },
  {
    path: "/sessions/create",
    component: SessionForm,
  },
  {
    path: "/sessions/edit/:id",
    component: SessionEdit,
    props: true,
  },
  // Files
  {
    path: "/files",
    component: FileExports,
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

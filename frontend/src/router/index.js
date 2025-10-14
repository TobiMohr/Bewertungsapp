import { createRouter, createWebHistory } from "vue-router";

// Auth
import RegisterForm from "../components/AuthComponents/RegisterForm.vue";
import LoginForm from "../components/AuthComponents/LoginForm.vue";

// Users
import UserList from "../components/UserComponents/UserList.vue";
import UserForm from "../components/UserComponents/UserForm.vue";
import UserDetail from "../components/UserComponents/UserDetail.vue";
import UserEvaluation from "@/components/UserComponents/UserEvaluation.vue";
import UserFiles from "@/components/UserComponents/UserFiles.vue";

// Criterias
import CriteriaList from "@/components/CriteriaComponents/CriteriaList.vue";
import CriteriaForm from "@/components/CriteriaComponents/CriteriaForm.vue";
import CriterionUserView from "@/components/CriteriaComponents/CriterionUserView.vue";

// Sessions
import SessionList from "@/components/SessionComponents/SessionList.vue";
import SessionForm from "@/components/SessionComponents/SessionForm.vue";
import SessionEdit from "@/components/SessionComponents/SessionEdit.vue";

// Phases
import PhaseDetail from "@/components/PhaseComponents/PhaseDetail.vue";
import PhaseForm from "@/components/PhaseComponents/PhaseForm.vue";



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
  {
    path: "/users/files",
    component: UserFiles,
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
  // Phases
  {
    path: "/phases/:id",
    component: PhaseDetail,
    props: true,
  },
  {
    path: "/phases/create",
    component: PhaseForm,
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

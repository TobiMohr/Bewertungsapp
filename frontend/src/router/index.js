import { createRouter, createWebHistory } from "vue-router";

// Auth
import RegisterForm from "@/live-sessions/components/AuthComponents/RegisterForm.vue";
import LoginForm from "@/live-sessions/components/AuthComponents/LoginForm.vue";

// Users
import UserList from "@/live-sessions/components/UserComponents/UserList.vue";
import UserForm from "@/live-sessions/components/UserComponents/UserForm.vue";
import UserDetail from "@/live-sessions/components/UserComponents/UserDetail.vue";
import UserEvaluation from "@/live-sessions/components/UserComponents/UserEvaluation.vue";

// Teams
import TeamList from "@/live-sessions/components/TeamComponents/TeamList.vue";
import TeamForm from "@/live-sessions/components/TeamComponents/TeamForm.vue";

// Criterias
import CriteriaList from "@/live-sessions/components/CriteriaComponents/CriteriaList.vue";
import CriteriaForm from "@/live-sessions/components/CriteriaComponents/CriteriaForm.vue";
import CriterionUserView from "@/live-sessions/components/CriteriaComponents/CriterionUserView.vue";

// Sessions
import SessionList from "@/live-sessions/components/SessionComponents/SessionList.vue";
import SessionForm from "@/live-sessions/components/SessionComponents/SessionForm.vue";
import SessionEdit from "@/live-sessions/components/SessionComponents/SessionEdit.vue";

// Roles
import RoleList from "@/live-sessions/components/RoleComponents/RoleList.vue";
import RoleForm from "@/live-sessions/components/RoleComponents/RoleForm.vue";

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

  // Teams
  {
    path: "/teams",
    component: TeamList,
  },
  {
    path: "/teams/create",
    component: TeamForm,
  },
  { 
    path: "/teams/edit/:id",
    component: TeamForm,
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
    path: "/criterias/edit/:id",
    component: CriteriaForm,
    props: true,
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
  // Roles
  {
    path: "/roles",
    component: RoleList,
  },
  { 
    path: "/roles/create",
    component: RoleForm,
  },
  {
    path: "/roles/edit/:id",
    component: RoleForm,
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

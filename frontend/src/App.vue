<template>
  <div id="app">
    <h1>User Management</h1>
    <!-- User form to create new users -->
    <UserForm @user-created="refreshUsers" />

    <!-- User list -->
    <UserList 
      ref="userList"
      @edit-user="startEdit"
    />

    <!-- Optional: User edit view/modal -->
    <UserView 
      v-if="editingUser"
      :user="editingUser"
      @update-complete="onUpdateComplete"
      @close="editingUser = null"
    />
  </div>
</template>

<script>
import UserForm from './components/UserForm.vue';
import UserList from './components/UserList.vue';
import UserView from './components/UserView.vue';

export default {
  name: 'App',
  components: {
    UserForm,
    UserList,
    UserView
  },
  data() {
    return {
      editingUser: null
    }
  },
  methods: {
    refreshUsers() {
      // call UserList's fetch method via ref
      this.$refs.userList.fetchUsers();
    },
    startEdit(user) {
      this.editingUser = user; // show the edit modal/view
    },
    onUpdateComplete() {
      this.editingUser = null;
      this.refreshUsers();
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 40px;
}
</style>

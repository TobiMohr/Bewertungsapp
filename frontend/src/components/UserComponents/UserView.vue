<template>
  <div>
    <UserForm @user-created="refreshUsers" />
    <UserList @edit-user="startEdit" ref="userList" />
  </div>
</template>

<script>
import UserForm from "./UserComponents/UserForm.vue";
import UserList from "./UserComponents/UserList.vue";

export default {
  components: { UserForm, UserList },
  methods: {
    refreshUsers() {
      this.$refs.userList.fetchUsers();
    },
    startEdit(user) {
      // handle edit in future, e.g., open a modal
      alert(`Edit user ${user.username} not implemented yet`);
    },
  },
};
</script>
